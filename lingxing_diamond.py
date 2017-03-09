#!/usr/bin/env python
#!-*- coding:utf-8 -*-
#author:Yinhu
n=17
m=15
str1="*"
for i in range(1,n,2):
    if i<=n/2:
        print (str1*i).center(m)
    elif i==(n-i+1):
        continue
    else:
        print (str1*(n-i-1)).center(m)

"""
#!/usr/bin/env python
n=17
#m位字符串总长度
m=15
str1="*"
#循环输出*，步长为2，及n=17时，i=1,3,5...
for i in range(1,n,2):
#当值小于一半时，输出的*递增
    if i<=n/2:
#str1*i输出*的个数，center(width,fillchar)是字符串的方法，
#该方法返回一个原字符串居中,并使用空格或者指定字符(fillchar)填充至长度 width 的新字符串。
        print (str1*i).center(m)
#因为步长为2,当n为中间值时会出现同样数量的*输出两次的问题，通过处理跳过该情况
    elif i==(n-i+1):
        continue
#依次减少输出的*，因为步长为2,通过n-i-1可以算出剩下的应该输出*的个数，如果n为偶数时应该为n-i-2
    else:
        print (str1*(n-i-1)).center(m)
"""
