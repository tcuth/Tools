#!/data/bin/anaconda/bin/python

import sys
import argparse
from argparse import ArgumentParser
from parseFields import parseFields
from numpy import genfromtxt
from fdr import fraud_detection_rate

usage = "cat SCORES_FILE | fdr.weights.py [options] > OUTPUT"
parser = ArgumentParser(usage = usage, formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("--delimiter","-d",default = "|", type = str, \
		help = "Input file delimiter.")
parser.add_argument("--weights","-w",default = 0, type = int,\
		help = "Weights column (if present; 0 if no weights).")
parser.add_argument("--scores","-s", default = "1", type = str, \
		help = "Score fields.")
parser.add_argument("--target", "-t", default = "2", type = int, \
		help = "Target field.")
parser.add_argument("-p","--percentile", default = 95, type = int, \
		help = "Percentile to calculate.")
args = parser.parse_args()

OUTPUT_HEADER = "var,FDR,N"

DELIMITER = args.delimiter
if args.weights:
	WEIGHTS = args.weights - 1
else:
	WEIGHTS = None
SCORES = parseFields(args.scores)
TARGET = args.target - 1
P = int(args.percentile)

for i,line in enumerate(sys.stdin):
	if i == 0:
		fields = []
		header = line.strip().split(DELIMITER)
		for score in SCORES:
			fields.append(header[score])
		continue
	if WEIGHTS is not None:
		data = genfromtxt(sys.stdin, unpack = True, delimiter = DELIMITER, usecols = [TARGET] + SCORES + [WEIGHTS], comments = None)
		y = data[0]
		w = data[-1]
		print OUTPUT_HEADER
		for name,score in zip(fields,data[1:-1]):
			fdr_score,n = fraud_detection_rate(y, score, w, P)
			print name + "," + str(fdr_score) + "," + str(n)
	else:
		data = genfromtxt(sys.stdin, unpack = True, delimiter = DELIMITER, usecols = [TARGET] + SCORES, comments = None)
		y = data[0]
		print OUTPUT_HEADER
		for name,score in zip(fields,data[1:]):
			fdr_score = fraud_detection_rate(y, score, None, P)
			print name + "," + str(fdr_score)



