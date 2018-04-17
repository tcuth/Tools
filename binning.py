import json
import math
import operator

class Binning:

	def getBin(self,val):
		for bin in self.bins:
			isIn = bin.get(val)
			if isIn:
				return isIn
		raise Exception(str(val)+" :does not fit in any bin")
		#throw exception if not found

	def __init__(self, bins):
		self.bins = bins

	def toJSON(self):
		res = {}
		for bin in self.bins:
			res[bin.name] = bin.value
		return res
#		return json.dumps(res,sort_keys="True",indent=4, separators=(',',':'))

	def __str__(self):
		return self.toJSON()


class CategoricalBin:

	def isIn(self,thisVal):
		return thisVal in self.cats

	def get(self,thisVal):
		if self.isIn(thisVal):
			return self
		else:
			return False

	def __init__(self,cat,vals):
		self.value = list(vals)
		self.cats = vals
		self.name = cat


class IntervalBin:

	def isIn(self,val):
		res = False
		if val == self.min and self.minIncluded:
			res = True
		if val == self.max and self.maxIncluded:
			res = True
		if val>self.min and val<self.max:
			res = True
		return res

	def get(self,val):
		if self.isIn(val):
			return self
		else:
			return False

	def __init__(self,min,max,minIncluded=False,maxIncluded=True):
		self.min = min
		self.max = max
		self.minIncluded = minIncluded
		self.maxIncluded = maxIncluded
		name = ""
		if minIncluded:
			name+="[ "
		else:
			name+="( "
		name+=str(min)+" , "+str(max)
		if maxIncluded:
			name+=" ]"
		else:
			name+=" )"
		self.value = min
		self.name = name

	def __str__(self):
		return self.range


def interval_bins_from_json(bins):
	binning = []
	sorted_bins = sorted(bins.items(), key=operator.itemgetter(1))
	for name,val in sorted_bins:
		minInc = name[0]=="["
		maxInc = name[-1]=="]"
		min,max = name[1:-1].split(",")
		binning.append(IntervalBin(float(min),float(max),minIncluded=minInc,maxIncluded=maxInc))
	return Binning(binning)


def makeUniqueBinning(vals):
	uniqVals = set(vals)
	bins = []
	for val in sorted(uniqVals):
		bins.append(CategoricalBin(val, set([val])))
	return Binning(bins)


def makeEqualBinning(vals,numBins):
	return equal_weighted_bins([(val,1) for val in vals],numBins)


#vals is a tuple of (val,weight)
def equal_weighted_bins(vals,numBins):
	sortedVals = sorted(vals)
	n = sum(n for _,n in vals)
	minCnt = round(n/float(numBins))
	bins = []
	cnt = 0
	lastVal = float('-inf')
	for val,weight in sortedVals:
		if val!=lastVal:
			if cnt>=minCnt:
				cnt=0
				bins.append(val)
				lastVal  = val
			cnt+=weight
	intervals = [IntervalBin(float("-inf"),bins[0],minIncluded=True,maxIncluded=False)]
	for i in range(len(bins)-1):
		intervals.append(IntervalBin(bins[i],bins[i+1],minIncluded=True,maxIncluded=False))
	intervals.append(IntervalBin(bins[-1],float("inf"),minIncluded=True,maxIncluded=True))
	return Binning(intervals)
