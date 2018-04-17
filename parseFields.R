parseFields <- function(fieldsStr) {
	fields <- integer(0)
	parsed = stringr::str_split(fieldsStr,",")[[1]]
	for(part in parsed) {
		subParsed <- stringr::str_split(part,"-")[[1]]
		if(length(subParsed) == 1) {
			fields <- c(fields, as.integer(part))
		} else if(length(subParsed) == 2) {
			fields <- c(fields, as.integer(subParsed[1]:subParsed[2]))
		}
	}

	return(fields)
}
