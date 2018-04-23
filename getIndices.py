#!/usr/bin/env python

# output index in Linux format of headerFile

from argparse import ArgumentParser
import sys
from parseFields import parseFields
from combineFields import combineFields

usage = "cat INPUT_PSV | topvars.py HEADERFILE > OUTPUT"
parser = ArgumentParser(usage = usage)
parser.add_argument('headerFile')
parser.add_argument("-i","--index",default = 1, type=int,
		help = "index of header column [default: 1]")
parser.add_argument("-d","--delimiter", default = "|", type=str,\
		help = 'Input file delimiter for both INPUT and HEADER file [default: "|"]')
#parser.add_argument("-k","--keep",default = None, type=str,\
#		help = "Indices of additional variables to keep [default: None]")
args = parser.parse_args()

#if args.keep is not None:
#	KEEP = parseFields(args.keep)
#else:
#	KEEP = None
FILE = args.headerFile

# save additional variables in input file
keep = []
with open(FILE) as f:
	for i,line in enumerate(f):
		var = line.strip().split(args.delimiter)[args.index - 1]
		keep.append(var)

header = sys.stdin.readline().strip().split(args.delimiter)
indices = [header.index(x) for x in keep if x in header]
indices.sort()
print combineFields(indices)
sys.exit(0)
