#!/usr/bin/env python

import pandas
import sys
from argparse import ArgumentParser
from cStringIO import StringIO

if __name__ == "__main__":
	parser = ArgumentParser(description = 'A tool to convert fixed width files to delimited files')

	parser.add_argument('-w', '--widths', type=str, help='comma separated list of column widths')
	parser.add_argument('-d', '--delimiter', type=str, default = '|', help = 'output file delimiter [default: "|"]')

	args = parser.parse_args()

	WIDTHS = args.widths.split(',')
	WIDTHS = [int(w) for w in WIDTHS]

	df = pandas.read_fwf(sys.stdin, widths = WIDTHS, converters = {i:str for i in range(len(WIDTHS))})
	df.to_csv(sys.stdout, sep = args.delimiter, index = False)
