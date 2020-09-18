import datetime
import sys

from routes import Routes

DEFAULT_BASE_FEE_SAT_MSAT = 1000
DEFAULT_FEE_RATE_MSAT = 0.001


def debug(message):
    # sys.stderr.write(message + "\n")
    # using print to capture output in bash. would also work with stdout
    print(message)

def debugnobreak(message):
    sys.stderr.write(message)


class Logic:
    def __init__(self,
                 lnd,
                 first_hop_channel_id,
                 last_hop_channel_id,
                 from_ratio,
                 to_ratio,
                 amount,
                 max_amount_halvings,
                 max_fee_factor,
                 max_routes_to_request):
        self.lnd = lnd
        self.first_hop_channel_id = first_hop_channel_id
        self.last_hop_channel_id = last_hop_channel_id
        self.first_hop_channel = None
        self.last_hop_channel = None
        self.from_ratio = from_ratio / 100
        self.to_ratio = to_ratio / 100
        self.amount = amount
        self.excluded = []
        self.max_fee_factor = max_fee_factor
        self.max_routes_to_request = max_routes_to_request
        self.max_amount_halvings = max_amount_halvings
        self.num_amount_halvings = 0

    def rebalance(self):
        self.update_channels()
        if self.channels_balanced():
            debug("Done with rabalancing %d and %d"
                  % (self.first_hop_channel_id, self.last_hop_channel_id))
            return True
        if self.amount_too_big():
            debug("Amount %d is too big for current local and/or remote balance of first and/or last hop channel."
                  % self.amount)
            if self.num_amount_halvings < self.max_amount_halvings:
                # if number of halvings is lower then max allowed halvings, halve the amount and try another recursion
                self.amount //= 2
                self.num_amount_halvings += 1
                return self.rebalance()
            return False

        debug(("Sending {:,} satoshis to rebalance to channel with ID %d from channel with ID %d"
               % (self.last_hop_channel.chan_id, self.first_hop_channel.chan_id)).format(self.amount))

        payment_request = self.generate_invoice()
        routes = Routes(self.lnd,
                        payment_request,
                        self.first_hop_channel,
                        self.last_hop_channel,
                        self.max_routes_to_request)

        tried_routes = []
        while routes.has_next():
            debug("trying new route")
            route = routes.get_next()
            success = self.try_route(payment_request, route, routes, tried_routes)
            if success:
                debug("one rebalance successful")
                self.update_channels()
                if self.channels_balanced():
                    debug("Done with rabalancing %d and %d"
                          % (self.first_hop_channel.chan_id, self.last_hop_channel.chan_id))
                    return True
                if self.amount_too_big():
                    debug(
                        "Amount %d is too big for current local and/or remote balance of first and/or last hop channel."
                        % self.amount)
                    if self.num_amount_halvings < self.max_amount_halvings:
                        self.amount //= 2
                        self.num_amount_halvings += 1
                        return self.rebalance()
                routes.payment_request = self.generate_invoice()
                debug("continuing with rebalance")
        debug("All routes exhausted")
        if self.num_amount_halvings < self.max_amount_halvings:
            self.amount //= 2
            self.num_amount_halvings += 1
            return self.rebalance()
        return False

    def try_route(self, payment_request, route, routes, tried_routes):
        if self.route_is_invalid(route, routes):
            debug("Invalid route: %s" % (Routes.print_route(route)))
            return False

        debug("trying route %s" % Routes.print_route(route))

        tried_routes.append(route)

        response = self.lnd.send_payment(payment_request, route)
        is_successful = response.failure.code == 0
        if is_successful:
            debug("Success in route #%d! Paid fees: %s sat (%s msat) %s" %
                  (len(tried_routes), route.total_fees,
                   route.total_fees_msat,
                   datetime.datetime.now().strftime("%Y-%m%d %H:%M:%S")))
            debug("Successful route: %s" % (Routes.print_route(route)))
            return True
        else:
            self.handle_error(response, route, routes)
            return False

    def update_channels(self):
        for channel in self.lnd.get_channels():
            if channel.chan_id == self.first_hop_channel_id:
                self.first_hop_channel = channel
            if channel.chan_id == self.last_hop_channel_id:
                self.last_hop_channel = channel

    def channels_balanced(self):
        local_balance = self.last_hop_channel.local_balance
        remote_balance = self.last_hop_channel.remote_balance
        if local_balance / (local_balance + remote_balance) > self.to_ratio:
            return True

        local_balance = self.first_hop_channel.local_balance
        remote_balance = self.first_hop_channel.remote_balance
        if local_balance / (local_balance + remote_balance) < self.from_ratio:
            return True

        return False

    def amount_too_big(self):
        if self.first_hop_channel.local_balance - self.amount < 0 or self.last_hop_channel.remote_balance < 0:
            return True
        return False

    @staticmethod
    def handle_error(response, route, routes):
        code = response.failure.code
        failure_source_pubkey = Logic.get_failure_source_pubkey(response, route)
        if code == 15:
            debugnobreak("Temporary channel failure, ")
            routes.ignore_edge_on_route(failure_source_pubkey, route)
        elif code == 18:
            debugnobreak("Unknown next peer, ")
            routes.ignore_edge_on_route(failure_source_pubkey, route)
        elif code == 12:
            debugnobreak("Fee insufficient, ")
            routes.ignore_edge_on_route(failure_source_pubkey, route)
        else:
            debug(repr(response))
            debug("Unknown error code %s" % repr(code))

    @staticmethod
    def get_failure_source_pubkey(response, route):
        if response.failure.failure_source_index == 0:
            failure_source_pubkey = route.hops[-1].pub_key
        else:
            failure_source_pubkey = route.hops[response.failure.failure_source_index - 1].pub_key
        return failure_source_pubkey

    def route_is_invalid(self, route, routes):
        if self.fees_too_high(route):
            routes.ignore_node_with_highest_fee(route)
            return True
        return False

    def fees_too_high(self, route):
        # hops_with_fees = len(route.hops) - 1
        # lnd_fees = hops_with_fees * (DEFAULT_BASE_FEE_SAT_MSAT + (self.amount * DEFAULT_FEE_RATE_MSAT))
        # limit = self.max_fee_factor * lnd_fees
        limit = self.max_fee_factor * 1000
        return route.total_fees_msat > limit

    def generate_invoice(self):
        if self.last_hop_channel:
            memo = "Rebalance of channel with ID %d" % self.last_hop_channel.chan_id
        else:
            memo = "Rebalance of channel with ID %d" % self.first_hop_channel.chan_id
        return self.lnd.generate_invoice(memo, self.amount)

    def get_channel_for_channel_id(self, channel_id):
        for channel in self.lnd.get_channels():
            if channel.chan_id == channel_id:
                return channel
