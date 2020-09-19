

class FeeReport:
    def __init__(self, lnd):
        self.lnd = lnd

    def generate(self):
        report = {}
        rebalance_invoice_payment_hashs = []

        feereport = self.lnd.get_feereport()
        report["day_fee_sum"] = feereport.day_fee_sum
        report["week_fee_sum"] = feereport.week_fee_sum
        report["month_fee_sum"] = feereport.month_fee_sum

        print(report)

        invoices = self.lnd.list_invoices(0)

        for invoice in invoices:
            if invoice.settled and "Rebalance" in invoice.memo:
                rebalance_invoice_payment_hashs.append(invoice.payment_hash)

        print(rebalance_invoice_payment_hashs)

        return True