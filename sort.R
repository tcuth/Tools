#!/usr/bin/env Rscript --vanilla --slave --quiet

suppressWarnings(suppressPackageStartupMessages(library('optparse')))
suppressWarnings(suppressPackageStartupMessages(library('bit64')))
suppressWarnings(suppressPackageStartupMessages(library('dplyr')))


# suppress scientific notation
options(scipen=99999)

# create options
option_list <- list(
	make_option(c("-d","--delimiter"), action = "store", default = "|",
		help = "Input file delimiter [default: |]"),
	make_option(c("-f","--fields"), action = "store", default = '1', type = "character",
		help = "Index of fields by which to sort (in Linux fields format) [default: NULL]"),
	make_option(c("-r","--reverse"), action = "store_true", default = FALSE, type = "logical",
		help = "Reverse sort (i.e., sort descending) [default: False]")
)

opt <- parse_args(OptionParser(option_list = option_list))

# use data.table for fast data loading
d <- data.table::fread('cat /dev/stdin', sep = opt$delimiter, na.strings = "", data.table = F, showProgress=F)

# parse fields by which to sort
fields_index <- creditR::parseFields(opt$fields)

# select fields by which to sort
sort_fields <- names(d)[fields_index]

# create sort string
sort_str <- paste0(sort_fields, collapse = ",")
# dplyr str
if (opt$reverse) {
	eval_str <- paste0("d %>% arrange(desc(", sort_str, "))")
} else {
	eval_str <- paste0("d %>% arrange(", sort_str, ")")
}
# evaluate
output <- eval(parse(text = eval_str))

# print output to stdout
write.table(output, stdout(), quote = F, sep = opt$delimiter, na = "", row.names = FALSE)

