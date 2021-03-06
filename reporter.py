import time
# from terminaltables import AsciiTable

DAY = 60*60*24
WEEK = DAY*7
MONTH = DAY*30

class Reporter:
    def __init__(self, lnd):
        self.lnd = lnd

    def feereport(self):
        now = int(time.time())

        report = {}

        feereport_response = self.lnd.get_feereport()
        report["day_fee_sum"] = feereport_response.day_fee_sum
        report["week_fee_sum"] = feereport_response.week_fee_sum
        report["month_fee_sum"] = feereport_response.month_fee_sum
        report["day_fee_reb"] = 0
        report["week_fee_reb"] = 0
        report["month_fee_reb"] = 0

        rebalance_invoice_hashes = self.get_invoice_hashes(now)

        list_payments_response = self.lnd.list_payments()
        # print(len(list_payments_response.payments),
        #       list_payments_response.payments[0],
        #       list_payments_response.payments[-1])

        for payment in list_payments_response.payments:
            if payment.payment_hash in rebalance_invoice_hashes:
                if payment.creation_date > now - DAY:
                    report["day_fee_reb"] += payment.fee_msat
                if payment.creation_date > now - WEEK:
                    report["week_fee_reb"] += payment.fee_msat
                if payment.creation_date > now - MONTH:
                    report["month_fee_reb"] += payment.fee_msat

        # for payment in list_payments_response.payments:
        #     decoded_request = self.lnd.decode_payment_request(payment.payment_request)
        #     print(decoded_request)

            # if "Rebalance" in decoded_request.description:
            #     if payment.creation_date > now - DAY:
            #         report["day_fee_reb"] += payment.fee_msat
            #     if payment.creation_date > now - WEEK:
            #         report["week_fee_reb"] += payment.fee_msat
            #     if payment.creation_date > now - MONTH:
            #         report["month_fee_reb"] += payment.fee_msat

        # table_data = [
        #     ["", "collecter", "paid", "sum"],
        #     ["day", str(report["day_fee_sum"]), str(report["day_fee_reb"] // 1000),
        #      str(report["day_fee_sum"] - report["day_fee_reb"] // 1000)],
        #     ["week", str(report["week_fee_sum"]), str(report["week_fee_reb"] // 1000),
        #      str(report["week_fee_sum"] - report["week_fee_reb"] // 1000)],
        #     ["month", str(report["month_fee_sum"]), str(report["month_fee_reb"] // 1000),
        #      str(report["month_fee_sum"] - report["month_fee_reb"] // 1000)],
        # ]
        #
        # table = AsciiTable(table_data)
        # print(table.table)

        report["day_fee_reb"] //= 1000
        report["week_fee_reb"] //= 1000
        report["month_fee_reb"] //= 1000

        report["day_sum"] = report["day_fee_sum"] - report["day_fee_reb"]
        report["week_sum"] = report["week_fee_sum"] - report["week_fee_reb"]
        report["month_sum"] = report["month_fee_sum"] - report["month_fee_reb"]

        print("------------------------------------")
        i = 0
        for k in report:
            print(k, '\t', report[k])
            i += 1
            if i % 3 == 0:
                print("------------------------------------")

        return True

    # obsolete if decode_payment works
    def get_invoice_hashes(self, now):
        hashes = []

        one_month_old_cnt = 0

        first_index_offset = 0
        while one_month_old_cnt < 2:
            list_invoices_response = self.lnd.list_invoices(first_index_offset)
            first_index_offset = list_invoices_response.first_index_offset

            for invoice in list_invoices_response.invoices[::-1]:
                if invoice.settled and invoice.settle_date < now - MONTH:
                    one_month_old_cnt += 1
                if invoice.settled and "Rebalance" in invoice.memo and invoice.settle_date > now - MONTH:
                    hashes.append(invoice.r_hash.hex())

        return hashes

    def mintgox(self):
        now = int(time.time())
        got_paid = 0
        paid = 0
        first_index_offset = 0

        loop = True

        while loop:
            list_invoices_response = self.lnd.list_invoices(first_index_offset)
            first_index_offset = list_invoices_response.first_index_offset

            for invoice in list_invoices_response.invoices[::-1]:
                if invoice.settled and invoice.settle_date < now - WEEK:
                    loop = False
                if invoice.settled and ("Sats Stacker" in invoice.memo or "Sarutobi" in invoice.memo) \
                        and invoice.settle_date > now - WEEK:
                    got_paid += invoice.amt_paid_sat

        print(got_paid)

        list_payments_response = self.lnd.list_payments()

        for payment in list_payments_response.payments:
            decoded_request = self.lnd.decode_payment_request(payment.payment_request)

            if decoded_request.timestamp > now - WEEK\
                    and ("mintgox" in decoded_request.description or "bananas" in decoded_request.description):
                paid += payment.num_satoshis

        print(paid)
