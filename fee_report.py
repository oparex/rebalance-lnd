

class FeeReport:
    def __init__(self, lnd):
        self.lnd = lnd

    def generate(self):
        print(self.lnd.get_feereport())
        return True