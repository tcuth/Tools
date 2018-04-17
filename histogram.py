#!/usr/bin/python
import sys
import operator
from optparse import OptionParser

def makeBinningFunc(binSize):
	def binning(val):
		try: 
			return int(val/binSize)*binSize
		except Exception:
			return val
	return binning

def makeListBins(bins):
	#just in case
	bins.sort()
	def binning(val):
		try:
			val = float(val)
		except Exception:
			res =  val
		found=False
		for bin in bins:
			if  val < bin:
				res = bin
				found=True
				break
		if not found:
			res = ">"+str(bin)
		return res
	return binning
			
	


def histogram(inFH,binningFunc,isNumeric,freq):
	histo = {}
	n= 0.0
	for line in inFH:
		val = line.strip()
		if isNumeric:
			try:
				val = int(val)
			except Exception:
				val = val
		val = binningFunc(val)
		histo[val] = histo.get(val,0)+1
		n+=1

	if freq:
		sItems = sorted(histo.items(),key=operator.itemgetter(1),reverse=True)
	else:
		sItems = sorted(histo.items())
	cumPerc=0
	res = []
	for key,val in sItems:
		cnt = histo[key]
		perc = cnt/n
		cumPerc+=perc
		res.append((key,cnt,perc,cumPerc))
	return res

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-b", "--bins", dest="bins",
		help="size of bins")
	parser.add_option("-l", "--list", dest="list",
		help="comma seperated list of numeric bins, takes precedence over -b")
	parser.add_option("-n", "--numeric",
		action="store_true", dest="numeric", default=False,
		help="values are numeric")
	parser.add_option("-f", "--freq",
		action="store_true", dest="freq", default=False,
		help="values are numeric")
	(options, args) = parser.parse_args()
	binningFunc = lambda x: x
	if options.bins!=None:
		binningFunc=makeBinningFunc(int(options.bins))
		options.numeric = True
	if options.list!=None:
		binningFunc=makeListBins([float(x) for x in options.list.split(",")])
		options.numeric = True
	res = histogram(sys.stdin,binningFunc,options.numeric,options.freq)
	for row in res:
		print ",".join([str(x) for x in row])
