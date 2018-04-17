#!/data/bin/anaconda/bin/python

"""
Put columns in one dataset in same order as in another dataset.
Only keep columns both have in common.
"""

import sys
import csv
from parseFields import parseFields
from optparse import OptionParser

usage = "cat STDIN | python join.cols.py [options] FORMATFILE > OUTPUT"
desc = "Subset columns from STDIN to columns in FORMATFILE"
parser = OptionParser(usage = usage, description = desc)
parser.add_option("-d","--delimiter", dest = "DELIMITER", default = "|",\
	help = "Input file delimter [default: %default]")
parser.add_option("-s","--sort", dest = "SORT", default = False,\
	action = "store_true", help = "Sort output columns alphabetically [default: False]")
parser.add_option("-k","--keep", dest = "KEEP", default = None,
		help = "Index of columns to keep in FILE2 [default: %default]")
options,args = parser.parse_args()

DELIMITER = options.DELIMITER
SORT = options.SORT
FORMATFILE = args[0]
INFILE = sys.stdin

# read header in format file
with open(FORMATFILE,'rb') as f:
	header1 = f.readline().strip().split(DELIMITER)

# process second file
#stdinput = sys.stdin.readline()
reader = csv.reader(iter(sys.stdin.readline,''), delimiter = DELIMITER)

for i,line in enumerate(reader):
	if i == 0:
		header2 = line
		# select common fields
		common = list(set(header1) & set(header2))
		if SORT:
			common.sort()
		# select fields to keep
		if options.KEEP:
			KEEP = [header2[k] for k in parseFields(options.KEEP)]
		else:
			KEEP = []
		common = [c for c in common if c not in KEEP]
		to_write = KEEP + common
		index = [header2.index(x) for x in to_write]
	output = [line[ind] for ind in index]
	try:
		sys.stdout.write(DELIMITER.join(output)+"\n")
	except IOError:
		try:
			sys.stdout.close()
		except IOError:
			pass
		try:
			sys.stderr.close()
		except IOError:
			pass

sys.stdin.close()
