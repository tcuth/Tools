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
	make_option(c("-p","--probs"), action = "store", default = NULL, type = "character",
		help = "Comma separated list of quantiles to calculate [default: NULL]"),
	make_option(c("-x","--groups"), action = "store", default = NULL, type = "character",
		help = "Index of grouping variable [default: NULL]"),
	make_option(c("-t","--tag"), action = "store", default = NULL, type = "character",
	   help = "Index of tag variable [default: NULL]")
)

opt <- parse_args(OptionParser(option_list = option_list))

# use data.table for fast data loading
d <- data.table::fread('cat /dev/stdin', sep = opt$delimiter, na.strings = "", data.table = F, showProgress=F)

# select relevant variable names for dataset
# save as strings for later use in non standard evaluation
vars <- names(d)
score_index <- creditR::parseFields(opt$scores)
score_name <- vars[score_index]
tag_index <- creditR::parseFields(opt$tag)
tag_name <- vars[tag_index]
probs <- creditR::parseFloats(opt$probs)
probs <- sort(probs)
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

# create weighted quantile function that takes data.frame as first argument
# for dplyr compatibility
quantile_wrapper <- function(df, x, p = 0.5, w = NULL) {
  x <- substitute(x)
  x <- eval(x, df)
  
  w <- substitute(w)
  if(!is.null(w)) {
    w <- eval(w, df)
  } else {
    w <- rep(1, length(x))
  }
  
  out <- Hmisc::wtd.quantile(x = x, probs = p, weights = w)
  return(data.frame(t(out)))
}

fdr <- function(df, x, t, p = 0.5, w = NULL) {
  x <- substitute(x)
  x <- eval(x, df)
  
  t <- substitute(t)
  t <- eval(t, df)
  
  w <- substitute(w)
  if(!is.null(w)) {
    w <- eval(w, df)
  } else {
    w <- rep(1, length(x))
  }
  
  q <- Hmisc::wtd.quantile(x = x, probs = p, weights = w)
  
  nout <- length(q)
  
  out <- vector("numeric",nout)
  
  for(i in 1:nout) {
    out[[i]] <- (t[x > q[[i]]] %*% w[x > q[[i]]]) / (t %*% w)
  }
  
  return(data.frame(t(out)))
  
}

# this is currently a hack: use strings and eval(parse(text = stuff)))
# create eval string for summarise function
# create fdr by groups
# need to figure out how to do this using non-standard evaluation
eval_str <- paste0("d %>% group_by(",group_name,") %>% do(fdr(., x = ", score_name, ", t = ", tag_name, ", p = probs, w = ",weights_name,"))")
# old quantile wrapper function for testing
#eval_str <- paste0("d %>% group_by(",group_name,") %>% do(quantile_wrapper(., x = ", score_name, ", p = probs, w = ",weights_name,"))")
output <- eval(parse(text = eval_str))
names(output)[-1] <- paste0("p",probs)

# print output to stdout
write.table(output, stdout(), quote = F, sep = "|", na = "", row.names = FALSE)

