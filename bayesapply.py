#!/usr/bin/env python

# Baysiean risk table application for categorical variables

import csv
import sys
import json
from collections import defaultdict
from parseFields import parseFields
from argparse import ArgumentParser
import json

usage = "cat file | bayesapply.py [options] risktable.json > output"
parser = ArgumentParser(usage=usage)
parser.add_argument("risktable", help="json risktable file")
parser.add_argument("-d", "--delimiter", default = "|", type=str,\
		help = 'Input file delimiter [default: "|"]')
parser.add_argument("-k", "--keep", default = None, type=str, \
		help = "Index of additional input file fields to keep [default: None]")
parser.add_argument("-x","--default", default = 0.25, type=float, \
		help = "Default value for missing keys [default: 0.25]")
parser.add_argument("-m", "--missing", default = [], \
	help = "Comma separated list of values to replace with DEFAULT value [default: []]")
args = parser.parse_args()

DEFAULT = float(args.default)
if args.missing or args.missing == "":
	MISSING = [str(x) for x in args.missing.split(",")]
else:
	MISSING = args.missing
# Load risk Table
TABLE = json.load(open(args.risktable))

# Load dataset
reader = csv.DictReader(sys.stdin, delimiter = args.delimiter)

# apply risk tables
for i,line in enumerate(reader):
	if i == 0:
		header = reader.fieldnames

		KEEP = []
		if args.keep:
			keep_idx = parseFields(args.keep)
			KEEP = [j for i,j in enumerate(header) if i in keep_idx]

		TABLE_KEYS = [k for k in TABLE.keys() if k != "prior"]
		TABLE_KEYS_PROPORTION = [k + "_proportion" for k in TABLE_KEYS]
		TABLE_KEYS_BAYES = [k + "_bayes_proportion" for k in TABLE_KEYS]
		output_header = KEEP + TABLE_KEYS_PROPORTION + TABLE_KEYS_BAYES

		writer = csv.DictWriter(sys.stdout, delimiter = args.delimiter, fieldnames = output_header)
		writer.writeheader()

	output = {}
	if KEEP:
		for var in KEEP:
			output[var] = line[var]
	
	for var in TABLE_KEYS:
		if str(line[var]) in MISSING:
			output[var + "_proportion"] = DEFAULT
			output[var + "_bayes_proportion"] = DEFAULT
		else:
			try:
				output[var + "_proportion"] = TABLE[var][line[var]]['proportion']
				output[var + "_bayes_proportion"] = TABLE[var][line[var]]['bayes_proportion']
			except KeyError:
				output[var + "_proportion"] = DEFAULT
				output[var + "_bayes_proportion"] = DEFAULT

	writer.writerow(output)

