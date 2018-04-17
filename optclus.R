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
	make_option(c("-e","--eigen-threshold"), action = 'store', default = 0.7,
		help="Threshold at which to group correlated variables, corresponds to 2nd eigenvalue of cluster correlation matrix [default: %default]"),
	make_option(c("-n","--nvars"), action = 'store', default = 1,
		help="Number of variables to keep within each cluster, use 'Inf' to output all variables [default %default]"),
	make_option(c("-t","--topK"), action = 'store', default = Inf,
		help="Lowest overall ranking feature to keep [default %default]"),
	make_option(c("-d","--delimiter"), action = 'store', default = "|",
		help="File delimiters [default: %default]"),
	make_option(c("-r","--records"), action = 'store', default = NULL,
		help="If provided, sample r records for clustering [default: %default]"),
	make_option(c("-s","--seed"), action = 'store', default = 8675309,
		help="Random seed for sampling [default: %default]")
)


usage = "cat FILE | %prog [options] VARIMP_FILE > OUTPUT_FILE"
arguments <- parse_args(OptionParser(option_list = option_list, usage = usage),
	positional_arguments = 1)

opt <- arguments$options

# load varimp file
write("Loading variable importance file... ",stderr())
varimp_file <- data.table::fread(arguments$args, sep = opt$delimiter,
	header = TRUE, na.strings = "", stringsAsFactors = FALSE, data.table = FALSE, showProgress = FALSE)

# assert varimp file has only two columns
#stopifnot(ncol(varimp_file) == 2)

# rename varimp columns
#names(varimp_file) <- c('variable','importance')

# make sure imortances are all positive
#varimp_file[,'importance'] <- abs(varimp_file[,'importance'])
write("Done.",stderr())

# load variables file
write("Loading data file...",stderr())
data <- data.table::fread('cat /dev/stdin', sep = opt$delimiter, integer64 = "numeric",
	header = TRUE, na.strings = "", stringsAsFactors = FALSE, data.table = FALSE, showProgress = FALSE)

data <- data[,varimp_file$variable]

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

data.num <- as.matrix(data.sample)
write("Done.",stderr())

write("Creating varclus object...", stderr())
clust <- varclus(data.num, 'pearson')
write("Done.", stderr())
#----------------------------------------------------------

# function to evaluate number of clusters
check_clus <- function(n_clus, varclus_obj) {
	cluster <- cutree(varclus_obj$hclust, n_clus)
	groups <- data.frame(cluster)
	groups$var <- row.names(groups)

	clusters <- groups$cluster
	for (cluster in unique(clusters)) {
		included <- groups[clusters == cluster, 'var']
		if (length(included) > 1) {
			group_cor <- varclus_obj$sim[included,included]
			eigen_vals <- eigen(group_cor, symmetric = T, only.values=T)$values
			# check 2nd eigenvalue vs threshold
			if (eigen_vals[2] > opt$'eigen-threshold') {
				return (FALSE)
			}
		}
	}
	return (TRUE)
}

#----------------------------------------------------------

min_cut <- 1
max_cut <- ncol(clust$sim)

# test n_clus in middle of range (always round down)
# if 2nd eigen > threshold, we want at least one more than n_clus tested
# if 2nd eigen <= threshold, upper bound is n_clus
# range will converge to two consecutive values
# test lower value and keep if condition satisfied, otherwise upper
write("Finding optimal clusters...",stderr())
while (min_cut != max_cut) {
	n_clus <- floor((min_cut + max_cut)/2)
	write(sprintf("Optimal number of clusters is between %i and %i; Testing %i clusters", min_cut, max_cut, n_clus), stderr())
	satisfy <- check_clus(n_clus, clust)
	if(satisfy) {
		max_cut <- n_clus
	}
	else {
		min_cut <- n_clus + 1
	}
}

# cut tree at optimal number of clusters
write(sprintf("Optimal clusters at correlation threshold of %1.2f: %i", opt$'eigen-threshold', min_cut), stderr())
cluster <- cutree(clust$hclust, min_cut)
groups <- data.frame(cluster)
groups$var <- row.names(groups)

varimp.groups <- sqldf("select a.*,
                       b.cluster
                       from varimp_file a join groups b
                       on a.variable = b.var
                       order by b.cluster, a.gain desc")

varimp.groups <- varimp.groups %>% 
  mutate(overall_rank = rank(desc(gain), ties.method = "first"))

vars_to_keep <- varimp.groups %>% tbl_df %>% group_by(cluster) %>%
  mutate(cluster_rank = rank(desc(gain), ties.method = "first")) %>% 
  dplyr::filter(cluster_rank <= opt$nvars, overall_rank <= opt$topK)

# write output to stdout
write.table(vars_to_keep, file = stdout(),
             quote = FALSE, sep = "|", na = "", row.names = F)

#if(opt$p){
#	x11()
#	heatmap(1 - cor(data[,vars_to_keep$variable]))
#	readLines(stdin(), n = 1)
#	dev.off()
#}

#summary(cor(data[,vars_to_keep$variable])[lower.tri(cor(data[,vars_to_keep$variable]))])
# 
