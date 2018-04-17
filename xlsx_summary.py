#!/usr/bin/env python

import csv
import sys
from openpyxl import Workbook
from argparse import ArgumentParser
from argparse import FileType
from histogram import histogram

# global constants
csv_quoting = {
	'all':csv.QUOTE_ALL,
	'minimal':csv.QUOTE_MINIMAL,
	'nonnumeric':csv.QUOTE_NONNUMERIC,
	'none':csv.QUOTE_NONE
}

LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def XLCell(row_num, col_num):
	res = []
	while col_num:
		col_num, rem = divmod(col_num - 1, 26)
		res[:0] = LETTERS[rem]
	return ''.join(res) + str(row_num)


if __name__ == "__main__":

	parser = ArgumentParser(description = 'A tool that generates a Microsoft Excel file containing column-wise summaries of a set of files')

	parser.add_argument('infiles', nargs='+', type=FileType('r'))
	parser.add_argument('outfile', type=str)
	parser.add_argument('-d', '--delim', type=str, default='|', help='input file delimter [default: "|"]')
	parser.add_argument('-s', '--skip', type=bool, default=True, help='skip header line [default: True]')
	parser.add_argument('-q', '--quoting', type=str, default='none', choices=['all','minimal','nonnumeric','none'], help='quoting in input files')
	parser.add_argument('-n', '--lines', type=int, default=50, help='number of entries from histogram')

	args = parser.parse_args()
	if args.outfile.split('.')[-1] != 'xlsx':
		args.outfile = args.outfile+'.xlsx'

	wb = Workbook()

	summary = wb.active
	summary.title = 'Summary'
	summary[XLCell(1,1)] = 'File'
	summary[XLCell(1,2)] = 'Num Records'

	for i, f in enumerate(args.infiles):
		# gather header and initialize data dictionary
		if args.skip:
			reader = csv.DictReader(f, delimiter=args.delim, quoting=csv_quoting[args.quoting])
			header = reader.fieldnames
			n_col = len(header)
			data = {key: [] for key in header}
		else:
			reader = csv.reader(f, delimter=args.delim, quoting=csv_quoting[args.quoting])
			n_col = len(reader.next())
			f.seek(0)
			header = range(0,n_col)
			data = {key: [] for key in header}

		# collect data
		n_row = 0
		for line in reader:
			for col, value in line.iteritems():
				data[col].extend([value])
			n_row += 1

		# create new sheet for each file & add to summary
		sheet = wb.create_sheet(title=f.name[:31])
		summary[XLCell(i + 2,1)] = f.name
		summary[XLCell(i + 2,2)] = n_row

		sheet[XLCell(1,1)] = 'NROW'
		sheet[XLCell(1,2)] = n_row
		sheet[XLCell(2,1)] = 'NCOL'
		sheet[XLCell(2,2)] = n_col

		# summarize data in original order of columns
		for j, col in enumerate(header):
			histo = [(key,cnt) for key,cnt,_,_ in histogram(data[col], lambda x: x, False, True)]
			histo_dict = dict(histo)
			sheet[XLCell(4,j*3 + 1)] = col
			sheet[XLCell(5,j*3 + 1)] = 'UNIQUES'
			sheet[XLCell(5,j*3 + 2)] = len(histo)
			sheet[XLCell(6,j*3 + 1)] = 'EMPTY STRING'
			sheet[XLCell(6,j*3 + 2)] = histo_dict.get('',0)
			sheet[XLCell(7,j*3 + 1)] = 'NULLS'
			sheet[XLCell(7,j*3 + 2)] = histo_dict.get('NULL', 0)
			for n, entry in enumerate(histo):
				if n < args.lines:
					sheet[XLCell(9 + n,j*3 + 1)] = entry[0]
					sheet[XLCell(9 + n,j*3 + 2)] = entry[1]

	wb.save(args.outfile)
