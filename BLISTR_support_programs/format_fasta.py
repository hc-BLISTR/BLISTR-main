# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 14:45:42 2016

@author: Owen Neuber

Program that will take in contig header data from a TSV. The TSV will be formatted with two columns:
path/to/file  \t  Genome_name,Author,Collection_date,Clinical_or_Environmental,Source_info,Institution,Lat,Long,Country,Region

This program will take in the path to the TSV file.
The program will take the given header in the TSV and apply it to the supplied fasta
file and append >contig number to the front of each header.
Also removes any fasta files below 500 bp
"""
import os
from blessings import Terminal
from tqdm import tqdm
import argparse

colours = Terminal()

parser = argparse.ArgumentParser()
parser.add_argument("path", help="The path to the TSV file wich is formated: path/to/file \t Genome_name,Author,Collection_date,Clinical_or_Environmental,Source_info,Institution,Lat,Long,Country,Region")
args = parser.parse_args()

path = args.path

TSV = open(path, 'r')
num_lines = 0
for line in TSV: #count how many fastas we will change (for loading bar)
    num_lines += 1
TSV.close()

TSV = open(path, 'r')

print colours.cyan + "Formatting Fasta Files:" + colours.magenta
with tqdm(total=num_lines) as pbar:
    for line in TSV:
        path_to_fasta = line.split("\t")[0] #extracting the path to the fasta file and the header information
        header = line.split("\t")[1].rstrip("\n")
        if len(header.split(",")) != 10: #there should be 10 entries in the header if this is formatted correctly
            print colours.red + header + " is an invalidly formatted header" + colours.magenta
            continue
        fasta = open(path_to_fasta, 'r')
        
        seqs = []
        seq = "5"*508 #just something to get past the first round (needs to be over 500 characters)
        if not os.path.isfile(path_to_fasta):
            print colours.red + path_to_fasta + " is an invalid path" + colours.magenta
            continue
        for l in fasta:
            if l.startswith(">"):
                if len(seq) >= 500: #if the contig is large enough
                    seq= seq.rstrip("5") #remove those rediculous fives
                    seqs.append(seq) #if things check out, add in the contig
                    seq = "" #got to remember to reset the sequence between contigs
                    continue
                seq = "" #if the sequence was not large enough, reset it and start again
                continue
            seq = seq + l
        if len(seq) >= 500: #keep all the sequences over 500 bp
            seqs.append(seq) #add that last sequence
        seqs.remove("") #remove any nonsense that may have slipped by
        fasta.close()
        
        fasta = open(path_to_fasta, 'w') #overwrite with our format
        counter = 1
        for seq in seqs:
            fasta.write(">"+str(counter)+","+header+"\n"+seq) #write the header (with contig number) and our sequence following that
            counter += 1
    
        pbar.update(1)
print colours.cyana + "done" +colours.normal