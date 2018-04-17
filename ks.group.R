#!/usr/bin/Rscript --vanilla --slave --quiet

suppressWarnings(suppressPackageStartupMessages(library('optparse')))
suppressWarnings(suppressPackageStartupMessages(library('bit64')))
suppressWarnings(suppressPackageStartupMessages(library('dplyr')))


# suppress scientific notation
options(scipen=99999)

# create options
option_list <- list(
	make_option(c("-d","--delimiter"), action = "store", default = "|",
		help = "Input file delimiter [default: |]"),
	make_option(c("-s","--scores"), action = "store", default = NULL, type = "character",
		help = "Index of score fields [default: NULL]"),
	make_option(c("-w","--weights"), action = "store", default = NULL, type = "character",
		help = "Index of weights [default: NULL]"),
	make_option(c("-t","--tag"), action = "store", default = NULL, type = "character",
		help = "Index of tag [default: NULL]"),
	make_option(c("-x","--groups"), action = "store", default = NULL, type = "character",
		help = "Index of grouping variable [default: NULL]")
)

opt <- parse_args(OptionParser(option_list = option_list))

# use data.table for fast data loading
d <- suppressWarnings(data.table::fread('cat /dev/stdin', sep = opt$delimiter, na.strings = "", data.table = F, showProgress=F, verbose = F))

# select relevant variable names for dataset
# save as strings for later use in non standard evaluation
vars <- names(d)
score_index <- creditR::parseFields(opt$scores)
score_name <- vars[score_index]
tag_index <- creditR::parseFields(opt$tag)
tag_name <- vars[tag_index]
group_index <- creditR::parseFields(opt$groups)
group_name <- vars[group_index]
group_name <- paste(group_name, collapse = ",", sep = "")

# select weights if present; save as vector
if(!is.null(opt$weights)) {
	weights_index <- eval(parse(text = opt$weights))
	weights_name <- vars[weights_index]
} else {
	weights_name <- "NULL"
}

# wrap ksC for use in lapply
ks_output <- function(df, score, tag, weights = NULL) {
	score <- substitute(score)
	score <- eval(score, df)

	tag <- substitute(tag)
	tag = eval(tag, df)

	if(!is.null(weights)) {
		w <- substitute(weights)
		w <- eval(w, df)
	} else {
		w <- NULL
	}

	creditR::ksC(score = score, tag = tag, weights = w)
}

# this is currently a hack: use strings and eval(parse(text = stuff)))
# create eval string for summarise function
summarise_str <- paste0("ks_",score_name," = ks_output(., ",score_name, ", ",tag_name, ", ", weights_name, ")", collapse = ", ")
# create ks by groups
# need to figure out how to do this using non-standard evaluation
#eval_str <- paste0("d %>% group_by(",group_name,") %>% summarise(",summarise_str, ")")
eval_str <- paste0("d %>% group_by(",group_name,") %>% summarise(",summarise_str, ", n = n(), ntarget = sum(", tag_name, "== 1))")

output <- eval(parse(text = eval_str))

# print output to stdout
write.table(output, stdout(), quote = F, sep = "|", na = "", row.names = FALSE)

