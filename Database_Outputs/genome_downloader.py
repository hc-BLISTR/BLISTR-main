# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 10:02:44 2016

@author: Owen Neuber

program to take a string input of numbers separated by dashes (i.e. 2-3-4-1)
and extract those numbers. Those numbers represent the genome.id numbers
that a BLISTR user would like to download. This program will then download 
the contig files of all the corresponding genomes to the directory:
PATH/TO/DOWNLOADS/ with the filename corresponding to the genome's name
in the database (i.e. DFPST0008).

The file types to be downloaded (see parser.add_argurents for detals) are indicated
by the flags this program receives (which are based off of those check boxes in
the BLISTR app). It is views.py that calls this program with the needed flags.
"""

import re
from sqlalchemy.orm import sessionmaker
from models import Genome, GeographicLocation, Contig, Toxin, Prokka, S_16
from sqlalchemy import create_engine
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("list", help="The list of genome id numbers to be processed in the form of 2-3-4-1, where the '-' represents a comma in a list")
parser.add_argument("--con", "-c", help= "This flag is includeed if the user wants to download the contig file", action="store_true")
parser.add_argument("--toxin", "-t", help= "This flag is includeed if the user wants to download the toxin file", action="store_true")
parser.add_argument("--toxin_extra", "-e", help= "This flag is includeed if the user wants to download the toxin++ file", action="store_true")
parser.add_argument("--sixteen_s", "-s", help= "This flag is includeed if the user wants to download the 16S sequence", action="store_true")
parser.add_argument("--ffaa", help= "This flag is includeed if the user wants to download the fasta faa file", action="store_true")
parser.add_argument("--fffn", help= "This flag is includeed if the user wants to download the fasta ffn file", action="store_true")
parser.add_argument("--tfaa", help= "This flag is includeed if the user wants to download the toxin faa file", action="store_true")
parser.add_argument("--tffn", help= "This flag is includeed if the user wants to download the toxin ffn file", action="store_true")
args = parser.parse_args() 

genome_ids = args.list.split("-")

engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session/allow session.add()
session = Session()
path = "PATH/TO/DOWNLOADS/"

for g_id in genome_ids:
    g_id = int(g_id) #gotta convert thaat string input to an int!
    g = session.query(Genome).filter_by(id=g_id).first() #our basic genome query form
    geo = session.query(GeographicLocation).filter_by(genome_id=g_id).first() #our basic geographic location query form
    toxins = session.query(Toxin).filter_by(genome_id=g_id).all() #all incase we have multiple toxins and thus this is in list format
    pro = session.query(Prokka).filter_by(genome_id=g_id).first() #for use with Genome faa and ffn
    mulit_pro = session.query(Prokka).filter_by(genome_id=g_id).all() #for use with the toxin faa and ffn (in case of multi toxin)
    sixteen = session.query(S_16).filter_by(genome_id=g_id).first()
    
    if args.con:
        fasta = open(path+g.name+".fasta", 'w')
        contigs = session.query(Contig).filter_by(genome_id=g_id).order_by(Contig.contig_number).all() #list of all the query forms that hold a contig. Without the order_by, the contigs would show up in random order
        for contig in contigs: #run this for every contig in the database for the specific genome
            fasta.write(">"+str(contig.contig_number)+","+str(g.name)+","+str(g.author)+","+str(g.collection_date)+","+str(g.clinical_or_environmental) \
                +","+str(g.source_info)+","+str(g.institution)+","+str(geo.lat)+","+str(geo.lng)+","+str(geo.country)+","+str(geo.region).rstrip("\n")+"\n"
            ) #every contig header
            fasta.write(re.sub("(.{60})", "\\1\n", contig.seq, 0, re.DOTALL)) #this fancy line just writes the contig files out with an newline every 60 characters
            fasta.write("\n")
        fasta.close()
    
    if args.toxin:
        toxin = open(path+g.name+".toxin.fasta", 'w')
        counter = 0
        for tox in toxins: #run for all toxins (even if there is just one)
            if tox == None:
                toxin.write("No Toxin found")
            else:
                if counter > 0: #if there is more than one toxin, add an endline before the next one
                    toxin.write("\n")
                toxin.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+","+str(tox.best_hit)+"\n") #a nifty header for the toxin
                output = tox.seq[tox.bp_before:-tox.bp_after] #removes the extra base pairs we added to the toxin beforehand. The after needs to have a minus otherwise it will not take from the end of the string
                toxin.write(re.sub("(.{60})", "\\1\n", str(output), 0, re.DOTALL))
                counter +=1
        toxin.close()
    
    if args.toxin_extra:
        toxin_extra = open(path+g.name+".toxin++.fasta", 'w')
        counter = 0
        for tox in toxins:
            if tox == None:
                toxin_extra.write("No Toxin found")
            else:
                if counter > 0:
                    toxin_extra.write("\n")
                toxin_extra.write(">"+str(g.name)+",From contig number: "+str(tox.contig.contig_number)+",Base pairs before/after toxin: "+str(tox.bp_before)+"/"+str(tox.bp_after)+","+str(tox.best_hit)+"\n")
                toxin_extra.write(re.sub("(.{60})", "\\1\n", tox.seq, 0, re.DOTALL))
                counter += 1
        toxin_extra.close()
        
    if args.ffaa:
        ffaa = open(path+g.name+".faa", 'w')
        ffaa.write(str(pro.fasta_faa)) #this one liner input already has its \n's for formmatting so the outputted files should be perfect
        ffaa.close()
    
    if args.fffn:
        fffn = open(path+g.name+".ffn", 'w')
        fffn.write(str(pro.fasta_ffn)) 
        fffn.close()
        
    if args.tfaa: 
        counter = ""
        for pro in mulit_pro:
            tfaa = open(path+g.name+".toxin"+str(counter)+".faa", 'w')
            if pro.tox_faa == None:
                tfaa.write("No Toxin found")
            else:
                tfaa.write(str(pro.tox_faa)) 
            tfaa.close()
            if type(counter) == int: #setting up labling such that the first output does not have a number appended to it but then all following outputs, if exists, will
                counter += 1
            else:
                counter = 2
        
    if args.tffn:
        counter = ""
        for pro in mulit_pro:
            tffn = open(path+g.name+".toxin"+str(counter)+".ffn", 'w')
            if pro.tox_ffn == None:
                tffn.write("No Toxin found")
            else:
                tffn.write(str(pro.tox_ffn)) 
            tffn.close()
            if type(counter) == int: 
                counter += 1
            else:
                counter = 2
                
    if args.sixteen_s:
        Sx = open(path+g.name+".16S.fasta", 'w')
        if sixteen.seq:
            Sx.write(">"+str(g.name)+"\n"+re.sub("(.{60})", "\\1\n", str(sixteen.seq), 0, re.DOTALL))
        else:
            Sx.write("No 16S data")
        Sx.close()