#!/usr/bin/python -tt
# Copyright 2010 Google Inc.
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0


"""Ham and SPAM thesaurus program
This program takes two directories (a spam and a ham directory) and compiles two thesauri based on them.

Symbols, one letter words and numbers are excluded by default

ham.txt: Ham thesaurus contains all words contained in the ham directory with a frequency of each word with one word per line.

spam.txt: Spam thesaurus contains all words contained in the spam directory with a frequency of one that do not occur in the ham thesaurus.

Optional: Inside the home directory there is an ignore list of words to discard
"""

import sys, os
import random, string
import nltk, nltk.corpus

class DataMember:
    def __init__(self):
        self.ip_address = ''
        self.degree_domains_match = 0.0
        self.subject = ''
        self.name = ''
        #type is True for HTML, False for text
        self.type_HTML = False
        #-1 for no attachments, 0 for text attachments, 1 for non-text attachments
        self.attachments = -1
        self.num_urls = 0
        self.percent_urls = 0.0
        self.percent_spam = 0.0
        self.degree_spam = 0.0
        #False for ham, True for spam
        self.spam = False

    def _print(self, str):
        print str % \
            (self.ip_address,           \
            self.degree_domains_match,  \
            self.subject,               \
            self.name,                  \
            self.type_HTML,             \
            self.attachments,           \
            self.num_urls,              \
            self.percent_urls,          \
            self.percent_spam,          \
            self.degree_spam,           \
            self.spam)    
        
    def printFile(self):
        str = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s"
        self._print(str)
        
        
    def println(self):
        print "New entry::"
        str = "%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s"
        self._print(str)
        print ''
        

def word_count_dict(home_dir, dir, percent):
    """Returns a word/count dict for this directory."""
    word_count = {}
    file_list = os.listdir(home_dir + dir)
    count = len(file_list)
    numSamples = max(1, int(count * percent))
    sample_files = []
    #Sample x% of all files to build this thesaurus 
    for n in range(numSamples):
        sample_files.append( file_list[ int(random.uniform(0,count)) ] )
    if os.path.isfile(home_dir + 'ignore.txt'):
        ignore_file = open(home_dir + 'ignore.txt', 'r')
        ignore = nltk.word_tokenize(ignore_file.read())
        ignore_file.close()
    else:
        ignore_file = []
        
    for filename in sample_files:
        if filename[0] == '.':
            continue
        input_file = open(home_dir + dir + '/' + filename, 'r')
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


def build_thesaurus(home_dir, dir, percent):
    """Prints one per line '<word> <count>' sorted by word for the given file."""
    word_count = {}
    top_50 = {}
    word_count = word_count_dict(home_dir, dir, percent)
    file = open(home_dir + dir + 'Thesaurus.txt','w')
    file2 = open(home_dir + dir + 'Top50.txt','w')
    #Sort words based on the frequency of the word
    count = 0
    for word in sorted(word_count, key = word_count.get, reverse = True):
        #print word, word_count[word]
        file.write(word + ' ' + str(word_count[word]) + '\n')
        if count < len(word_count) / 2:
            file2.write(word + ' ' + str(word_count[word]) + '\n')
            top_50[word] = word_count[word]
        else:
            break
        count = count + 1
    file.close()
    file2.close()
    return word_count, top_50
    

def spam_unique(home_dir, ham, spam):
    unique = {}
    file = open(home_dir + 'spamOnly.txt','w')
    for word in sorted(spam, key = spam.get):
        if spam[word] == 1 and word not in ham:
            unique[word] = spam[word]
            file.write(word + ' ' + str(spam[word]) + '\n')        
    file.close()
    
    
def build_dataset(home_dir, dir, spam, spam_top_50):
    """Build dataset
    Data set should have the fields
    1.) IP Address from the received field in the header
    2.) Matching degree of domain names between Message-Id and (Received/From ??) field (Easy just read and compare)
    3.) Subject (Easy just read it)
    4.) Name from the From field (Easy just read it)
    5.) Content type (Easy just read it)
    6.) Attachments: none, text, or non-text (Need to parse this)
    7.) Number of URLs present (Count http:// links)
    8.) URL ratio (% of message body that is URLs) (This one is tricky, how much of the message to use?)
    9.) SPAM word ratio (Again how much of the message to use? Exclude header and attachments?)
    10.) SPAM degree as by equation in paper (Simple calculation)
    11.) Classification label: Spam or Ham (What the classification SHOULD be. Predefined by filename)"""
    file_list = os.listdir(home_dir + dir)
    count = len(file_list)
    data_set = {}
    for file_name in file_list:
        data_set[file_name] = DataMember()
        if file_name[0] == '.':
            continue 
        file = open(home_dir + dir + '/' + file_name)
        for line in file:
            #1.) IP Address from the received field in the header (Easy just read it)
            #Get the IP address of the last Received from field unless its 127.0.0.1
            if line.startswith('Received: from'):
                start = line.find('[') + 1
                end = line.find(']') 
                if start < end and line[start:end].find('127.0.0.1') == -1:
                    data_set[file_name].ip_address = line[start:end]
                    colon = data_set[file_name].ip_address.find(':')
                    if colon != -1:
                        data_set[file_name].ip_address = data_set[file_name].ip_address[:colon]
            #3.) Subject (Easy just read it)          
            if line.startswith('Subject: '):
                data_set[file_name].subject = line[9:-1]
                #print file_name
                #print data_set[file_name].subject

            #3.) Subject (Easy just read it)          
            if line.find('http://') != -1:
                if line.find('schema') == -1 and line.find('Schema') == -1:
                    print line
                
        #print data_set[file_name].println()
        file.close()
    #Repeat for ham files
    
    
def main():
    if len(sys.argv) != 4:
        print 'usage: ./dataset.py ham_dir spam_dir %_to_sample'
        sys.exit(1)
    home_dir = sys.argv[0][:-10]
    ham_dir =  sys.argv[1]
    spam_dir = sys.argv[2]
    sample_size = int(sys.argv[3]) / 100.0 # as a %
    #Sample ham and spam, don't use the entire corpus
    ham_word_count, ham_top_50 = build_thesaurus(home_dir, ham_dir, 1.0) #Check against all ham files
    spam_word_count, spam_top_50 = build_thesaurus(home_dir, spam_dir, sample_size)  
    unique_spam = spam_unique(home_dir, ham_word_count, spam_word_count)
    
    build_dataset(home_dir, spam_dir, spam_word_count, spam_top_50)


if __name__ == '__main__':
    main()
