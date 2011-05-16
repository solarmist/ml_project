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
  file = open('dataset.arff','r')
  lines = []
  lines = file.readlines()
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
  print len(set1), len(set2), len(set3), len(lines)
  #print index
  #find the @data line
  file.close()
  


if __name__ == '__main__':
	main()

