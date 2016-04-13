#!/usr/bin/env python
#-*-coding:utf8;-*-
#author:Yinhu

print "This is console module"
for i in range(1,10):
    for j in range(1,10):
        if i==j:
            print "%d * %d = %d" % (j,i,i*j)
            break
        else:
            print "%d * %d = %d" % (j,i,i*j),
