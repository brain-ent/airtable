import os
import csv
from tkinter import filedialog, Tk

# dialog window
root = Tk()
root.withdraw()
# get path to the airtable
airtable_csv = filedialog.askopenfilename()
# or by manual
# airtable_csv = "/path/to/the/file"

result = os.path.join(os.path.dirname(airtable_csv), 'code_class.csv')
with open(airtable_csv, 'r') as airtable, open(result, 'w') as result:
	writer = csv.writer(result, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
	reader = csv.reader(airtable, delimiter=',')
	next(reader)    # remove header
	for row in reader:
		classname, gencodes, dataset = row[1], row[8], row[6]
		gencodes = gencodes.split(',')
		if classname and gencodes:
			for gencode in gencodes:
				writer.writerow([gencode, classname, dataset])

