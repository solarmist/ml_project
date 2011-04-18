#!/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0


"""Ham and SPAM thesaurus program
This program takes two directories (a spam and a ham directory) and compiles two thesauri based on them.

Symbols, one letter words and numbers are excluded by default

ham.txt: Ham thesaurus contains all words contained in the ham directory with a frequency of each word with one word per line.

spam.txt: Spam thesaurus contains all words contained in the spam directory with a frequency of one that do not occur in the ham thesaurus.

Optional: Inside the ham directory there is an ignore list of words to discard
"""

import sys, os
import string
import nltk, nltk.corpus

def word_count_dict(home_dir, dir):
    """Returns a word/count dict for this directory."""
    word_count = {}
    #implement sampling
    ignore_file = open(home_dir + '/' + 'ignore.txt', 'r')
    ignore = nltk.word_tokenize(ignore_file.read())
    ignore_file.close()
    for filename in os.listdir(dir):
        if filename[0] != '.':
            input_file = open(home_dir + '/' + dir + '/' + filename, 'r')
            text = input_file.read()
            subjectIndex = text.find("Subject: ")
            text = text[subjectIndex:]
            #Clean the message of attachments
            attachmentIndex = text.find("Content-Disposition: attachment")
            if attachmentIndex > 0:
                text = text[:attachmentIndex]
            raw = nltk.clean_html(text)
            words = nltk.wordpunct_tokenize(raw.lower())
            for word in words:
                # Special case if we're seeing this word for the first time.
                #Ignore very short words
                if len(word) > 2:
                    if not word in word_count:
                        if word.isalpha() and word not in ignore:
                            word_count[word] = 1
                    else:
                        word_count[word] = word_count[word] + 1
            input_file.close()  # Not strictly required, but good form.
    return word_count


def build_thesaurus(home_dir, dir):
    """Prints one per line '<word> <count>' sorted by word for the given file."""
    word_count = {}
    top_50 = {}
    
    word_count = word_count_dict(home_dir, dir)
    file = open(home_dir + '/' + dir + 'Thesaurus.txt','w')
    file2 = open(home_dir + '/' + dir + 'Top50.txt','w')

    #Sort words based on the frequency of the word
    count = 0
    for word in sorted(word_count, key = word_count.get, reverse = True):
        #print word, word_count[word]
        file.write(word + ' ' + str(word_count[word]) + '\n')
        if count < 50:
            file2.write(word + ' ' + str(word_count[word]) + '\n')
            top_50[word] = word_count[word]
        count = count + 1
    
    file.close()
    file2.close()
    return word_count, top_50

def spam_unique(home_dir, ham, spam):
    unique = {}
    file = open(home_dir + '/' +  'spamOnly.txt','w')
    for word in sorted(spam, key = spam.get):
        if word not in ham:
            unique[word] = spam[word]
            file.write(word + ' ' + str(spam[word]) + '\n')
            
    file.close()
    
    
def main():
    if len(sys.argv) != 3:
        print 'usage: ./wordcount.py ham_dir spam_dir'
        sys.exit(1)

    home_dir = sys.argv[0][:-12]
    ham_dir =  sys.argv[1]
    spam_dir = sys.argv[2]
   
    ham_word_count, ham_top_50 = build_thesaurus(home_dir, ham_dir)    
    spam_word_count, spam_top_50 = build_thesaurus(home_dir, spam_dir)  
    unique_spam = spam_unique(home_dir, ham_word_count, spam_word_count)
  


if __name__ == '__main__':
    main()
