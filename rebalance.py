#!/usr/bin/env python

import argparse
import sys

from lnd import Lnd
from logic import Logic
from fee_report import FeeReport

MAX_SATOSHIS_PER_TRANSACTION = 4294967


def main():
    argument_parser = get_argument_parser()
    arguments = argument_parser.parse_args()
    lnd = Lnd(arguments.lnddir, arguments.grpc, arguments.max_fee_factor)

    if arguments.fee_report:
        # return FeeReport(lnd).generate()
        return FeeReport(lnd).get_mintgox_profit()

    from_channel = vars(arguments)['from']
    to_channel = arguments.to
    from_ratio = arguments.from_ratio / 100
    to_ratio = arguments.to_ratio / 100
    max_amount_halvings = arguments.max_amount_halvings
    amount = min(int(arguments.amount), MAX_SATOSHIS_PER_TRANSACTION)

    if from_ratio < 0 or from_ratio > 100:
        print("--from_ratio must be between 0 and 100")
        sys.exit(1)

    if to_ratio < 0 or to_ratio > 100:
        print("--to_ratio must be between 0 and 100")
        sys.exit(1)

    if arguments.amount is None:
        print("--amount argument is required")
        sys.exit(1)

    if to_channel is None or from_channel is None:
        argument_parser.print_help()
        sys.exit(1)

    max_fee_factor = arguments.max_fee_factor
    max_routes_to_request = arguments.max_routes_to_request

    return Logic(lnd, from_channel, to_channel, from_ratio, to_ratio, amount, max_amount_halvings,
                 max_fee_factor, max_routes_to_request, 0).rebalance()


def get_channel_for_channel_id(lnd, channel_id):
    for channel in lnd.get_channels():
        if channel.chan_id == channel_id:
            return channel
    return None


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lnddir",
                        default="~/.lnd",
                        dest="lnddir",
                        help="(default ~/.lnd) lnd directory")
    parser.add_argument("--grpc",
                        default="localhost:10009",
                        dest="grpc",
                        help="(default localhost:10009) lnd gRPC endpoint")
    parser.add_argument("--fee-report",
                        action='store_true',
                        help="(default false) toggle to print fee report")
    rebalance_group = parser.add_argument_group("rebalance",
                                                "Rebalance a channel. You need to specify at least"
                                                " the 'from' channel (-f) or the 'to' channel (-t).")
    rebalance_group.add_argument("-f", "--from",
                                 metavar="CHANNEL",
                                 type=int,
                                 help="channel ID of the outgoing channel "
                                      "(funds will be taken from this channel)")
    rebalance_group.add_argument("-t", "--to",
                                 metavar="CHANNEL",
                                 type=int,
                                 help="channel ID of the incoming channel "
                                      "(funds will be sent to this channel). "
                                      "You may also use the index as shown in the incoming candidate list (-l -i).")
    amount_group = rebalance_group.add_mutually_exclusive_group()
    amount_group.add_argument("-a", "--amount",
                              type=int,
                              default=800000,
                              help="Amount to start the rebalance, in satoshis.")
    rebalance_group.add_argument("-l", "--max_amount_halvings",
                              type=int,
                              default=0,
                              help="Number of amount halvings in the rebalance process.")
    rebalance_group.add_argument("-fr", "--from_ratio",
                                 type=int,
                                 default=50,
                                 help="(default: 50) ratio for first hop channel balance between 0 and 100, "
                                      "eg. 20 means that rebalance will not be performed if less then"
                                      "20 percent of balance is on local side in to_channel")
    rebalance_group.add_argument("-tr", "--to_ratio",
                                 type=int,
                                 default=50,
                                 help="(default: 50) ratio for last hop channel balance between 0 and 100, "
                                      "eg. 20 means that rebalance will not be performed if more then"
                                      "20 percent of balance is on local side in to_channel")
    rebalance_group.add_argument("--max-fee-factor",
                                 type=int,
                                 default=10,
                                 help="(default: 10) Reject routes that cost more than x times the lnd default "
                                      "(base: 1 sat, rate: 1 millionth sat) per hop on average")
    rebalance_group.add_argument("-n", "--max-routes_to_request",
                                 type=int,
                                 default=10,
                                 help="(default: 30) Number of routes to request from lnd")
    return parser

success = main()
if success:
    sys.exit(0)
sys.exit(1)
