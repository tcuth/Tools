weighted.cdf <- function(data, variable, weights=NULL) {
  # Calcluates a weighted or non weighted CDF for plotting.
  # 
  # Args:
  #   data: data frame to use 
  #   variable: variable name in dataset (quoted)
  #   weights: weights variable in dataset (quoted); NULL if weights = 1
  #
  # Returns:
  #   data.frame with empirical cdf
  df <- data[order(data[[variable]]), ]
  if(is.null(weights)) {
    df$w <- 1
  } else {
    df$w <- df[[weights]]
  }
  df$x <- df[[variable]]
  df$cum.pct <- with(df, cumsum(x * w) / sum(x * w))
  df <- df[,c('x','cum.pct')]
  names(df) <- c(variable,'cum.pct')
  return(df)
}