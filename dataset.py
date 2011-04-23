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
import random, string, email, re
import nltk, nltk.corpus

class DataMember:
    """Defines a line in the dataset"""
    def __init__(self):
        self.ip_address = ''
        self.degree_domains_match = 0.0
        self.subject = ''
        self.name = ''
        #type is 1 for HTML, 2 for text, 3 for mixed
        self.type_HTML = 1
        #-1 for no attachments, 0 for text attachments, 1 for non-text attachments
        self.attachments = -1
        self.num_urls = 0
        self.percent_urls = 0.0
        self.percent_spam = 0.0
        self.degree_spam = 0.0
        #1 for ham, 2 for spam
        self.spam = 1
    
    def _print(self, format):
        return format % \
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
    
    def stringFile(self):
        format = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s'
        return self._print(format)
    
    def stringPrint(self):
        format = '( %s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s|||%s )'
        return self._print(format)        
    


def get_message_body(mail):
    text = ''
    if not mail.is_multipart():
        text = re.sub('(=?[\\r\\n])|(=[\\da-fA-F]{2})','', mail.get_payload())
    else:
        for part in mail.get_payload():
            attachment = False
            for key in part.keys():
                #Check all keys for an attachment name
                if key.startswith('Content'):
                    if str(part[key]).find('name') != -1:
                        attachment = True
            #Only check get the body of the next part if it's not an attachment
            if not attachment:
                text += get_message_body(part) + ' '  
    return text


def get_message_len(mail):
    text = 0 #Will be off by one, but this prevents /0 errors
    if not mail.is_multipart():
        text = len(mail.get_payload())
    else:
        for part in mail.get_payload():
            attachment = False
            for key in part.keys():
                #Check all keys for an attachment name
                if key.startswith('Content'):
                    if str(part[key]).find('name') > -1:
                        attachment = True
            #Only check the len of the next part if it's not an attachment
            if not attachment:                    
                text += get_message_len(part)
    return max(text,1)    


def get_type_content(mail):
    """Return values
    text based = 1
    HTML based = 2
    mixed = 3"""
    type = 1
    if not mail.is_multipart():
        #Contains an attachment
        for key in mail.keys():
            #Check all keys for an attachment file"name"
            if key.startswith('Content'):
                if str(mail[key]).find('name') == -1:
                    if str(mail[key]).startswith('text/html'):
                        if type <= 2:
                            type = 2
                        else:
                            type = 3
                    elif str(mail[key]).startswith('text/plain'):
                        if type == 2:
                            type = 3
        return type
    else:
        for part in mail.get_payload():
            temp = get_type_content(part)
            if (type > 1 and type != temp):
                return 3
            else:
                type = temp
    return type


def get_type_attachments(mail):
    """Return values
    No attachments = 1
    Text attachments only = 2
    Non-text attachments only = 3
    Mixed attachments = 4"""
    type = 1
    if not mail.is_multipart():
        #Contains an attachment
        for key in mail.keys():
            #Check all keys for an attachment name
            if key.startswith('Content'):
                if str(mail[key]).find('name') != -1:
                    if str(mail[key]).startswith('text'):
                        if type <= 2:
                            type = 2
                        else:
                            type = 4
                    else: #Non-text attachment
                        if type % 2: 
                            type = 3
                        else:
                            type = 4
        return type
    else:
        for part in mail.get_payload():
            temp = get_type_attachments(part)
            if temp > 3 or (type > 1 and type != temp):
                return 4
            else:
                type = temp
    return type


def word_count_dict(home_dir, dir, percent):
    """Returns a word/count dict for this directory."""
    word_count = {}
    file_list = os.listdir(home_dir + dir)
    count = len(file_list)
    num_samples = max(1, int(count * percent))
    sample_files = []
    
    #Sample x% of all files to build this thesaurus 
    for n in range(num_samples):
        sample_files.append( file_list[ int(random.uniform(0,count)) ] )
        
    #Load the list of words to ignore (optional)
    if os.path.isfile(home_dir + 'ignore.txt'):
        ignore_file = open(home_dir + 'ignore.txt', 'r')
        ignore = nltk.word_tokenize(ignore_file.read())
        ignore_file.close()
    else:
        ignore_file = []
        
    for file_name in sample_files:
        #Ignore files that start with .
        if file_name[0] == '.':
            continue
        input_file = open(home_dir + dir + '/' + file_name, 'r')
        mail = email.message_from_file(input_file)
        input_file.close()
        
        #Get the message contents
        text = get_message_body(mail)
            
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
    2.) Matching degree of domain names between Message-Id and Received/From
    3.) Subject 
    4.) Name from the From field 
    5.) Content type
    6.) Attachments: none, text, or non-text 
    7.) Number of URLs present 
    8.) URL ratio 
    9.) SPAM word ratio 
    10.) SPAM degree as by equation in paper 
    11.) Classification label: Spam or Ham """
    
    file_list = os.listdir(home_dir + dir)
    count = len(file_list)
    data_set = {}
    for file_name in file_list:
        data_set[file_name] = DataMember()
        #Ignore files that start with .
        if file_name[0] == '.':
            continue 
        #print file_name    
        file = open(home_dir + dir + '/' + file_name)
        mail = email.message_from_file(file)
        file.close()
        
        #Extract information from header
        for key in mail.keys():
            #1.) IP Address from the received field in the header (Easy just read it)
            #Get the IP address of the last Received from field unless its 127.0.0.1
            if key == 'Received':
                address = re.search('(\d{1,3}\.){3}\d{1,3}',mail[key]).group()
                if address != '127.0.0.1':
                    data_set[file_name].ip_address += ' ' + address
                        
            #2.) Matching degree of domain names between Message-Id and (Received/From ??) field (Easy just read and compare)
                        
            #3.) Subject (Easy just read it)          
            if key == 'Subject':
                data_set[file_name].subject = mail[key]
                
            #4.) Name from the From field (Easy just read it)
            if key == 'From':
                data_set[file_name].name = mail[key]
                
            #9.) SPAM word ratio 
            #10.) SPAM degree as by equation in paper 
            w1 = 50 / 51.0
            w2 = 1 / 51.0
        
        #5.) Content type (Easy just read it)
        data_set[file_name].type_HTML = get_type_content(mail)
        #6.) Attachments: none, text, or non-text 
        data_set[file_name].attachments = get_type_attachments(mail)
        #7.) Number of URLs present 
        urls = re.findall( \
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', \
                    get_message_body(mail))
        data_set[file_name].num_urls = len(urls)
        #8.) URL ratio (% of message body that is URLs)
        length = (get_message_len(mail) * 1.0)
        data_set[file_name].percent_urls = len(''.join(urls)) / length
        #11.) Classification label: Spam or Ham
        if file_name.startswith('ham'):
            data_set[file_name].spam = 1
        else:
            data_set[file_name].spam = 2
      
    for key in data_set.keys():
        print data_set[key].stringFile()
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
