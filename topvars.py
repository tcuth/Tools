#!/usr/bin/env python

# select top n vars from uniks output

from optparse import OptionParser
import csv
import sys
from parseFields import parseFields
from combineFields import combineFields

usage = "cat INPUT_PSV | topvars.py KS_FILE > OUTPUT"
parser = OptionParser(usage = usage)
parser.add_option("-d","--delimiter",dest = "DELIMITER", default = "|",\
		help = "Input file delimiter for both KS and DATA file [default: %default]")
parser.add_option("-n","--nvars", default = 100, dest = "NVARS",\
		help = "Number of variables to keep [default: %default]")
parser.add_option("-k","--keep",default = None, dest = "KEEP",\
		help = "Indices of additional variables to keep [default: %default]")
parser.add_option("-i","--indicesOnly", default = False, action = "store_true", dest = "INDICES",\
		help = "Only print indices of variables [default: %default]")
options,args = parser.parse_args()

DELIMITER = str(options.DELIMITER)
# no need to subtrace one from NVARS; accounts for header in KS file
NVARS = int(options.NVARS)
if options.KEEP:
	KEEP = parseFields(options.KEEP)
else:
	KEEP = None
KS_FILE = str(args[0])

# save additional variables in input file
keep = []
with open(KS_FILE) as f:
	for i,line in enumerate(f):
		var = line.strip().split(DELIMITER)[0]
		if i <= NVARS:
			keep.append(var)

if options.INDICES:
	header = sys.stdin.readline().strip().split(DELIMITER)
	indices = [header.index(x) for x in keep if x in header]
	indices.sort()
	print combineFields(indices)
	sys.exit(0)

reader = csv.DictReader(sys.stdin, delimiter = DELIMITER)

for i, line in enumerate(reader):
	if i == 0:
		if KEEP is not None:
			fields = reader.fieldnames
			fields_to_keep = [var[1] for var in enumerate(fields) if var[0] in KEEP]
			keep = fields_to_keep + [var for var in keep if var in fields]
		writer = csv.DictWriter(sys.stdout, delimiter = DELIMITER, fieldnames = keep)
		writer.writeheader()
	output = dict((k,line[k]) for k in keep if k in reader.fieldnames)
	writer.writerow(output)
