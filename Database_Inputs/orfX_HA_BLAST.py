# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 14:53:25 2016

@author: Owen Neuber

A Cheap knock off of orfX_HA_BLAST.py as seen in Database_Creation. For more 
information in the docstring, just go there.
"""


import os
import subprocess
import glob
from blessings import Terminal
from shutil import rmtree

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
parser.add_argument("--clean", "-c", help="orders the program to remove the toxin prokka folders after running", action="store_true")
args = parser.parse_args()
URL = args.URL

colours = Terminal() #for terminal outputs with gorgeous colours!


database = "PATH/TO/ROOT/fasta_files/databases/orfX_HA_db/orfX_HA_NTNH_proteinDB.faa"
out_dir = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/'

LENSLEN = 0.90
PIDENT = 90.0


folder_name = os.path.basename(URL)[:-6] #removes the path and .fasta from the folder name
folder = 'PATH/TO/ROOT/fasta_files/PROKKA/tox/'+folder_name #path to the toxin folder
folders = [folder + "/"] #formating it so that if there is only the one it will still work with n number of things
counter = 0 #counter to keep track of which toxin we are on
if not os.path.isdir(folder): #check to see if the toxin folder exists
    folders = glob.glob('PATH/TO/ROOT/fasta_files/PROKKA/tox/'+folder_name+"*") #i.e. temp.1 instead of temp. If there is no toxin, this will be an empty list
    folders.sort()
    
for folder in folders: #if the passed in folder simply does not exist, no problem!
    counter += 1
    
    multi_tox = False
    if len(folders) > 1:
        multi_tox = True
        folder_name = folder_name.rstrip("."+str(counter-1)) + "."+str(counter) #the rstrip bit is to avoid things like: temp.1.2.blastp.tsv
    
    BLAST_outputs = out_dir + folder_name + ".tsv" #sets up the correct output directory, parallel to the database being processed
    
    cmdln = "blastp -query " + folder+"/"+folder_name+".toxin.faa" + " -db " + database + " -outfmt '6 qseqid stitle qlen slen length nident pident mismatch gaps qstart qend qseq' -out " + out_dir + folder_name + ".blastp.tsv"
    process = subprocess.Popen(cmdln, shell=True) #executes the desired program
    process.wait() #waits until the command has finished processing before ending
    
    
    x = os.path.getsize(out_dir + folder_name + ".blastp.tsv") #checking if a file is empty and, if it is, renaming the empty file to reflect this       
    if x == 0:
        if multi_tox:
            out_file = open(out_dir + "data/" + folder_name + "."+str(counter)+".no_hits", 'w') #that check for .1
        else:
            out_file = open(out_dir + "data/" + folder_name + ".no_hits", 'w')
        out_file.write("No hits")
        out_file.close()
        continue #and that is all we care for doing with an empty file
            
    blast_file = open(out_dir + folder_name + ".blastp.tsv", 'r')
    out_file = open(out_dir + "data/" + folder_name + ".orfX_HA.tsv", 'w')
    
    orfx1, orfx2, orfx3, ha70, ha17, ha33 = [False]*6 #setting all the variables we are checking for to a false default
    list_to_check = ['orf-x1', 'orf-x2', 'orf-x3', 'ha70', 'ha17', 'ha33']
    
    
    for line in blast_file:
        #quality variables
        line = line.split("\t")
        slen = float(line[3]) #extracting data from the quast results
        length = float(line[4])
        pident = float(line[6])
        if length/slen >= LENSLEN and pident >= PIDENT: #checking if our stuff does passes our requirements
            thing_to_check = line[1].split("!!!")[1].lower() # this is what we are looking for and we want it lower case, just to avoid any un needed errors
            try:
                position = list_to_check.index(thing_to_check) #this will spit out the list index the thingshoes up it
            except: #if the item is not in our list, an error is thrown and so we will catch it and have our script go on to the next line
                continue
            #now the part where we set the matching resutls to True and writting to the out_file in tsv form.
            #if one of the types has already been found, then skip along as we do not want to repeat the same output
            if position == 0 and not orfx1:
                orfx1 = True #prevent duplicates
                out_file.write(list_to_check[position] + "\t") #write out that we got this result to the file
            elif position == 1 and not orfx2:
                orfx2 = True
                out_file.write(list_to_check[position] + "\t")
            elif position == 2 and not orfx3:
                orfx3 = True
                out_file.write(list_to_check[position] + "\t")
            elif position == 3 and not ha70:
                ha70 = True
                out_file.write(list_to_check[position] + "\t")
            elif position == 4 and not ha17:
                ha17 = True
                out_file.write(list_to_check[position] + "\t")
            elif position == 5 and not ha33:
                ha33 = True
                out_file.write(list_to_check[position] + "\t")
            #else we don't care
    
    blast_file.close()
    out_file.close()
    

    x = os.path.getsize(out_dir + "data/" + folder_name + ".orfX_HA.tsv") #checking if a file is empty and, if it is, renaming the empty file to reflect this
    if x == 0:
        os.rename(out_dir + "data/" + folder_name + ".orfX_HA.tsv", out_dir + "data/" + folder_name + ".no_hits")

    if args.clean:
        rmtree(folder) #remove the old temp folder file after finishing (so that we will not see any conflicts between independent uploads)
