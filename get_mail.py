#!/usr/bin/python -tt

#Created on 03/11/2011
#Grabs all spam and ham from a gmail account for yesterday's email.

#Modified 03/11/2011
#Modified by Joshua Olson
#Added support for multiple email accounts (Gmail only as of now)
#Added support for specific date grabs

"""
Joshua Olson 
Copyright 2010
This script reads an IMAP email account for spam and ham on a given day

Right now the spam and ham folders are expected to be [Gmail]/All Mail and [Gmail]/Spam respectively

"""
import email, getpass, imaplib, os, sys, string
from datetime import date, datetime, timedelta

def main():
    home_dir = sys.argv[0][:-11]
    ham_dir = home_dir + 'ham' # directory to store ham
    spam_dir = home_dir + 'spam' # directory to store spam

    args = len(sys.argv)
    in_text_format = '%m/%d/%Y' #Accept a date in the format MM/DD/YYYY
    when = date.today() - timedelta(1) #Default to yesterday
    imap = 'imap.gmail.com'
    
    if args > 1:
        option  = sys.argv[1] #This can be either the --h mm/dd/yyyy or a username 

        if option == '--h':
            print """Usage: ./get_mail.py [date] [username password [imap_server]]
            --h displays usage information"""
            sys.exit(1)
        elif option[0] in string.digits:
            when = datetime.strptime(option, in_text_format)

            if args > 2:
                user = sys.argv[2]
                pwd = sys.argv[3]
                if args == 5:
                    imap = sys.argv[4]
                
        else:
            user = sys.argv[1]
            pwd = sys.argv[2]
            if args == 4:
                imap = sys.argv[3]
            
    else:   #Default settings
       user = raw_input("Enter your username:")
       pwd  = getpass.getpass("Enter your password:")

    grabDate = when.strftime("%d-%b-%Y") #Get yesterday's date (03-Mar-2011)
    grabDate2 = when.strftime("%d-%m-%Y") #Get yesterday's date (03-03-2011)        

    # connecting to the gmail imap server
    m = imaplib.IMAP4_SSL(imap)
    
    login = True
    while login:
        try:
            m.login(user,pwd)
            login = False
        except m.error:
            print 'Error on login\n'
            user = raw_input("Enter your username:")
            pwd = getpass.getpass("Enter your password: ")

    m.select("[Gmail]/All Mail") # here you a can choose a mail box like INBOX instead
    #for folder in m.list() iterate though each folder to find mail for a general IMAP account
    
    resp, items = m.search(None,'ON', grabDate) # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
    hamIDs = items[0].split() # getting the mails id

    for emailid in hamIDs:
        filename = 'ham' + '_' + grabDate2 + '_' + str(emailid).zfill(3) + '_' + user + '.txt'
        att_path = os.path.join(ham_dir, filename)

        #Check if its already there
        if not os.path.isfile(att_path) :
            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            # finally write the stuff
            fp = open(att_path, 'wb')
            fp.write(email_body)
            fp.close()

    m.select("[Gmail]/Spam")
    resp, items = m.search(None,'ON', grabDate) 
    spamIDs = items[0].split() 

    for emailid in spamIDs:
        filename = 'spam' + '_' + grabDate2 + '_' + str(emailid).zfill(3) + '_' + user + '.txt'
        att_path = os.path.join(spam_dir, filename)
            
        #Check if its already there
        if not os.path.isfile(att_path) :
            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            
            # finally write the stuff
            fp = open(att_path, 'wb')
            fp.write(email_body)
            fp.close()
            
    m.close()
    m.logout()

if __name__ == '__main__':
  main()