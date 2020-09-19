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
        report["day_fee_sum"] = feereport_response.day_fee_sum * 1000
        report["week_fee_sum"] = feereport_response.week_fee_sum * 1000
        report["month_fee_sum"] = feereport_response.month_fee_sum * 1000
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

        print(report)

        return True

    def get_invoice_hashes(self, now):
        hashes = []
        i = 0
        while i < 10:
            list_invoices_response = self.lnd.list_invoices(i * 100)
            i += 1

            for invoice in list_invoices_response.invoices:
                print(invoice.creation_date, invoice.settle_date)
                # if invoice.settled and invoice.settle_date < now - MONTH:
                #     print(i, invoice.settle_date, now)
                #     return hashes
                if invoice.settled and "Rebalance" in invoice.memo and invoice.settle_date > now - MONTH:
                    hashes.append(invoice.r_hash.hex())

        return hashes
