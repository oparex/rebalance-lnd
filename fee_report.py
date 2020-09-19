

class FeeReport:
    def __init__(self, lnd):
        self.lnd = lnd

    def generate(self):
        report = {}
        rebalance_invoice_payment_hashs = []

        feereport_response = self.lnd.get_feereport()
        report["day_fee_sum"] = feereport_response.day_fee_sum
        report["week_fee_sum"] = feereport_response.week_fee_sum
        report["month_fee_sum"] = feereport_response.month_fee_sum

        print(report)

        list_invoices_response = self.lnd.list_invoices(0)

        for invoice in list_invoices_response.invoices:
            if invoice.settled and "Rebalance" in invoice.memo:
                rebalance_invoice_payment_hashs.append(invoice.r_hash.hex())

        list_payments_response = self.lnd.list_payments()

        for payment in list_payments_response.payments:
            print(payment)
            break

        return True