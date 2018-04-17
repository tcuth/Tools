#!/data/bin/anaconda/bin/python
"""Remove NULLS from file (usually resulting from a SQL query).
"""



import sys
import csv
from optparse import OptionParser

usage = "cat INPUT_FILE | nonulls.py [options] > OUTPUT"
parser = OptionParser(usage = usage)
parser.add_option("-d","--delimiter", dest = "DELIMITER", default = "\t",\
	help = "Input file delimiter [default: TAB]")
parser.add_option("-o","--output-delimiter", dest = "OUTPUT", default = "|",\
	help = "Output file delimiter [default: %default]")
options,args = parser.parse_args()

DELIMITER = str(options.DELIMITER)
OUTPUT_DELIMITER = str(options.OUTPUT)

reader = csv.DictReader(sys.stdin, delimiter = DELIMITER)

for i,line in enumerate(reader):
	if i == 0:
		header = reader.fieldnames
		writer = csv.DictWriter(sys.stdout, fieldnames = header, delimiter = OUTPUT_DELIMITER)
		writer.writeheader()
	output = dict((k,v) if v.strip() != "NULL" else (k,"") for k,v in line.iteritems())
	writer.writerow(output)
