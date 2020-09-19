import json
import os

# stream = os.popen("lncli listinvoices --max_invoices 100")
stream = os.popen("lncli feereport")
result = json.loads(stream.read())

print(result)