#!/usr/bin/env python


for i in range(2,100):
    j=2
    while j<=(i/j):
	if not(i%j):
	    break
        j=j+1
    if j>(i/j):
        print i, "is sushu"

