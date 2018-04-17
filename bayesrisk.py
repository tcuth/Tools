#!/usr/bin/env python

# Bayesian risk table calculation for categorical variables

import csv
import sys
import json
from argparse import ArgumentParser
from collections import defaultdict
from parseFields import parseFields

TARGET_TRUE = '1'
TOTAL = 'total'
PROPORTION = 'proportion'
BAYES_PROPORTION = 'bayes_proportion'
PRIOR = 'prior'

parser = ArgumentParser(description = 'A tool that generates a Bayesian risk table',usage = 'cat file | bayesrisk.py > risktable.json')

parser.add_argument('-a','--A', default=1.0, help='Prior number of bads (target) [default: 1.0]')
parser.add_argument('-b','--B', default=2.0, help='Prior number of goods (non-target) [default: 2.0]')
parser.add_argument('-d','--delimiter', default='|', help='input file delimter [default: "|"]')
parser.add_argument('-s','--scores', default=1, help='Score fields [default: 1]')
parser.add_argument('-t','--target', default=2, help='Target field [default: 2]')
parser.add_argument('-w','--weight', default=None, help='Weight field [default: None]')


args = parser.parse_args()

reader = csv.DictReader(sys.stdin, delimiter = args.delimiter)
header = reader.fieldnames

A = float(args.A)
B = float(args.B)
TAG = int(args.target) - 1
WEIGHT = int(args.weight) - 1 if args.weight is not None else None

risk = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

risk[PRIOR]['A'] = A
risk[PRIOR]['B'] = B
tag = header[TAG]
weight = header[WEIGHT] if WEIGHT is not None else None

for line in reader:
	W = float(line[weight]) if weight is not None else 1
	for current_var_index in parseFields(args.scores):
		current_var = header[current_var_index]
		risk[current_var][line[current_var]][line[tag]] += W
		risk[current_var][line[current_var]][TOTAL] += W

for var in risk.keys():
	if var != PRIOR:
		for value in risk[var].keys():
			y = risk[var][value][TARGET_TRUE]
			n = risk[var][value][TOTAL]
			risk[var][value][PROPORTION] = y/n
			prior_estimator = ((A + B) / (n + A + B)) * (A / (A + B))
			data_estimator = (n / (n + A + B)) * (y/n)
			risk[var][value][BAYES_PROPORTION] = prior_estimator + data_estimator

json.dump(risk, sys.stdout)
