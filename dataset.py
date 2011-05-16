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
import random, string, email, re, hashlib
import nltk, nltk.corpus

class DataMember:
    """Defines a line in the dataset"""
    def __init__(self):
        self.ip_address = 0
        self.ip_address_str = ''
        self.degree_domains_match = 0.0
        self.subject = 0
        self.subject_str = ''
        self.from_name = 0
        self.from_name_str = ''
        #type is 1 for HTML, 2 for text, 3 for mixed
        self.type_HTML = 1
        #1 for no attachments, 2 for text attachments, 3 for non-text attachments, 4 for mixed
        self.attachments = 1
        self.num_urls = 0
        self.percent_urls = 0.0
        self.percent_spam = 0.0
        self.degree_spam = 0.0
        #1 for ham, 2 for spam
        self.spam = 1
    
    def __str__(self):
        format = '(%s|%s|%s|%s|%s|%s|%s|%% urls %s|%% spam %s|Degree %s|Spam? %s)'
        return self._print(format)
    
    def file_out(self):
        seperator = ', '
        format = '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + '%s'
        return self._print(format)
    
    def _print(self, format):
        return format % \
            (self.ip_address,           \
            self.degree_domains_match,  \
            self.subject,               \
            self.from_name,             \
            self.type_HTML,             \
            self.attachments,           \
            self.num_urls,              \
            self.percent_urls,          \
            self.percent_spam,          \
            self.degree_spam,           \
            self.spam)    
    
    def file_test_out(self):
        output = ''
        seperator = ', '
        format = '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + \
                 '%s' + seperator + '%s' + seperator + '?'
        output = format % \
                     (self.ip_address,           \
                     self.degree_domains_match,  \
                     self.subject,               \
                     self.from_name,             \
                     self.type_HTML,             \
                     self.attachments,           \
                     self.num_urls,              \
                     self.percent_urls,          \
                     self.percent_spam,          \
                     self.degree_spam)
        return output
    

def get_message_body(mail):
    text = ''
    if not mail.is_multipart():
        text = re.sub('(=\r\n)|(=[\\da-fA-F]{2})','', mail.get_payload())
        text = re.sub('[\r\n]',' ', text)
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


def word_count_dict(home_dir, dir, percent = 0.1):
    """Returns a word/count dict for this directory."""
    word_count = {}
    file_list = os.listdir(home_dir + dir)
    count = len(file_list)
    num_samples = max(1, int(count * percent))
    sample_files = []
        
    #Sample x% of all files to build this thesaurus 
    if dir.find('ham') != -1:
        for file in file_list:
            sample_files.append(file);
    else:
        for n in range(num_samples):
            index =  int(random.uniform(0,count))
            #Ensure all items are unique
            while file_list[index] in sample_files:
                index =  int(random.uniform(0,count))
                
            sample_files.append( file_list[index] )
        
    #Load the list of words to ignore (optional)
    if os.path.isfile(home_dir + 'ignore.txt'):
        ignore_file = open(home_dir + 'ignore.txt', 'r')
        ignore = nltk.word_tokenize(ignore_file.read())
        ignore_file.close()
    else:
        ignore_file = []
        
    for file_name in sample_files:
        #Ignore files that start with .
        if file_name[0] == '.' or os.path.isdir(home_dir + dir + '/' + file_name) or \
            os.path.islink(home_dir + dir + '/' + file_name):
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
    """Find the words that occur in only 1 spam message"""
    unique = {}
    file = open(home_dir + 'spamOnly.txt','w')
    for word in sorted(spam, key = spam.get):
        if spam[word] == 1 and word not in ham:
            unique[word] = spam[word]
            file.write(word + ' ' + str(spam[word]) + '\n')        
    file.close()
    return unique


