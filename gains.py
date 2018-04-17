#!/usr/bin/env python

import binning
from optparse import OptionParser
import sys
import csv
import json


GAINS_DELIM="|"

def makeGains(vals,weights,target,otherVals,bins,reverse=True):
	header = ["binRange","binCount","cumCount","cumPerc","sumTarget","cumSumTarget","meanTarget","percTotalTarget"]
	sumOthers = {}
	for otherField in otherVals.keys():
		header.append(otherField+"_sum")
		sumOthers[otherField] = {}
	print GAINS_DELIM.join(header)
	binCnts = {}
	sumTarget = {}

	totalCnt = sum(weights)
	totalTarget = 0
	intervals = bins.bins
	#setup bin vals
	for bin in intervals:
		binCnts[bin] = 0.0
		sumTarget[bin] = 0.0
		for otherField in otherVals.keys():
			sumOthers[otherField][bin] = 0.0
	#bin all values
	#need to fix this up for the other vals
	for i,val in enumerate(vals):
		bin = bins.getBin(val)
		weight = weights[i]
		tar = target[i]
		binCnts[bin] += weight
		sumTarget[bin] += tar*weight
		#not done yet
		for otherField,thisOtherVals in otherVals.items():
			sumOthers[otherField][bin] += weight*thisOtherVals[i]
		totalTarget += tar*weight
	if reverse:
		intervals = intervals[::-1]
	cntSoFar = 0.0
	targetSoFar = 0.0
	for bin in intervals:
		thisCnt = binCnts[bin]
		thisTarget = sumTarget[bin]
		cntSoFar+=thisCnt
		targetSoFar+=thisTarget
		#bin range
		res = [bin.name]
		#bin count
		res.append(thisCnt)
		#cum count
		res.append(cntSoFar)
		#cum % so far
		res.append(cntSoFar/totalCnt)
		# sum target
		res.append(thisTarget)
		# cum sum target
		res.append(targetSoFar)
		# mean target
		res.append(thisTarget/thisCnt)
		# cum % total target
		res.append(targetSoFar/totalTarget)
		for otherField in otherVals.keys():
			res.append(sumOthers[otherField][bin])
		print GAINS_DELIM.join([str(x) for x in res])
	

def getFields(reader, target, scores, otherFields,numBins,reverse,weight,storeBins,binFile):
	#setup all the necessary vectors
	targets = []
	weights = []
	scoreVals = dict([(score, []) for score in scores])
	otherVals = dict([(otherField,[]) for otherField in otherFields])
	#fill the vectors with the input file
	for row in reader:
		targets.append(float(row[target]))
		thisWeight = 1
		if weight != None:
			thisWeight = float(row[weight])
		weights.append(thisWeight)
		for score in scores:
			scoreVals[score].append(float(row[score]))
		for field in otherFields:
			otherVals[field].append(float(row[otherField]))
	#write out the gains chart
	allBins = {}
	existingBins = None
	if binFile!=None:
		binFH = open(binFile,'r')
		existingBins = json.load(binFH)
		binFH.close()
	for score in scores:
		print score
		vals = scoreVals[score]
		#read and load existing bins
		if existingBins!=None:
			if existingBins.has_key(score):
				bins = binning.interval_bins_from_json(existingBins[score])
			else:
				sys.exit("%s not found in bin file" % score)
		else:
			
			bins = binning.equal_weighted_bins(zip(vals,weights),numBins)
		makeGains(vals,weights,targets,otherVals,bins,reverse=reverse)
		allBins[score] = bins.toJSON()
		print ""
	if storeBins!=None:
		binOut = open(storeBins,'w')
		binOut.write(json.dumps(allBins,sort_keys="True",indent=4, separators=(',',':')))
		binOut.close()


def parseFields(fieldsStr,fields):
	fieldNums = []
	parsed = fieldsStr.split(",")
	for part in parsed:
		subParsed = part.split("-")
		if len(subParsed)==1:
			fieldNums.append(int(part))
		elif len(subParsed)==2:
			fieldNums+=range(int(subParsed[0]),int(subParsed[1])+1)
	return [fields[field-1] for field in fieldNums]

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-s", "--scores", dest="scores",
		help="comma seperated list of scores. Can also use x-y format")
	parser.add_option("-t", "--tag", dest="tag",
		help="tag field")
	parser.add_option("-d", "--delimiter", dest="delimiter",
		help="delimiter for file, defaults to pipe", default="|")
	parser.add_option("-b", "--bins", dest="bins",
		help="number of equal size bins to use, defaults to 10", default=10)
	parser.add_option("-o", "--otherFields", dest="otherFields",
		help = "list of other fields", default = None)
	parser.add_option("-r", "--reverse", action="store_true", dest="reverse",
		default=False, help="reverse sort score fields")
	parser.add_option("-w", "--weight", dest="weight", 
		help="the field which contains the sample weight, if not provide assume weight=1 for each record")
	parser.add_option("-x", "--output_bins",  dest="output_bins",
		help="output the bins to a file")
	parser.add_option("-y", "--bin_file", dest="bin_file",
		help="use existing bin file instead of recreating bins")
        (options, args) = parser.parse_args()
	if options.scores==None or options.tag==None:
		parser.error("Must specify score fields and tag field")
	reader = csv.DictReader(sys.stdin,delimiter=options.delimiter)
	fields = reader.fieldnames
        scoreFields = parseFields(options.scores,fields)
        tagField = fields[int(options.tag)-1]
	weight = None
	
	if options.weight != None:
		weight = fields[int(options.weight)-1]
	otherFields = []
	if options.otherFields !=None:
		otherFields = parseFields(options.otherFields,fields)
        getFields(reader,tagField,scoreFields,otherFields,
		numBins=options.bins,reverse=options.reverse,weight=weight,
		storeBins=options.output_bins,binFile=options.bin_file)
