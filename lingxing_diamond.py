#!/usr/bin/env python
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
