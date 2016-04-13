#!/usr/bin/env python
#-*-coding:utf8;-*-
#author:Yinhu
for i in range(1,10):
    for j in range(1,10):
	#当乘数被乘数相等时,打印结果后换行并推出循环
        if i==j:
            print "%d * %d = %d " % (j,i,i*j)
            break
        #乘数被乘数不相等时循环出输出, 结尾加','不换行
        else:
            print "%d * %d = %d " % (j,i,i*j),
