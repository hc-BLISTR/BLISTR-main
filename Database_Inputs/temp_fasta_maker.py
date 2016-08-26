# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 15:37:44 2016

@author: Owen Neuber

program that makes a temp file of the genome that our user wants to upload.
It is an exact copy except that every line with a ">" will be replaced with
our version with the format of:
>Contig_number,Genome_name,Author,Collection_date,Clinical_or_Environmental,Source_info,Institution,Lat,Long,Country,Region
Also, any contigs with less than 500bp will be cleaved.

From processor.py, this program will be passed a list (separated by '-'s) holding 
all the above information, in order, excluding Contig number (which will be
determined by this program)

The temaprary file will be called temp.fasta
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
parser.add_argument("--information", "-i", help="List of all the user metadata for the genome they are uploading (the list will be separated by '-' instead of commas). An spaces originally entered will be replaced with '~'s")
args = parser.parse_args()

temp_fasta = 'PATH/TO/ROOT/Database_Inputs/temp.fasta'
info = str(args.information).replace("-", ",").replace("~", " ").replace("????", "-") #formatting things to the mannor we would like them to be
URL = str(args.URL)
original = open(URL, 'r')
temp = open(temp_fasta, 'w')
contig_num = 1
    
path_to_fasta = temp_fasta
header = info
seqs = []
seq = "5"*508 #just some nonesense to meet some criteria I set myself
for l in original:
    if l.startswith(">"):
        if len(seq) >= 500: #if the contig is large enough
            seq= seq.rstrip("5") #remove those rediculous fives
            seqs.append(seq) #add in our dainty sequence to our list of sequences
            seq = "" #always go to reset this beween contigs
            continue
        seq = "" #if the sequence was not large enough, reset it and start again
        continue
    seq = seq + l #addig our currently processed line to our contig
if len(seq) >= 500: #check if the last contig is over 500 bp
    seqs.append(seq) #add that last sequence
seqs.remove("")
original.close()

temp = open(path_to_fasta, 'w') #overwrite with our format
counter = 1
for seq in seqs:
    temp.write(">"+str(counter)+","+header+"\n"+seq) #write out the header with its right proper contig number and matching sequence
    counter += 1

temp.close()