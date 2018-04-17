#!/usr/bin/env python

import csv
import sys
from argparse import ArgumentParser
from argparse import FileType
from datetime import datetime
import re

# global constants
csv_quoting = {
	'all':csv.QUOTE_ALL,
	'minimal':csv.QUOTE_MINIMAL,
	'nonnumeric':csv.QUOTE_NONNUMERIC,
	'none':csv.QUOTE_NONE
}

def date_conv(date_string, from_fmt, to_fmt):
	from_date = datetime.strptime(date_string, from_fmt)
	to_date = from_date.strftime(to_fmt)
	return to_date


def range_to_csv(field_str):
	fields = field_str.split(',')
	for i, field in enumerate(fields):
		if re.search('\d:\d', field):
			n = field.split(':')
			r = range(int(n[0]),int(n[1]) + 1)
			s = map(str,r)
			fields[i] = ','.join(s)
	return ','.join(fields)

def main():

	parser = ArgumentParser(description = "A tool that reformats data")

	parser.add_argument('infile', nargs='?', type=FileType('r'), default=sys.stdin)
	parser.add_argument('outfile', nargs='?', type=FileType('w'), default=sys.stdout)
	parser.add_argument('-s', '--skip', type=bool, default=True, help='skip header line [default: True]')
	parser.add_argument('-F', '--sep', type=str, default='|', help='input/output field separator [default: "|"]')
	parser.add_argument('-q', '--quoting', type=str, default='none', choices=['all','minimal','nonnumeric','none'], help='quoting in input files')
	parser.add_argument('-m', '--missing', nargs='+', help='string representing missing values to ignore in conversions')
	parser.add_argument('-d', '--date', action='append', nargs=3, metavar=('fields','from_date_fmt','to_date_fmt'), help='reformat dates within given field [uses strftime(3) format codes]')
	parser.add_argument('-c', '--convert', action='append', nargs='+', help='convert strings within given field(s) (before any global conversions) [field(s) (from_str, to_str)...]')
	parser.add_argument('-g', '--gc', nargs=2, metavar=('from_str', 'to_str'), help='globaly convert strings')
	parser.add_argument('-r', '--regex', action='append', nargs=4, metavar=('fields','pattern','replacement','max_replace'), help='replace regex matches in field(s) to pattern with replacement string up to max_replace times [max_count==0 replaces all occurences]')

	args = parser.parse_args()

	# create field lists for date conversions
	if args.date is not None:
		date_conv_list = []
		for l in args.date:
			fields = range_to_csv(l[0]).split(',')
			int_fields = map(int,fields)
			int_fields[:] = [i - 1 for i in int_fields]
			date_conv_list.append(int_fields)
	# create lists for string conversions
	if args.convert is not None:
		str_conv_list = []
		froms = []
		tos = []
		for l in args.convert:
			fields = range_to_csv(l[0]).split(',')
			int_fields = map(int,fields)
			int_fields[:] = [i - 1 for i in int_fields]
			str_conv_list.append(int_fields)
			if len(l) == 1:
				sys.exit('usage: cleanser.py [options]\ncleanser.py: error: argument -c/--convert: expected field(s) and tuples, received 1 argument')
			elif len(l) % 2 == 0:
				sys.exit('usage: cleanser.py [options]\ncleanser.py: error: argument -c/--convert: expected field(s) and tuples, received even number of arguments')
			else:
				conversions = l[1:]
				#same result as 'conversion_pairs = zip(conversions[::2], conversions[1::2])'
				conversion_pairs = zip(*[iter(conversions)]*2)
				froms.append([x[0] for x in conversion_pairs])
				tos.append([x[1] for x in conversion_pairs])
	# create field lists for regex conversions
	if args.regex is not None:
		re_conv_list = []
		for l in args.regex:
			fields = range_to_csv(l[0]).split(',')
			int_fields = map(int,fields)
			int_fields[:] = [i - 1 for i in int_fields]
			re_conv_list.append(int_fields)


	reader = csv.reader(args.infile, delimiter=args.sep, quoting=csv_quoting[args.quoting])
	writer = csv.writer(args.outfile, delimiter=args.sep, quoting=csv_quoting[args.quoting])

	if args.skip:
		head = reader.next()
		writer.writerow(head)

	for row in reader:
		# string conversions
		if args.convert is not None:
			for i, fields in enumerate(str_conv_list):
				for j, field in enumerate(fields):
					for k, from_str in enumerate(froms[i]):
						if row[field] == from_str:
							row[field] = tos[i][k]
		# global conversions
		if args.gc is not None:
			for index, field in enumerate(row):
				if field == args.gc[0]:
					row[index] = args.gc[1]
		# date conversions
		if args.date is not None:
			for i, fields in enumerate(date_conv_list):
				for index, field in enumerate(fields):
					if args.missing is not None:
						if row[field] not in args.missing:
							row[field] = date_conv(row[field],args.date[i][1],args.date[i][2])
					else:
						row[field] = date_conv(row[field],args.date[i][1],args.date[i][2])
		# regex conversions
		if args.regex is not None:
			for i, fields in enumerate(re_conv_list):
				for index, field in enumerate(fields):
					if args.missing is not None:
						if row[field] not in args.missing:
							row[field] = re.sub(args.regex[i][1], args.regex[i][2], row[field], int(args.regex[i][3]))
					else:
							row[field] = re.sub(args.regex[i][1], args.regex[i][2], row[field], int(args.regex[i][3]))

		writer.writerow(row)


if __name__ == '__main__':
	main()
