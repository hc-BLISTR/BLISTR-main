# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 14:53:25 2016

@author: Owen Neuber

So this program determines which orfx of ha things we get from blasting a toxin++
faa file against the database: PATH/TO/ROOT/fasta_files/databases/orfX_HA_db/orfX_HA_NTNH_proteinDB.faa
The toxin++ faa files will be provided by every entry folder in the directory:
PATH/TO/ROOT/fasta_files/PROKKA/tox/ Then all blast results will
be stored in the directory PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/
After processing those outputted blast files (of the form genome_name.blastp.tsv),
a new tsv (of the form genome_name.orfX_HA.tsv) will be stored in the directory:
PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/data/
containing relevant information on the toxin relating to orfx and HA.

How I'm going to do this is using len/slen >= 0.90 and pident >= 90 as our threshold.
Anything out of this threshold will not be considered. Then, of our passing hits,
if they have a any of: orfx1, orfx2, orfx3, ha70, ha17, ha33 it will be recorded by 
setting their corresponding variables to True. Then after figuring out which it hit,
I am going to write the corresponding relevant information to the aforementioned data folder.

Now you may be wondering what we will do about multi toxin genomes (i.e. with toxin 
folders of both genome_name.1 and genome_name.2). Great question. The answer is nothing!
We will do nothing special and we will process the both of them individually as
though the other did not exist. It is the job of extractor.py to deal with the 
niceties of politics.

This program has to be run after PROKKA, it will not work if run before
"""

import os
import subprocess
import glob
from tqdm import tqdm
from blessings import Terminal

colours = Terminal() #for terminal outputs with gorgeous colours!

folders = glob.glob('PATH/TO/ROOT/fasta_files/PROKKA/tox/*') #will prodcue a list of all folders in the directory
num_folders = float(len(folders))
#Check against current files to prevent time consuming repeats
current_files = glob.glob('PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/data/*')

database = "PATH/TO/ROOT/fasta_files/databases/orfX_HA_db/orfX_HA_NTNH_proteinDB.faa"
out_dir = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/'

LENSLEN = 0.90
PIDENT = 90.0


print colours.cyan + "Processing the orfX_HA database:" + colours.magenta
with tqdm(total=num_folders) as pbar: #setting up the sweetest progressbar
    for folder in folders:
        folder_name = os.path.basename(folder) #removes the path from the folder's name
        
        if out_dir+"data/"+folder_name+".orfX_HA.tsv" in current_files or out_dir+"data/"+folder_name+".no_hits" in current_files: #checks the current fasta to be processed against ones already processed. It can only be done against the whole path so that is why this if statement is so disgusting
            pbar.update(1) #can't forget to update that sexy loadin bar
            continue #if it has already been processed, skip it      
        
        
        BLAST_outputs = out_dir + folder_name + ".tsv" #sets up the correct output directory, parallel to the database being processed
                
        cmdln = "blastp -query " + folder+"/"+folder_name+".toxin.faa" + " -db " + database + " -outfmt '6 qseqid stitle qlen slen length nident pident mismatch gaps qstart qend qseq' -out " + out_dir + folder_name + ".blastp.tsv"
        process = subprocess.Popen(cmdln, shell=True) #executes the desired program
        process.wait() #waits until the command has finished processing before ending
        
        x = os.path.getsize(out_dir + folder_name + ".blastp.tsv") #checking if a file is empty and, if it is, renaming the empty file to reflect this
        if x == 0:
            out_file = open(out_dir + "data/" + folder_name + ".no_hits", 'w')
            out_file.write("No hits")
            out_file.close()
            pbar.update(1)
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

        pbar.update(1)