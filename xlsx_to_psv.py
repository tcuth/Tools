#!/usr/bin/env python

import pandas as pd
import sys
from optparse import OptionParser

usage = "Usage: python xlsx_to_psv.py [options] FILE > OUTPUT"
parser = OptionParser(usage = usage)
parser.add_option("-s", "--sheetname", dest = "SHEET", default = "Sheet1",
				help = "Sheet name to parse [default: %default]")
options, args = parser.parse_args()

FILE = args[0]
data = pd.read_excel(FILE, sheetname = options.SHEET)
data.to_csv(sys.stdout, sep = "|", index = False, encoding = 'utf-8')
