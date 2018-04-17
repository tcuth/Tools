# helper function to parse command line fields argument

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
