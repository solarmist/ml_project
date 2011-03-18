#!/usr/bin/python

import random, sys

d = [0,0,0,0,0,0,0,0,0,0]

for i in range(int(sys.argv[1])):
    r = int(random.uniform(0,10))
    d[r] = d[r] + 1

print d	    