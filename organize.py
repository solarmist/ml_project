#!/usr/bin/env python
# encoding: utf-8
"""
organize.py

This script partitions the data into periods

Created by Joshua Olson on 2011-04-23.
Copyright (c) 2011 solarmist. All rights reserved.
"""

import sys, shutil, os, datetime, fnmatch

def main():
    if len(sys.argv) != 4:
        print 'usage: ./organize.py home_dir ham_dir spam_dir'
        print 'Ex: ./organize.py ./ ham spam'
        sys.exit(1)
    home_dir = sys.argv[1]
    ham_dir =  sys.argv[2]
    spam_dir = sys.argv[3]
    
    #first partition the files into 2/per month increments / period_2011_03_01-15, period_2011_03_16-31, etc
    year = str(datetime.datetime.now().year)
    #Eg. './period_2011_'
    dir = home_dir + '/period_' + year + '_'
    for file in os.listdir(home_dir + ham_dir):
        #Check month
        for mon in range(1, 13):
            month = str(mon).zfill(2)
            for file in os.listdir(home_dir + ham_dir):
                if fnmatch.fnmatch(file, '*_0[1-9]-' + month + '-' + year + '*.txt') or \
                   fnmatch.fnmatch(file, '*_1[0-5]-' + month + '-' + year + '*.txt'):
                    #Ex. './period_2011_03_01-15'
                    period_dir = dir + month + '_01-15'
                    if not os.path.exists(period_dir):
                        os.mkdir(period_dir)
                        os.mkdir(period_dir + '/' + ham_dir)
                        os.mkdir(period_dir + '/' + spam_dir)
                        
                    shutil.move(home_dir + ham_dir + '/' + file, period_dir + '/' + ham_dir)
                        
                if fnmatch.fnmatch(file, '*_1[6-9]-' + month + '-' + year + '*.txt') or \
                   fnmatch.fnmatch(file, '*_[23][0-9]-' + month + '-' + year + '*.txt'):
                    
                    if month in ['01','03','05','07','08','10','12']:
                        end = '31'
                    elif month in ['04','06','09','11']:
                        end = '30'
                    else:
                        end = '28' #Just labelling, so ignore leap years
                    #Ex. './period_2011_03_16-31'
                    period_dir = dir + month + '_16-' + end
                    if not os.path.exists(period_dir):
                        os.mkdir(period_dir)
                        os.mkdir(period_dir + '/' + ham_dir)
                        os.mkdir(period_dir + '/' + spam_dir)
                        
                    shutil.move(home_dir + ham_dir + '/' + file, period_dir + '/' + ham_dir)

    for file in os.listdir(home_dir + spam_dir):
        #Check month
        for mon in range(1, 13):
            month = str(mon).zfill(2)
            for file in os.listdir(home_dir + spam_dir):
                if fnmatch.fnmatch(file, '*_0[1-9]-' + month + '-' + year + '*.txt') or \
                   fnmatch.fnmatch(file, '*_1[0-5]-' + month + '-' + year + '*.txt'):
                    #Ex. './period_2011_03_01-15'
                    period_dir = dir + month + '_01-15'
                    if not os.path.exists(period_dir):
                        os.mkdir(period_dir)
                        os.mkdir(period_dir + '/' + ham_dir)
                        os.mkdir(period_dir + '/' + spam_dir)

                    shutil.move(home_dir + spam_dir + '/' + file, period_dir + '/' + spam_dir)

                if fnmatch.fnmatch(file, '*_1[6-9]-' + month + '-' + year + '*.txt') or \
                   fnmatch.fnmatch(file, '*_[23][0-9]-' + month + '-' + year + '*.txt'):

                    if month in ['01','03','05','07','08','10','12']:
                        end = '31'
                    elif month in ['04','06','09','11']:
                        end = '30'
                    else:
                        end = '28' #Just labelling, so ignore leap years
                    #Ex. './period_2011_03_16-31'
                    period_dir = dir + month + '_16-' + end
                    if not os.path.exists(period_dir):
                        os.mkdir(period_dir)
                        os.mkdir(period_dir + '/' + ham_dir)
                        os.mkdir(period_dir + '/' + spam_dir)

                    shutil.move(home_dir + spam_dir + '/' + file, period_dir + '/' + spam_dir) 

if __name__ == "__main__":
	sys.exit(main())