def build_dataset(data_set, home_dir, dir, unique_spam, spam_top_50):
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
    for file_name in file_list:
        data_set[file_name] = DataMember()
        #Ignore files that start with .
        if file_name[0] == '.' or os.path.isdir(home_dir + dir + '/' + file_name) or \
            os.path.islink(home_dir + dir + '/' + file_name):
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
                    data_set[file_name].ip_address_str += address + ' '
                        
            #3.) Subject (Easy just read it)          
            if key == 'Subject':
                data_set[file_name].subject_str = repr(mail[key])[1:-1]
                
            #4.) Name from the From field (Easy just read it)
            if key == 'From':
                data_set[file_name].from_name_str = repr(mail[key])[1:-1]
        
        #2.) Matching degree of domain names between Message-Id and (Received/From ??) field (Easy just read and compare)
        if mail['From'] != None:
            from_domain = re.search('@[\[\]\w+\.]+', mail['From'])
        else:
            from_domain = None;
        if str(from_domain) != 'None':
            from_domain = from_domain.group()[1:]
        else:
            #Non-ascii domain name, pull out the hex encoding
            from_domain = repr(mail['From']).replace('\\x','')
            if from_domain.find('@') == -1:
                from_domain = ' '
            else:
                from_domain = re.search('@[\[\]\w+\.]+', from_domain).group()[1:]
        message_domain = re.search('@[\[\]\w+\.]+',mail['Message-ID'])
        if str(message_domain) != 'None':
            message_domain = message_domain.group()[1:]
        else:
            #Non-ascii domain name, pull out the hex encoding
            message_domain = repr(mail['Message-ID']).replace('\\x','')
            message_domain = repr(mail['Message-ID']).replace('%','')
            if message_domain.find('@') == -1:
                message_domain = ' '
            else:
                message_domain = re.search('@[\[\]\w+\.]+', message_domain).group()[1:]
                
        distance = nltk.edit_distance(from_domain, message_domain)
        domain_len = max(len(from_domain), len(message_domain), 1) * 1.0
        
        data_set[file_name].degree_domains_match = 1.0 - distance / domain_len
                
        #Get the length of the message and the text
        length = (get_message_len(mail) * 1.0)
        body = get_message_body(mail)

        #5.) Content type (Easy just read it)
        data_set[file_name].type_HTML = get_type_content(mail)
        #6.) Attachments: none, text, or non-text 
        data_set[file_name].attachments = get_type_attachments(mail)
        #7.) Number of URLs present 
        urls = re.findall( \
                    'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', \
                    body)
        data_set[file_name].num_urls = len(urls)
        
        #8.) URL ratio (% of message body that is URLs)
        data_set[file_name].percent_urls = len(''.join(urls)) / length
        
        #9.) SPAM word ratio 
        #10.) SPAM degree as by equation in paper 
        spam_count = 0
        w1 = 50 / 51.0
        w2 = 1 / 51.0
        freq_spam = 0.0
        s1 = 0.0
        s2 = 0
        
        body = nltk.clean_html(body)
        words = nltk.word_tokenize(body)
        word_count = max(1, len(words)) #Don't allow divide by zero
        for word in nltk.word_tokenize(body):
            if word in unique_spam:
                #Must be SPAM
                s2 = 1
                spam_count += 1
            elif word in spam_top_50:
                freq_spam += 1.0
                spam_count += 1
                        
        s1 = freq_spam / word_count
        
        data_set[file_name].percent_spam = spam_count / length
        data_set[file_name].degree_spam = w1 * s1 + w2 * s2
        
        #11.) Classification label: Spam or Ham
        if file_name.startswith('ham'):
            data_set[file_name].spam = 1
        else:
            data_set[file_name].spam = 2
        #Fields that need to be md5 encoded are: IP address, Subject, and from        
        ip_address_md5 = hashlib.md5()
        ip_address_md5.update(data_set[file_name].ip_address_str)
        data_set[file_name].ip_address = int(ip_address_md5.hexdigest(),16)
        
        subject_md5 = hashlib.md5()
        subject_md5.update(data_set[file_name].subject_str)
        data_set[file_name].subject = int(subject_md5.hexdigest(),16) 
        
        from_name_md5 = hashlib.md5()
        from_name_md5.update(data_set[file_name].from_name_str)
        data_set[file_name].from_name = int(from_name_md5.hexdigest(),16) 

    #for key in data_set.keys():
    #    print data_set[key]
    return data_set
    #Repeat for ham files


def main():
    if len(sys.argv) != 5:
        print 'usage: ./dataset.py home_dir ham_dir spam_dir %_to_sample'
        sys.exit(1)
    home_dir = sys.argv[1]
    ham_dir =  sys.argv[2]
    spam_dir = sys.argv[3]
    sample_size = int(sys.argv[4]) / 100.0 # as a %
    #Sample ham and spam, don't use the entire corpus
    ham_word_count, ham_top_50 = build_thesaurus(home_dir, ham_dir, 1.0) #Check against all ham files
    spam_word_count, spam_top_50 = build_thesaurus(home_dir, spam_dir, sample_size)  
    unique_spam = spam_unique(home_dir, ham_word_count, spam_word_count) #Appears in only a single SPAM
    
    spam_data_set = {}
    spam_data_set = build_dataset(spam_data_set, home_dir, spam_dir, unique_spam, spam_top_50)
    ham_data_set = {}
    ham_data_set = build_dataset(ham_data_set, home_dir, ham_dir, unique_spam, spam_top_50)
    
    header ="""% 1. Title: Spam Classification Decision Tree
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

"""

    data_set_arff = open(home_dir + 'dataset.arff', 'w')
    data_set_arff.write(header)
    
    for key in spam_data_set.keys():
        data_set_arff.write(spam_data_set[key].file_out() + '\n')
    
    for key in ham_data_set.keys():
        data_set_arff.write(ham_data_set[key].file_out() + '\r\n')

    data_set_arff.close()
    
if __name__ == '__main__':
    main()
