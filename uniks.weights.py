#!/data/bin/anaconda/bin/python
import numpy
from optparse import OptionParser
import sys

HEADER="fieldName,maxKS"

def calcKS(score,tag,weights,totalZero,totalOne):
	index = numpy.argsort(score)[::-1]
	zeroSoFar = oneSoFar = maxKS = x_val = 0.
	lastScore = float('nan')
#	print "---"
	for i,ind in enumerate(index):
		thisScore = score[ind]
		thisWeight = weights[ind]
		if thisScore != lastScore:
			lastScore = thisScore
			ks = (oneSoFar/totalOne)-(zeroSoFar/totalZero)
			if abs(ks)>abs(maxKS):
				maxKS=ks
				x_val=thisScore
		if tag[ind] == 0:
			zeroSoFar+=thisWeight
		elif tag[ind] ==1:
			oneSoFar+=thisWeight
	return maxKS,x_val
	

def getFields(inFH, target, scores,weightField,delim="|",hasHeader=True,index=False):
	scoreNames = []
	if index:
		print HEADER+",atScore"
	else:
		print HEADER
	if hasHeader:
		parsed = inFH.readline().strip().split(delim)
		for score in scores:
			scoreNames.append(parsed[score])
	else:
		for score in scores:
			scoreNames.append(score)
	#use np to read just the right columns
	cols = [target]+scores
	if weightField!=-1:
		cols+=[weightField]
	data = numpy.genfromtxt(inFH,unpack=True,delimiter=delim,usecols=cols,comments=None)
	if weightField==-1:
		weights = numpy.ones(len(data[0]))
	else:
		weights = data[-1]
	tags = data[0]
	numZero = numpy.sum(weights[data[0]==0])
	numOne = numpy.sum(weights[data[0]==1])
	for  name,score in zip(scoreNames,data[1:len(scores)+1]):
		ks,x_val = calcKS(score,tags,weights,numZero,numOne)
		if index:
			print name+","+str(ks)+","+str(x_val)
		else:
			print name+","+str(ks)
			
			

def parseFields(fieldsStr):
	fields = []
	parsed = fieldsStr.split(",")
	for part in parsed:
		subParsed = part.split("-")
		if len(subParsed)==1:
			fields.append(int(part))
		elif len(subParsed)==2:
			fields+=range(int(subParsed[0]),int(subParsed[1])+1)
	
	return [field-1 for field in fields]

if __name__ == "__main__":
        parser = OptionParser()
        parser.add_option("-s", "--scores", dest="scores",
                help="comma seperated list of scores. Can also use x-y format")
        parser.add_option("-t", "--tag", dest="tag",
                help="tag field")
        parser.add_option("-d", "--delimiter", dest="delimiter",
                help="delimiter for file, defaults to pipe", default="|")
	parser.add_option("-x", "--index", dest="index",action="store_true",
		help="return index of maximum separation", default=False)
	parser.add_option("-f", "--noHeader", action="store_false", dest="hasHeader",
		default=True, help="specifiy this option if no header on file")
	parser.add_option("-w", "--weight", dest="weight",
			help="weight field")
        (options, args) = parser.parse_args()
	scoreFields = parseFields(options.scores)
	tagField = int(options.tag)-1 
	weightField = -1
	if options.weight != None:
		weightField = int(options.weight)-1
	getFields(sys.stdin,tagField,scoreFields,weightField,delim=options.delimiter,index=options.index)

