# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 12:38:47 2016

@author: Owen Neuber

This program will make three temparary files in the PATH/TO/ROOT/static/
directory. NOTE: they must be in the static folder, else flask cannot render them.
The files to be made are:
1. temp.fasta -> entire fasta file of genome being rendered
2. temptoxin.fasta -> the toxin, all by itself, excluding its extra base pairs added to it
3. temptoxin++.fasta -> the toxin gene plus more things!!!

Now, in the instance of a search, this will be run n number of times and thus the naming
scheme is as above with a number before the .fasta (i.e. temp1.fasta)
"""

import re
from sqlalchemy.orm import sessionmaker
from models import Genome, GeographicLocation, Contig, Toxin, Searches#, FlaA, FlaB
from sqlalchemy.sql.expression import func
from sqlalchemy import create_engine

engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session/allow session.add()
session = Session()
temp_path = 'PATH/TO/ROOT/static/temp/'

last_search = session.query(func.max(Searches.id)).scalar() #largest search id number
if last_search and not session.query(Searches).filter_by(id=last_search).first().searched_for: #if there is a search recorded in the database and the last search has searched_for set to False
    g_ids = session.query(Searches).filter_by(id=last_search).first().g_ids.split("-")
    counter = 0 # counter for naming purposes
    for g_id in g_ids:
        counter += 1
        g = session.query(Genome).filter_by(id=g_id).first() #our basic genome query form
        geo = session.query(GeographicLocation).filter_by(genome_id=g_id).first() #our basic geographic location query form
        toxins = session.query(Toxin).filter_by(genome_id=g_id).all()
        
        ###############################################################################
        #Step 1        
        contigs = session.query(Contig).filter_by(genome_id=g_id).order_by(Contig.contig_number).all() #list of all the query forms that hold a contig. Without the order_by, the contigs would show up in random order
        fasta = open(temp_path+"temp"+str(counter)+".fasta", 'w')
        for contig in contigs: #run this for every contig in the database for the specific genome
            fasta.write(">"+str(contig.contig_number)+","+str(g.name)+","+str(g.author)+","+str(g.collection_date)+","+str(g.clinical_or_environmental) \
                +","+str(g.source_info)+","+str(g.institution)+","+str(geo.lat)+","+str(geo.lng)+","+str(geo.country)+","+str(geo.region).rstrip("\n")+"\n"
            ) #every contig header
            fasta.write(re.sub("(.{60})", "\\1\n", contig.seq, 0, re.DOTALL)) #this fancy line just writes the contig files out with an newline every 60 characters
            fasta.write("\n")
        fasta.close()
        ###############################################################################
        #Step 2       
        toxin = open(temp_path+"temptoxin"+str(counter)+".fasta", 'w')
        for tox in toxins:
            if tox == None:
                toxin.write("No Toxin found")
            else:
                toxin.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+","+str(tox.best_hit)+"\n") #a nifty header for the toxin
                output = tox.seq[tox.bp_before:-tox.bp_after] #removes the extra base pairs we added to the toxin beforehand. The after needs to have a minus otherwise it will not take from the end of the string
                toxin.write(re.sub("(.{60})", "\\1\n", str(output), 0, re.DOTALL))
                toxin.write("\n")
        toxin.close()
        ###############################################################################
        #Step 3       
        toxin_extra = open(temp_path+"temptoxin++"+str(counter)+".fasta", 'w')
        for tox in toxins:
            if tox == None:
                toxin_extra.write("No Toxin found")
            else:
                toxin_extra.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+",Base pairs before/after toxin: "+str(tox.bp_before)+"/"+str(tox.bp_after)+","+str(tox.best_hit)+"\n")
                toxin_extra.write(re.sub("(.{60})", "\\1\n", tox.seq, 0, re.DOTALL))
                toxin_extra.write("\n") #need that new line for multi fasta files
        toxin_extra.close()
    
    #If a genome was uploaded instead of searched for
else:
    counter = 1 #every file's defualt name will be temp1.fasta (or similar)
    g_id = session.query(func.max(Genome.id)).scalar() #the most recently added genome's id number
    g = session.query(Genome).filter_by(id=g_id).first() #our basic genome query form
    geo = session.query(GeographicLocation).filter_by(genome_id=g_id).first() #our basic geographic location query form
    toxins = session.query(Toxin).filter_by(genome_id=g_id).all()
    
    ###############################################################################
    #Step 1
    #I am using the paragraph tag (<p>) and <br> to create a newline every 60 chracters and a paragraph every contig
    contigs = session.query(Contig).filter_by(genome_id=g_id).order_by(Contig.contig_number).all() #list of all the query forms that hold a contig. Without the order_by, the contigs would show up in random order
        
    fasta = open(temp_path+"temp"+str(counter)+".fasta", 'w')
    for contig in contigs: #run this for every contig in the database for the specific genome
        fasta.write(">"+str(contig.contig_number)+","+str(g.name)+","+str(g.author)+","+str(g.collection_date)+","+str(g.clinical_or_environmental) \
            +","+str(g.source_info)+","+str(g.institution)+","+str(geo.lat)+","+str(geo.lng)+","+str(geo.country)+","+str(geo.region).rstrip("\n")+"\n"
        ) #every contig header
        fasta.write(re.sub("(.{60})", "\\1\n", contig.seq, 0, re.DOTALL)) #this fancy line just writes the contig files out with an newline every 60 characters
        fasta.write("\n")
    fasta.close()
    ###############################################################################
    #Step 2
    toxin = open(temp_path+"temptoxin"+str(counter)+".fasta", 'w')
    for tox in toxins:
        if tox == None:
            toxin.write("No Toxin found")
        else:
            toxin.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+","+str(tox.best_hit)+"\n") #a nifty header for the toxin
            output = tox.seq[tox.bp_before:-tox.bp_after] #removes the extra base pairs we added to the toxin beforehand. The after needs to have a minus otherwise it will not take from the end of the string
            toxin.write(re.sub("(.{60})", "\\1\n", str(output), 0, re.DOTALL))
            toxin.write("\n")
    toxin.close()
    ###############################################################################
    #Step 3
    toxin_extra = open(temp_path+"temptoxin++"+str(counter)+".fasta", 'w')
    for tox in toxins:
        if tox == None:
            toxin_extra.write("No Toxin found")
        else:
            toxin_extra.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+",Base pairs before/after toxin: "+str(tox.bp_before)+"/"+str(tox.bp_after)+","+str(tox.best_hit)+"\n")
            toxin_extra.write(re.sub("(.{60})", "\\1\n", tox.seq, 0, re.DOTALL))
            toxin_extra.write("\n")
    toxin_extra.close()


"""
for contig in contigs: #run this for every contig in the database for the specific genome
    fasta.write("<p>>"+str(contig.contig_number)+","+str(g.name)+","+str(g.author)+","+str(g.collection_date)+","+str(g.clinical_or_environmental) \
        +","+str(g.source_info)+","+str(g.institution)+","+str(geo.lat)+","+str(geo.lng)+","+str(geo.country)+","+str(geo.region)+"<br>"
    ) #every contig header
    fasta.write(re.sub("(.{60})", "\\1<br>", contig.seq, 0, re.DOTALL)) #this fancy line just writes the contig files out with an newline every 60 characters
    fasta.write("</p>")
