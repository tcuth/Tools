#' Plot KS Curve.
#' 
#' Plot the KS curve for a binary classification score.
#' @param score a vector of scores
#' @param y a vector of observed outcomes; must be binary
#' @param color a vector of two colors; used to overwrite ggplot2 default colors
#' @return ks a ggplot2 object containing the KS plot
#' @export

plotKS <- function(score, y, color = NULL) {
  # load ggplot2 and scales packages
  if("ggplot2" %in% installed.packages()){
    library(ggplot2)
  }
  else {
    install.packages("ggplot2")
    library(ggplot2)
  }
  
  if("scales" %in% installed.packages()){
    library(scales)
  }
  else {
    install.packages("scales")
    library(scales)
  }
  
  # check that y has exactly two unique values
  y_vals <- unique(y)
  if(length(y_vals) != 2){
    stop("y must have exactly two values.")
  }
  
  # create ecdf for each y value
  x1 <- score[y == y_vals[1]]
  x2 <- score[y == y_vals[2]]
  
  Fn1 <- ecdf(x1)
  Fn2 <- ecdf(x2)
  
  p1 <- Fn1(x1)
  p2 <- Fn2(x2)
  
  p_vals <- c(p1,p2)
  x_vals <- c(x1,x2)
  
  outcome <- c(y[y == y_vals[1]], y[y == y_vals[2]])
  
  df <- data.frame(x = x_vals, y = p_vals, outcome = outcome)
  
  # identify score location of max KS value
  x <- seq(min(x1, x2), max(x1,x2), length.out=(max(length(x1), length(x2)))) 
  x0 <- x[which( abs(Fn1(x) - Fn2(x)) == max(abs(Fn1(x) - Fn2(x))) )] 
  # guard against cases where multiple scores produce the max KS
  # in those cases, take the lowest score
  x0 <- sort(x0)
  x0 <- x0[1]
  y0 <- Fn1(x0) 
  y1 <- Fn2(x0) 
  
  # calculate KS
  # suppress warnings that get produced when ties are present
  ks.value <- suppressWarnings(ks.test(x1, x2)$statistic)
  
  # create ks plot
  ks <- ggplot(data = df, aes(x = x, y = y, color = factor(outcome))) +
    geom_line() + 
    geom_segment(x = x0, y = y0, xend = x0, yend = y1, color = 'black') +
    annotate("text", x = -Inf, y = Inf, label = paste0("KS: ", round(ks.value,2)),
             hjust = -.2, vjust = 2) +
    annotate("text", x = -Inf, y = Inf, label = paste0("Max KS Score: ", round(x0,3)),
             hjust = -.08, vjust = 4) +
    scale_y_continuous(labels = percent) + ylab("Cumluative Percentage") +
    xlab("Score") + labs(color = "Outcome") + theme_bw(base_size = 18)
  
  # incorporate colors if provided in the function call
  if(!is.null(color)){
    ks <- ks + scale_colour_manual(values = color)
  }
  
  # print plot to screen
  print(ks)
  
  #return ggplot object
  return(ks)
}


#' Calculate AUC.
#' 
#' Calculate the AUC for a binary classifier.  This function acts as a wrapper around
#' the ROCR package's AUC calculation.
#' @param score predictions from a statistical model in the probability space
#' @param y observed outcomes (must be dichotomous)
#' @param posclass a vector containing the negative and positive class labels
#' @return auc numeric auc value
#' @export
calcAUC <- function(score, y, posclass = NULL) {
  
  # check that y has exactly two unique values
  y_vals <- unique(y)
  if(length(y_vals) != 2){
    stop("y must have exactly two values.")
  }
  
  # convert factors to characters
  # makes function calls easier
  if(class(y) == "factor"){
    y <- as.character(y)
    y_vals <- unique(y)
  }
  
  
  # calculate AUC
  if(is.null(posclass)){
    perf1 <- performance(prediction(score, labels = y, label.ordering = c(y_vals[1], y_vals[2])), 'auc')
    perf2 <- performance(prediction(score, labels = y, label.ordering = c(y_vals[2], y_vals[1])), 'auc')
    return(max(as.numeric(perf1@y.values), as.numeric(perf2@y.values)))
  }
  else {
    perf <- performance(prediction(score, labels = y, label.ordering = posclass), 'auc')
    return(as.numeric(perf@y.values))
  }
}

#' Plot ROC Curve.
#' @param score predictions from a statistical model in the probability space
#' @param y observed outcomes (must be dichotomous)
#' @param posclass value for class of interest
#' @return roc a ggplot2 object containing the ROC curve
#' @export
plotROC <- function(score, y, posclass = NULL, color = NULL) {
  
  if(is.null(color)){
    color = 'black'
  }
  
  # check that y only has two values
  y_vals <- unique(y)
  if(length(y_vals) != 2){
    stop("y must have exactly two values.")
  }
  
  # convert factors to characters
  # makes function calls easier
  if(class(y) == "factor"){
    y <- as.character(y)
    y_vals <- unique(y)
  }
  
  # if not provided in the function call, set positive class as the class with the largest
  # AUC value
  if(is.null(posclass)) {
    auc1 <- calcAUC(score, y, posclass = c(y_vals[2],y_vals[1]))
    auc2 <- calcAUC(score, y, posclass = c(y_vals[1],y_vals[2])) 
    posclass <- c(y_vals[which.min(c(auc1, auc2))],
                  y_vals[which.max(c(auc1, auc2))])
    auc <- max(auc1, auc2)
  }
  else {
    auc <- calcAUC(score, y, posclass)
  }
  
  # calculate tpr and fpr
  perf <- performance(prediction(score, labels = y, label.ordering = posclass), 'tpr','fpr')
  pf <- data.frame(FalsePositiveRate = perf@x.values[[1]],
                   TruePositiveRate = perf@y.values[[1]])
  
  # create ggplot object with roc curve
  roc <- ggplot() + geom_line(data = pf, aes(x = FalsePositiveRate,
                                             y = TruePositiveRate), colour = color) +
    geom_line(aes(x=c(0,1), y = c(0,1)), linetype = 2) + xlab("False Positive Rate") +
    ylab("True Positive Rate") +
    annotate("text", x = -Inf, y = Inf, label = paste0("AUC: ", round(auc,2)),
             hjust = -.2, vjust = 2)
  
  # print curve to screen
  print(roc)
  # return ggplot object
  return(roc)
}


