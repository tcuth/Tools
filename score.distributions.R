setwd('/data/projects/SBRE/40.enova/01.retro/01.20160923/headway')

library(dplyr)
library(ggplot2)

theme_xor <- theme_bw() +
  theme(axis.text=element_text(size=16),
        axis.title=element_text(size=18,face="bold"))

easy_read <- function(filename) {
  out <- data.table::fread(filename, sep = "|", data.table = F)
  return(out)
}

headway <- easy_read('headway.apps.psv.response')
    

headway %>% 
  ggplot(., aes(x = credit_score)) + geom_density(adjust = 3) +
  geom_vline(xintercept = 485) + xlim(c(200,850)) + 
  xlab("Credit Score") + ylab("Density") + theme_xor
  

headway %>%
  ggplot(., aes(x = fraud_score)) + geom_density(adjust = 3) +
  geom_vline(xintercept = 598) + xlim(c(1,800)) + 
  xlab("Fraud Score") + ylab("Density") + theme_xor

