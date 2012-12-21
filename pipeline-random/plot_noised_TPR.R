prefix='chr1_gl000192_random-cheapseq-m1000-c100-rd100'
postfix='.report.txt'
noise=c('500','100','50','20','10')
a<-read.table(paste(c(prefix,postfix),collapse=''),header=TRUE)
TPR=a[,'intersection']/(a[,'intersection']+a[,'original_only'])
e_cov=a[,'e_cov']
png('TPR_noised_100.png',width=640,height=640)
plot(e_cov,TPR,main='TPR, noised, dowsample from 100',ylim=c(0,1),xlab='coverage',ylab='TPR',cex=c(1))
for (ind in 1:5)
{
	a<-read.table(paste(c(prefix,"-n",noise[ind],postfix),collapse=''),header=TRUE)
	TPR=a[,'intersection']/(a[,'intersection']+a[,'original_only'])
	e_cov=a[,'e_cov']
	points(e_cov,TPR,ylim=c(0,1),pch=1+ind,cex=c(1))
}
dev.off()