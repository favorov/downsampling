opts <- commandArgs(trailingOnly = TRUE)
pipeline.results<-read.table(opts[1],header=TRUE)
sample_name<-strsplit(opts[1],'\\.')[[1]][[1]]
plotname<-paste(sample_name,".png",sep="")
TPR=pipeline.results[,'intersection']/
#test line
print (pipeline.results[,'intersection']+pipeline.results[,'original_only'])
png(plotname)
plot(pipeline.results[,'e_cov'],TPR,main=sample_name,ylim=c(0,1),xlab='coverage')
dev.off()
