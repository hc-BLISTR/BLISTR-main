# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 07:27:22 2016

@author: Owen Neuber

Program that takes the most recent addition to the BLISTR.db database (i.e. the 
entry with the largest genome.id number) and extracts all the useful information 
from the database about that genome and creates uses that information to create 
a TSV file. The TVS file will be given the path:
wolf/Desktop/BLISTR_outputs.
Should the user use BLISTR's search function in tandom with export to TSV, then
every search result will have its data exported to the TSV file.
The output file name will be of the form: genome_name.BLISTR.tsv
"""
#TODO: fix up the bit where we pick out the group and toxin type
from sqlalchemy.orm import sessionmaker
from models import Genome, GeographicLocation, Toxin, Searches#, FlaA, FlaB
from sqlalchemy.sql.expression import func
from sqlalchemy import create_engine

engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session/allow session.add()
session = Session()

last_search = session.query(func.max(Searches.id)).scalar() #largest search id number
if last_search and not session.query(Searches).filter_by(id=last_search).first().searched_for: #if there is a search recorded in the database and the last search has searched_for set to False then we know the user used the search function, not the upload function
    g_ids = session.query(Searches).filter_by(id=last_search).first().g_ids.split("-")
else:
    g_ids = [session.query(func.max(Genome.id)).scalar()] #the most recently added genome's id number (the user must have just uploade if we are not using the search). Turing it into a list to make it work with n number (even though there will only ever be one)
    
for g_id in g_ids:
    g = session.query(Genome).filter_by(id=g_id).first() #our basic genome query form
    g_name = str(g.name) #got to make sure this is not in unicode
    geo = session.query(GeographicLocation).filter_by(genome_id=g_id).first() #our basic geographic location query form
    tox = session.query(Toxin).filter_by(genome_id=g_id).all()
    #TODO: add in flaA & B versions of tox
    
    out_file = open('PATH/TO/DOWNLOADS/'+g_name+'.BLISTR.tsv', 'w')
    
    g_type = "" #setting default genome type
    
    for toxin in tox:
        g_type += toxin.best_hit + ", " #puts all the toxins on the same line
    g_type = g_type.rstrip(", ") #take away the extra comma
    
    #Set up to extract allthe QUAST data from its dictionary format
    quast = g.quality_stats
    quast_metadata = quast.keys()
    data = quast.values()
    quast_data = []#initializing an empty list for metadata to be added to
    for dirt in data: #the reason I'm doing this is to remove a newline which is at the end of each data entry
        quast_data.append(dirt.rstrip("\n"))
    toxin_data = []
    for toxin in tox:
        toxin_data.append("Toxin") #make as many of these as we have toxins
        toxin_data.append("bp before toxin")
        toxin_data.append("bp after toxin")
        toxin_data.append("Toxin sequence")
    
    #TODO: add flagellen stuff to both of these
    input_metadata = [["Genome name", "Toxins", "Collection date", "Source type", \
        "Source information", "Institution", "Author"], quast_metadata, ["Lat/Long", "Country", "Region", \
        ], toxin_data
    ]    
    input_metadata = [item for sublist in input_metadata for item in sublist] #fancy way to flatten our nested list
    
    toxin_data = []
    for toxin in tox:
        if toxin == None: #if there is no toxin entry in the database
            best_hit, bp_before, bp_after, seq = [None]*4
        else: #otherwise, output what the terms should be
           best_hit, bp_before, bp_after, seq = toxin.best_hit, toxin.bp_before, toxin.bp_after, toxin.seq
        toxin_data.append(best_hit)
        toxin_data.append(bp_before)
        toxin_data.append(bp_after)
        toxin_data.append(seq)
          
    
    input_data = [[g.name, g_type, g.collection_date, g.clinical_or_environmental, \
        g.source_info, g.institution, g.author], quast_data, [geo.lat+"/"+geo.lng, geo.country, \
        geo.region.rstrip("\n")], toxin_data
    ]
    
    input_data = [item for sublist in input_data for item in sublist]
    
    counter = 0 #setting up a counte to keep  data and metadata parallel
    
    for metadata in input_metadata:
        out_file.write(str(metadata) +"\t"+ str(input_data[counter]) +"\n") #output our data enmass to our new file
        counter += 1
    out_file.close() #and now we are done