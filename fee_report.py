import time

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

        print("-----------------------------------------------------------------------")
        print("------|\trouting fees collected\t|\trebalance fees paid\t|\tsum\t|------")
        print("day---|\t%d\t|\t%d\t|\t%d\t|------" % (
            report["day_fee_sum"],
            report["day_fee_reb"] // 1000,
            report["day_fee_sum"] - report["day_fee_reb"] // 1000))
        print("week--|\t%d\t|\t%d\t|\t%d\t|------" % (
            report["week_fee_sum"],
            report["week_fee_reb"] // 1000,
            report["week_fee_sum"] - report["week_fee_reb"] // 1000))
        print("month-|\t%d\t|\t%d\t|\t%d\t|------" % (
        report["month_fee_sum"],
        report["month_fee_reb"] // 1000,
        report["month_fee_sum"] - report["month_fee_reb"] // 1000))
        print("-----------------------------------------------------------------------")

        return True

    def get_invoice_hashes(self, now):
        hashes = []

        one_month_old_cnt = 0

        first_index_offset = 100
        while one_month_old_cnt < 10:
            list_invoices_response = self.lnd.list_invoices(first_index_offset - 100)
            first_index_offset = list_invoices_response.first_index_offset

            for invoice in list_invoices_response.invoices[::-1]:
                if invoice.settled and invoice.settle_date < now - MONTH:
                    one_month_old_cnt += 1
                if invoice.settled and "Rebalance" in invoice.memo and invoice.settle_date > now - MONTH:
                    hashes.append(invoice.r_hash.hex())

        return hashes
