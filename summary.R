#!/usr/bin/Rscript --vanilla --slave --quiet

suppressWarnings(suppressPackageStartupMessages(library('Hmisc')))
suppressWarnings(suppressPackageStartupMessages(library('optparse')))
suppressWarnings(suppressPackageStartupMessages(library('bit64')))

# suppress scientific notation
options(scipen=999)

# create options
option_list <- list(
	make_option(c("-d","--delimiter"), action = "store", default = "|",
		help = "Input file delimiter [default: |]"),
	make_option(c("-v","--variables"), action = "store", default = NULL, type = "character",
		help = "Index of variables to use in Linux format [default: NULL]"),
	make_option(c("-w","--weights"), action = "store", default = NULL, type = "integer",
		help = "Index of weights [default: NULL]")
)

opt <- parse_args(OptionParser(option_list = option_list))

#data <- read.table(pipe('cat /dev/stdin'), sep = opt$delimiter, header = TRUE,
#	na.strings = "", quote = "", stringsAsFactors = FALSE, comment.char = "")

# use readr for faster reading
#data <- readr::read_delim(pipe('cat /dev/stdin'), delim = opt$delimiter, quote = "", na = "")

# use data.table for fastest reading
data <- data.table::fread('cat /dev/stdin', sep = opt$delimiter, na.strings = "", data.table = F, showProgress=F)


if(is.null(opt$weights)) {
	w <- rep(1, nrow(data))
} else {
	w <- data[[opt$weights]]
}

variables <- creditR::parseFields(opt$variables)
data <- data[,variables]

sbre.summary <- function(x, w = NULL) {
	if (is.null(w)) {
		w <- rep(1, length(x))
	}
	min <- min(x[x >= 0])
	max <- max(x[x >= 0])
	mean <- wtd.mean(x[x >= 0], w[x >= 0])
	missing <- ((x == -1) %*% w)/sum(w)
	percentiles <- unname(wtd.quantile(x[x >= 0], w[x >= 0], probs = c(0.25, 0.5, 0.75)))
	sd <- sqrt(wtd.var(x[x >= 0], w[x >= 0]))
	gt0 <- ((x > 0) %*% w)/sum(w)
	return(c(mean = mean, median = percentiles[2], 
		p25 = percentiles[1], p75 = percentiles[3],
		pctmissing = missing, pctpopulated = 1 - missing,
		sd = sd, gt0 = gt0, min = min, max = max))
}

output <- t(sapply(data, sbre.summary, w = w))
output <- cbind(variable = names(data), output)
write.table(output, stdout(), quote = F, sep = "|", na = "", row.names = FALSE)

