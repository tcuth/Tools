#!/usr/bin/python
from optparse import OptionParser


import sys
import csv
import random

SEED=984902
random.seed(SEED)

#parse options
usage= "usage: %prog [options] tagField targetBR"
parser = OptionParser(usage=usage)
parser.add_option("-s", "--seed", dest="seed", help="provide your own random seed")
parser.add_option("-f", "--force", dest="force", help="another field which you want to keep all w/ value >0")
options,args = parser.parse_args()
if options.seed!=None:
	random.seed(options.seed)
if options.force!=None:
	options.force = int(options.force)-1
if len(args)!=2:
	parser.error("wrong number of arguments")
targetRate = float(args[1])
tagField = int(args[0]) - 1

header = sys.stdin.readline().strip()
sys.stdout.write(header+"|weight\n")

badCnt = 0
goodCnt = 0.0
goods = []
for row in sys.stdin:
	strippedRow = row.strip()
	parsed = strippedRow.split("|")
	if options.force and parsed[options.force] != "0":
		sys.stdout.write(strippedRow+"|1\n")
	elif parsed[tagField] == "0":
		goodCnt+=1
		goods.append(strippedRow)
	else:
		badCnt+=1
		sys.stdout.write(strippedRow+"|1\n")


random.shuffle(goods)
numGoods = int((badCnt/targetRate)-badCnt)

goodWeight = max(1,goodCnt/numGoods)
goodWeight = str(goodWeight)
for row in goods[:numGoods]:
	sys.stdout.write(row+"|"+goodWeight+"\n")

	
	

