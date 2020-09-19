import json
import os

stream = os.popen("lncli feereport")
fee_report = json.loads(stream.read())

stream = os.popen("lncli listinvoices --max_invoices 100")
invoices = json.loads(stream.read())

print(invoices[0])
print(invoices[0]["settled"])
print(invoices[0]["settled"] is True)
print(invoices[0]["memo"])
print("Rebalance" in invoices[0]["memo"])