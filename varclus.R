#!/usr/bin/env Rscript --vanilla --slave --quiet

suppressWarnings(suppressPackageStartupMessages(library('optparse')))
suppressWarnings(suppressPackageStartupMessages(library('Hmisc')))
suppressWarnings(suppressPackageStartupMessages(library('sqldf')))
suppressWarnings(suppressPackageStartupMessages(library('dplyr')))
suppressWarnings(suppressPackageStartupMessages(library('bit64')))


# suppress scientific notation
options(scipen=999)

# create options
option_list <- list(
	make_option(c("-k","--klusters"), action = 'store', default = 50,
		help="Number of clusters to keep [default %default]"),
	make_option(c("-n","--nvars"), action = 'store', default = 1,
		help="Number of variables to keep within each cluster [default %default]"),
	make_option(c("-t","--topK"), action = 'store', default = Inf,
		help="Lowest overall ranking feature to keep [default %default]"),
	make_option(c("-d","--delimiter"), action = 'store', default = "|",
		help="File delimiters [default: %default]"),
	make_option(c("-r","--records"), action = 'store', default = NULL,
		help="If provided, sample r records for clustering [default: %default]"),
	make_option(c("-s","--seed"), action = 'store', default = 8675309,
		help="Random seed for sampling [default: %default]"),
	make_option(c("-p","--plot"), action = 'store_true', default = FALSE,
		help = "Plot cluster heatmap [default: %default]")
)


usage = "cat FILE | %prog [options] VARIMP_FILE > OUTPUT_FILE"
arguments <- parse_args(OptionParser(option_list = option_list, usage = usage),
	positional_arguments = 1)

opt <- arguments$options

# load varimp file
varimp_file <- data.table::fread(arguments$args, sep = opt$delimiter, showProgress = FALSE,
	header = TRUE, na.strings = "", stringsAsFactors = FALSE, data.table = FALSE)

# assert varimp file has only two columns
#stopifnot(ncol(varimp_file) == 2)

# rename varimp columns
#names(varimp_file) <- c('variable','importance')

# make sure imortances are all positive
#varimp_file[,'importance'] <- abs(varimp_file[,'importance'])

# load variables file
data <- data.table::fread('cat /dev/stdin', sep = opt$delimiter, showProgress = FALSE, 
	header = TRUE, na.strings = "", stringsAsFactors = FALSE, data.table = FALSE)

# ----------------------------------------------------------

# clustering
# prep data
set.seed(opt$seed)
if(!is.null(opt$records)){
	data.sample <- data %>% tbl_df %>% sample_n(size = opt$records)
} else {
	data.sample <- data
}

# remove zero variance variables
sds <- sapply(data.sample, sd)
data.sample <- data.sample[,which(sds != 0)]
clust <- varclus(as.matrix(data.sample), 'pearson')
# 
groups <- cutree(clust$hclust, opt$klusters)
groups <- data.frame(groups)
groups$var <- row.names(groups)
# 
varimp.groups <- sqldf("select a.*, 
                       b.groups as cluster
                       from varimp_file a join groups b
                       on a.variable = b.var
                       order by b.groups, a.gain desc")

varimp.groups <- varimp.groups %>% 
  mutate(overall_rank = rank(desc(gain), ties.method = "first"))

vars_to_keep <- varimp.groups %>% tbl_df %>% group_by(cluster) %>%
  mutate(cluster_rank = rank(desc(gain), ties.method = "first")) %>% 
  dplyr::filter(cluster_rank <= opt$nvars, overall_rank <= opt$topK)

# write output to stdout
write.table(vars_to_keep, file = stdout(),
             quote = FALSE, sep = "|", na = "", row.names = F)

if(opt$p){
	x11()
	heatmap(1 - cor(data[,vars_to_keep$variable]))
	readLines(stdin(), n = 1)
	dev.off()
 }

#summary(cor(data[,vars_to_keep$variable])[lower.tri(cor(data[,vars_to_keep$variable]))])
# 
