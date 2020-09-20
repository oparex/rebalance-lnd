import time
# from terminaltables import AsciiTable

DAY = 60*60*24
WEEK = DAY*7
MONTH = DAY*30

class FeeReport:
    def __init__(self, lnd):
        self.lnd = lnd

    def generate(self):
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

        for payment in list_payments_response.payments:
            if payment.payment_hash in rebalance_invoice_hashes:
                if payment.creation_date > now - DAY:
                    report["day_fee_reb"] += payment.fee_msat
                if payment.creation_date > now - WEEK:
                    report["week_fee_reb"] += payment.fee_msat
                if payment.creation_date > now - MONTH:
                    report["month_fee_reb"] += payment.fee_msat

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
