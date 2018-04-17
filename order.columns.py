#!/usr/bin/env python

"""
Put columns in one dataset in same order as in another dataset.
Only keep columns both have in common.
"""

import sys
import csv
from optparse import OptionParser

usage = "python order.columns.py [options] FILE1 FILE2 > OUTPUT"
parser = OptionParser(usage = usage)
parser.add_option("-d","--delimiter", dest = "DELIMITER", default = "|",\
	help = "Input file delimter [default: %default]")
parser.add_option("-s","--sort", dest = "SORT", default = False,\
	action = "store_true", help = "Sort output columns alphabetically [default: False]")
parser.add_option("-p","--prepend", dest = "PREPEND", default = False,\
	action = "store_true", help = "Prepend filename as first column [default: False]")
options,args = parser.parse_args()

DELIMITER = options.DELIMITER
SORT = options.SORT
FILE1 = args[0]
FILE2 = args[1]
if options.PREPEND:
	PREPEND = ['file']
else:
	PREPEND = []

# increase field size limit
maxInt = sys.maxsize
decrement = True

while decrement:
	# decrease the maxInt value by factor 10 
	# as long as the OverflowError occurs.

	decrement = False
	try:
		csv.field_size_limit(maxInt)
	except OverflowError:
		maxInt = int(maxInt/10)
		decrement = True

# read headers
with open(FILE1,'rb') as f:
	header1 = f.readline().strip().split(DELIMITER)

with open(FILE2,'rb') as f:
	header2 = f.readline().strip().split(DELIMITER)

# select common fields
common = list(set(header1) & set(header2))
if SORT:
	common.sort()
else:
	common = sorted(common,key=header1.index)

# instantiate output writer
writer = csv.writer(sys.stdout, delimiter = DELIMITER)
writer.writerow(PREPEND + common)

# process first file
reader1 = csv.reader(open(FILE1, 'rb'), delimiter = DELIMITER)
if PREPEND:
	filename = [FILE1]
else:
	filename = []
for i,line in enumerate(reader1):
	if i == 0:
		continue
	output = filename + [line[header1.index(x)] for x in common]
	writer.writerow(output)

# process second file
reader2 = csv.reader(open(FILE2, 'rb'), delimiter = DELIMITER)
if PREPEND:
	filename = [FILE2]
else:
	filename = []
for i,line in enumerate(reader2):
	if i == 0:
		continue
	output = filename + [line[header2.index(x)] for x in common]
	writer.writerow(output)

