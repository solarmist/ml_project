#!/usr/bin/env python
# encoding: utf-8
"""
split.py

Created by Joshua Olson on 2011-05-15.
Copyright (c) 2011 solarmist. All rights reserved.
"""

import sys, random
import os

def header():
    return '''% 1. Title: Spam Classification Decision Tree
% 
% 2. Sources:
%      (a) Creator: Joshua Olson
%      (b) Date: April, 2011
% 
@RELATION spam
  
@ATTRIBUTE IP		  			NUMERIC
@ATTRIBUTE degree_domains_match	REAL
@ATTRIBUTE Subject				NUMERIC 
@ATTRIBUTE From					NUMERIC
@ATTRIBUTE text_type			NUMERIC
@ATTRIBUTE attach				NUMERIC %Or multipart
@ATTRIBUTE URLs					NUMERIC %Or url
@ATTRIBUTE URL_percent			REAL	%Or url_per
@ATTRIBUTE SPAM_percent			REAL	%Or spam_word_per
@ATTRIBUTE degree_spam			REAL	
@ATTRIBUTE spam					{1, 2}	%Actual classification (This needs to be in discrete classes)
  
@data
'''

    
def main():
    #open dataset.arff and split it into
    #Three sets of data
    #Set1 Set2 Set3
    #Set12 / Test3
    #Set13 / Test2
    #Set23 / Test1
    file = open('./dataset.arff','r')
    lines = []
    lines = file.readlines()
    #clear the header
    index = lines.index('@data\n') + 1
    lines = lines[index:]
    
    set1 = []
    set2 = []
    set3 = []
    for line in lines:
        r = int(random.uniform(1,10))
        if r % 3 == 0:
            set1.append(line)
        elif r % 3 == 1:
            set2.append(line)
        elif r % 3 == 2:
            set3.append(line)
    
    #Build the files
    set1f = open('./set1.arff','w')
    set1f.write(header())
    set2f = open('./set2.arff','w')
    set2f.write(header())
    set3f = open('./set3.arff','w')
    set3f.write(header())
    set12f = open('./set12.arff','w')
    set12f.write(header())
    test3f = open('./test3.arff','w')
    test3f.write(header())
    set13f = open('./set13.arff','w')
    set13f.write(header())
    test2f = open('./test2.arff','w')
    test2f.write(header())
    set23f = open('./set23.arff','w')
    set23f.write(header())
    test1f = open('./test1.arff','w')
    test1f.write(header())
    
    for line in set1:
        set1f.write(line)
        set12f.write(line)
        set13f.write(line)
        test1f.write(line)
        
    for line in set2:
        set2f.write(line)
        set12f.write(line)
        set23f.write(line)
        test2f.write(line)
    
    for line in set3:
        set3f.write(line)
        set13f.write(line)
        set23f.write(line)
        test3f.write(line)
    
    file.close()
    set1f.close()
    set2f.close()
    set3f.close()
    set12f.close()
    set13f.close()
    set23f.close()
    test1f.close()
    test2f.close()
    test3f.close()


if __name__ == '__main__':
	main()

