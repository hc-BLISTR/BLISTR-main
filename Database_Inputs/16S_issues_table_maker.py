# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:14:24 2016

@author: Owen Nuber

Program to create a .xlsx file holding metadata about uploads that had 16S
issues. A poor man's version of metadata_table_maker.py
"""

import xlsxwriter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Genome, GeographicLocation, Toxin, S_16#, FlaA, FlaB

engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
session = Session()

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook('PATH/TO/ROOT/Database_Inputs/16S_issues.xlsx')
worksheet = workbook.add_worksheet()
bold = workbook.add_format({'bold': 1}) #allowing bold wording because why not

#TODO: add flagellen stuff
#TODO: add quality stats and toxin type/group to headers (do this after you get the rest of this program working)
headers = ["Check boxes", "Genome name", "16S issue", "Collection date", "Source type", "Source information", "Institution", "Author", "Toxin", "SubType", "bp before toxin", "bp after toxin", "Lat/Long", "Country", "Region"]
letter = "a"
for col in headers: #adding all the headers to the file
    worksheet.write(letter.upper()+'1', col, bold) #sets the cell postion (i.e. A1, B1, C1 etc.) and makes the header bold
    letter = ''.join([chr(((ord(x)-ord('a')+1)%26)+ord('a')) for x in letter]) #wizard one linner that will increase the letter value of letter (i.e 'a' -> 'b')
    
g_list = session.query(Genome).order_by(Genome.id.asc()).all() #list of all the genomes in the database (in order of id)
row = 1 #initializing counter to keep track of row number
for g in g_list: #filling through all the genomes in the database. g can also be seen as a row in terms of the spreadsheet
    if session.query(S_16).filter_by(id=g.id).first().error == None: #if there is no error, carry on
        continue
    sub_type=str(g.sub_type)
    toxins = session.query(Toxin).filter_by(genome_id=g.id).all() #toxin data that corresponds to the genome in question
    geo = session.query(GeographicLocation).filter_by(genome_id=g.id).first()
    #The following is just some annoying cleanup incase there are not toxin entries for a genome
    t_meta, bp_before, bp_after = [""]*3 #If there was not toxin input, give these values None
    for tox in toxins:
        if tox != None: 
           t_meta=t_meta+tox.best_hit+", " #If there was a toxin input, give the outputs their proper values
           bp_before=bp_before+str(tox.bp_before)+", "
           bp_after=bp_after+str(tox.bp_after)+", "
    t_meta, bp_before, bp_after = t_meta.rstrip(", "), bp_before.rstrip(", "), bp_after.rstrip(", ")
       
    #Metadata is a list with values that correspond to the values in the list 'headers'
    metadata = [g.name, session.query(S_16).filter_by(id=g.id).first().error, g.collection_date, g.clinical_or_environmental, g.source_info, g.institution, g.author, t_meta, sub_type, bp_before, bp_after, str(geo.lat)[:6]+"/"+str(geo.lng)[:6], geo.country, geo.region.rstrip("\n")]
    letter = "b" #'b' because 'a' is reserved for check boxes
    row += 1 #row starts at 2 and increases from there
    check_box = "<input type=checkbox name=check value="+str(g.id)+">" #the html/jninja required to make a check box, synced to the genome id. All check boxes have the name 'check' which makes for an easy 'select all' box
    worksheet.write("A"+str(row), check_box)
    for col in metadata:
        worksheet.write(letter.upper()+str(row), col)
        letter = ''.join([chr(((ord(x)-ord('a')+1)%26)+ord('a')) for x in letter])


workbook.close()