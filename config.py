# -*- coding: utf-8 -*-
"""
Created on Wed May 25 10:18:39 2016

@author: wolf

Nothing on this page is really used (though it should have been used a lot more, 
bad practice on my part). The only relavent thing is the UPLOAD_PATHS list which
holds the entire path to where your computer will be able to upload fasta files
to BLISTR via the upload home page.
"""


import os
#basedir = os.path.abspath(os.path.dirname(__file__))

#using these ridiculus cappitalized names is actually very important for SQL, so be sure to name them as shown for future databases
SQLALCHEMY_DATABASE_URI = 'postgresql://wolf:Halflife3@localhost:5432/BLISTR.db'          #/' + os.path.join(basedir, 'BLISTR.db') #path of database file
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository') #where we will store the SQLAlchemy-migrate data files

#WTF_CSRF_ENABLED = True #activates the cross-site request forgery prevention #security
SECRET_KEY = 'you-will-never-guess' #your super encription to protect from malicious edits from outside users
#for products you will actually put online, you want this secretKey to be steadfast

#The follwoing list is all of the allowed paths which an upload file may be held in. If you need to add an allowed path, feel free to add it to this list
UPLOAD_PATHS = ['PATH/TO/ROOT/fasta_files/', '/home/wolf/Desktop/OWEN/Test_fastas/']


"""
#mail server setting, to receive user error messages
MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None #nede to put in your actual email credentials to receive email
MAIL_PASSWORD = None

#for pagination
POSTS_PER_PAGE = 3

#flask-whooshalchemy global variable (for searching)
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

#administrator list
ADMINS = ['owenneuber@yahoo.com']
"""