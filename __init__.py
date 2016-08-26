# -*- coding: utf-8 -*-
"""
Created on Wed May 25 10:16:12 2016

@author: Owen Neuber

Old init file. Not sure of all its functionallity but it is important. Just here
to keep things schwifty.
"""

#import os
#from config import  basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy




BLISTR = Flask(__name__)
BLISTR.config.from_object('config') #tells flask to read and use the configure file
db = SQLAlchemy(BLISTR) #our database

#from BLISTR import models, views
