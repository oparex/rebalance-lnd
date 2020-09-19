import time

ONE_MONTH = 60*60*24*30

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

        rebalance_invoice_hashes = self.get_invoice_hashes(now)

        list_payments_response = self.lnd.list_payments()

        for payment in list_payments_response.payments:
            if payment.payment_hash in rebalance_invoice_hashes:
                print(payment.fee_msat)

        return True

    def get_invoice_hashes(self, now):
        hashes = []
        i = 0
        while True:
            list_invoices_response = self.lnd.list_invoices(i * 100)
            i += 1

            for invoice in list_invoices_response.invoices[::-1]:
                if invoice.settled and invoice.settle_date < now - ONE_MONTH:
                    print(hashes)
                    return hashes
                if invoice.settled and "Rebalance" in invoice.memo and invoice.settle_date > now - ONE_MONTH:
                    hashes.append(invoice.r_hash.hex())
