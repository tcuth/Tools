#!/usr/bin/env python

"""Reservoir sampling at the command line."""

import sys
import random
from argparse import ArgumentParser
usage = "cat FILE | reservoir.py [options] > OUTPUT"

parser = ArgumentParser('A reservoir sampling command line utility', usage = usage)
parser.add_argument("-n","--nsamples",default=100,type=int,help="Number of records to output [default: 100]")
parser.add_argument("-s","--seed",default=2813308004,help="Random seed [default: 2813308004]")
parser.add_argument("-k","--hasHeader",action="store_true",default=False,help="File contains header [default: False]")
parser.add_argument("-r","--remaining",default=None,type=str,help="file for remaining data [default: None]")
args = parser.parse_args()


# set random seed for repeatability
random.seed(int(args.seed))

sample = []
if args.remaining is not None:
	remaining = []
	writer = open(args.remaining, 'w')

# keep header
if args.hasHeader:
	header = sys.stdin.readline()
	sys.stdout.write(header)
	if args.remaining:
		writer.write(header)

for i, line in enumerate(sys.stdin):
	if i < args.nsamples:
		sample.append(line)
	elif i >= args.nsamples and random.random() < args.nsamples/float(i+1):
		replace = random.randint(0, len(sample) - 1)
		if args.remaining is not None:
			writer.write(sample[replace])
		sample[replace] = line
	elif args.remaining is not None:
		writer.write(line)

for line in sample:
	sys.stdout.write(line)