fasta.write('{% endblock %}')
fasta.close() #and, of course, you cant forget to close the file

toxin = open(path+"toxin.html", 'w')
toxin.write('{% extends "base.html" %}{% block content %}')
if tox == None:
    toxin.write("No Toxin found")
else:
    toxin.write("<p>>"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+"<br>") #a nifty header for the toxin
    output = tox.seq[tox.bp_before:-tox.bp_after] #removes the extra base pairs we added to the toxin beforehand. The after needs to have a minus otherwise it will not take from the end of the string
    toxin.write(re.sub("(.{60})", "\\1<br>", str(output), 0, re.DOTALL))
    toxin.write("</p>")
toxin.write('{% endblock %}')
toxin.close()

toxin_extra = open(path+"toxin_extra.html", 'w')
toxin_extra.write('{% extends "base.html" %}{% block content %}')
if tox == None:
    toxin_extra.write("No Toxin found")
else:
    toxin_extra.write("<p>>"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+",Base pairs before/after toxin: "+str(tox.bp_before)+"/"+str(tox.bp_after)+"<br>")
    toxin_extra.write(re.sub("(.{60})", "\\1<br>", tox.seq, 0, re.DOTALL))
    toxin_extra.write("</p>")
toxin_extra.write('{% endblock %}')
toxin_extra.close()
"""