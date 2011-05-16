#!/bin/bash

java weka.classifiers.trees.J48 -t set12.arff -T test3.arff>results1.txt
java weka.classifiers.trees.J48 -t set13.arff -T test2.arff>results2.txt
java weka.classifiers.trees.J48 -t set23.arff -T test1.arff>results3.txt