#' Plot cross-validation curves.
#' 
#' Plot CV values as a function of bin number.  Plot includes error bars representing one standard error.
#' The red horizontal line represnts the maximum CV value.  The blue horisontal line the largest value that is
#' no more than one standard error from the maximum CV value.  This can be used to prevent overfitting by applying
#' the 'one standard error rule' whereby the number of bins is selected by choosing the small bin value
#' within in standard error of the maximum value.
#' @param crossvalidation an object returned from a call to cvBins
#' @return a ggplot object with the CV curve.
#' @examples
#' data(GermanCredit)
#' amountCvKS <- cvBins(GermanCredit$Duration, GermanCredit$Class)
#' plotCV(amountCvKS)
#' amountCvAUC <- cvBins(GermanCredit$Amount, GermanCredit$Class, summaryFunction = 'auc')
#' plotCV(amountCvAUC)
plotCV <- function(crossvalidation){
  data <- crossvalidation$crossvalidation
  means <- apply(data,2,mean)
  sds <- apply(data,2,sd)
  idx <- crossvalidation$minbin:crossvalidation$maxbin
  sumFunc <- crossvalidation$summaryFunction
  nfolds <- crossvalidation$nfolds
  
  ks.plot <- data.frame(idx, means, sds)
  ks.plot$se <- ks.plot$sds/sqrt(nfolds)
  
  
  oneSeRule <- ks.plot$means[which.max(ks.plot$means)] - ks.plot$se[which.max(ks.plot$means)]
  
  
  p <- ggplot(ks.plot, aes(x = idx, y = means)) + geom_point() + geom_line() + 
    geom_hline(yintercept = max(ks.plot$means), color = 'red') +
    geom_hline(yintercept = oneSeRule, color = 'blue') +
    geom_errorbar(aes(ymin = means - (1 * se), ymax = means + (1 * se))) +
    ylab(paste0("CV ", toupper(sumFunc), " Value")) + 
    xlab("Number of Bins") + 
    ggtitle(paste0(toupper(sumFunc), " Optimized Number of Bins"))
  
  print(p)
  
  return(p)
}

#' Plot WOE and Percent Bad by bin.
#' 
#' Plot bar graph of WOE values by bin and line graph of median WOE value vs percent bad in each bin.
#' 
#' @param iv Discretized independent variable (i.e., a variable that has been binned); must be
#' a factor.
#' @param dv Dependent variable.
#' @param civ Continuous version of the discretized independent variable; used for calculating
#' information values
#' @return NULL; prints graphs to current graphics device.
#' @example
#' \dontrun{plotWOE(iv= test$AddrWoe, dv = test$fraud, civ = test$n_address_match)}
plotWOE <- function(iv, dv, civ){
  woe <- Woe(iv = iv, dv = dv, civ = civ)
  
  woeData <- data.frame(median = woe$civ.bin.median, posclass = woe$true.count,
                        total = woe$bin.count, info_val = woe$information.value,
                        linearity = woe$linearity, woe = woe$log.density.ratio)
  
  woeData$PctBad <- woeData$posclass/woeData$total
  woeData$bin <- rownames(woeData)
  woeData$position <- ifelse(woeData$woe < 0, 0, woeData$woe)
  
  woe_graph <- ggplot(woeData, aes(x = bin, y = woe)) +
    geom_bar(stat = 'identity') +
    geom_text(aes(y = position + 0.05, label = paste0("WOE: ", round(woe,2)))) +
    geom_text(aes(y = position + 0.02, label = paste0("IV: ", round(info_val,2)))) +
    annotate("text", x = -Inf, y = Inf, parse = TRUE,
             label = paste0("r: ",round(woe$linearity,2)),
             hjust = -.2, vjust = 2) +
    annotate("text", x = -Inf, y = Inf, parse = TRUE,
             label = paste0("IV: ",round(sum(woeData$info_val),2)),
             hjust = -.2, vjust = 4.2) +
    geom_hline(yintercept = 0, color = 'black')
  
  linearity_graph <- ggplot(woeData, aes(x = median, y = PctBad)) +
    geom_point() + geom_line() +
    scale_x_continuous(breaks = woeData$median, labels=rownames(woeData)) +
    annotate("text", x = -Inf, y = Inf, parse = TRUE,
             label = paste0("r: ",round(woe$linearity,2)),
             hjust = -.2, vjust = 2) +
    annotate("text", x = -Inf, y = Inf, parse = TRUE,
             label = paste0("IV: ",round(sum(woeData$info_val),2)),
             hjust = -.2, vjust = 4.2) +
    geom_hline(yintercept = weighted.mean(woeData$PctBad, woeData$total), color = 'red')
  
  plots <- grid.arrange(woe_graph, linearity_graph, ncol = 2)
  print(plots)
}
