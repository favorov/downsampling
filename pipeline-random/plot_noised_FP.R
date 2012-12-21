prefix='chr1_gl000192_random-cheapseq-m1000-c100-rd100'
postfix='.report.txt'
noise=c('500','100','50','20','10')
a<-read.table(paste(c(prefix,postfix),collapse=''),header=TRUE)
FP=a[,'called_only']
e_cov=a[,'e_cov']
png('FP_noised_100.png',width=640,height=640)
plot(e_cov,FP,main='FP, noised, dowsample from 100',xlab='coverage',ylab='FP#',ylim=c(0,15),cex=c(1))
for (ind in 1:5)
{
	a<-read.table(paste(c(prefix,"-n",noise[ind],postfix),collapse=''),header=TRUE)
	FP=a[,'called_only']
	e_cov=a[,'e_cov']
	points(e_cov,FP,ylim=c(0,15),pch=1+ind,cex=c(1))
}
dev.off()
