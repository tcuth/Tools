#!/usr/bin/env python

import ujson
import sys
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-d', metavar='DELIM', default='|', help='Output delimiter')
parser.add_argument('keys', nargs='+', default=[], metavar='KEY', help='Keys to output. E.g. request.result.score')

args = vars(parser.parse_args())

keys = [ key.strip().split('.') for key in args['keys'] ]

# print the header
print args['d'].join(args['keys'])

empty_str = args['d'].join([ '' for i in range(0,len(args['keys'])) ])

def get_value(d, keys):
	sub_d = d
	for key in keys:
		sub_d = sub_d[key]
	return sub_d

for line in sys.stdin:
	try:
		d = ujson.loads(line)
		l = []
		for key in keys:
			try:
				l.append(get_value(d, key))
			except KeyError,e:
				l.append('')
		print args['d'].join([ str(v) for v in l ])
	except:
		print empty_str
