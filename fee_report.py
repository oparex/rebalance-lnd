

class FeeReport:
    def __init__(self, lnd):
        self.lnd = lnd

    def generate(self):
        # feereport = self.lnd.get_feereport()
        # invoices = self.lnd.list_invoices(0)
        payments = self.lnd.list_payments(0)
        print(payments)
        return True