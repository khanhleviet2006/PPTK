# Validated external reference for Python Taylor calculations.
library(survey)
args <- commandArgs(trailingOnly=TRUE)
d <- read.csv(args[1])
options(survey.lonely.psu="fail")
s <- svydesign(ids=~psu,strata=~stratum,weights=~weight,data=d,nest=TRUE)
m <- svymean(~y,s,na.rm=TRUE)
g <- svyglm(y~x,design=s,family=quasibinomial())
write.csv(data.frame(estimate=coef(m),variance=diag(vcov(m))),paste0(args[2],"_mean.csv"),row.names=FALSE)
write.csv(data.frame(beta=coef(g),variance=diag(vcov(g))),paste0(args[2],"_logistic.csv"),row.names=FALSE)
write.csv(vcov(g),paste0(args[2],"_cov.csv"),row.names=FALSE)
# Domain result retains full design degrees of freedom in variance estimation.
md <- svymean(~y,subset(s,domain==1),na.rm=TRUE)
write.csv(data.frame(estimate=coef(md),variance=diag(vcov(md))),paste0(args[2],"_domain.csv"),row.names=FALSE)
# Independent multinomial fit (nnet), numerical Hessian, survey variance aggregation.
if ("ymulti" %in% names(d)) {
  library(nnet)
  library(numDeriv)
  nm <- multinom(factor(ymulti)~x,data=d,weights=weight/mean(weight),trace=FALSE,
                 maxit=1000,abstol=1e-12,reltol=1e-12)
  coefmat <- coef(nm)
  b <- as.vector(t(coefmat))
  xx <- cbind(1,d$x); ww <- d$weight/mean(d$weight)
  objective <- function(par) {
    bb <- matrix(par,nrow=2,byrow=TRUE)
    eta <- cbind(0, xx %*% t(bb))
    eta <- eta-apply(eta,1,max)
    pp <- exp(eta)/rowSums(exp(eta))
    -sum(ww*log(pp[cbind(seq_len(nrow(d)),d$ymulti+1)]))
  }
  pp <- predict(nm,type="probs")
  yy <- model.matrix(~factor(d$ymulti)-1)[,2:3]
  scores <- cbind(xx*(ww*(yy[,1]-pp[,2])),xx*(ww*(yy[,2]-pp[,3])))
  bread <- solve(hessian(objective,b))
  meat <- svyrecvar(scores,clusters=s$cluster,stratas=s$strata,fpcs=s$fpc)
  vv <- bread %*% meat %*% bread
  write.csv(data.frame(beta=b),paste0(args[2],"_multi_beta.csv"),row.names=FALSE)
  write.csv(vv,paste0(args[2],"_multi_cov.csv"),row.names=FALSE)
}
