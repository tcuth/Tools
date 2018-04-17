#!/usr/bin/Rscript --vanilla --slave --quiet

suppressWarnings(suppressPackageStartupMessages(library('optparse')))
suppressWarnings(suppressPackageStartupMessages(library('bit64')))

# suppress scientific notation
options(scipen=99999)

# create options
option_list <- list(
	make_option(c("-d","--delimiter"), action = "store", default = "|",
		help = "Input file delimiter [default: |]"),
	make_option(c("-s","--scores"), action = "store", default = NULL, type = "character",
		help = "Index of variables to use (in Linux fields format) [default: NULL]"),
	make_option(c("-w","--weights"), action = "store", default = NULL, type = "integer",
		help = "Index of weights [default: NULL]"),
	make_option(c("-t","--tag"), action = "store", default = NULL, type = "integer",
		help = "Index of tag [default: NULL]")
)

opt <- parse_args(OptionParser(option_list = option_list))

# use data.table for fast data loading
d <- suppressWarnings(data.table::fread('cat /dev/stdin', sep = opt$delimiter, na.strings = "", data.table = F, showProgress=F))

# parse score and tag indices
# truthfully, a parseFields function is needed
# this is a cheap hack for the time being
scores_index <- creditR::parseFields(opt$scores)
tag_index <- eval(parse(text = opt$tag))

# select scores; save as data.frame
scores <- d[, scores_index, drop = F]
# select tag; save a vector
tag <- d[, tag_index, drop = T]
# select weights if present; save as vector
if(!is.null(opt$weights)) {
	weights_index <- eval(parse(text = opt$weights))
	weights <- d[, weights_index, drop=T]
} else {
	weights <- NULL
}

# wrap ksC for use in lapply
ks_output <- function(x) {
	creditR::ksC(x, tag = tag, weights = weights)
}

# apply ksC to each column in scores
output <- lapply(scores, ks_output)
# collect output
output <- do.call('rbind',output)
# cbind variable names and KS values
output <- cbind(names(scores), output)
# add header to output
colnames(output) <- c("fieldName","maxKS")
# print output to stdout
write.table(output, stdout(), quote = F, sep = "|", na = "", row.names = FALSE)

