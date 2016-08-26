# -*- coding: utf-8 -*-
"""
Created on Mon Jul 25 10:11:24 2016

@author: Owen Neuber

program to count the number of files in a direcetory with over two lines in them.
This is used for finding which genomes have multiple good hit toxins.
"""

import os 
import glob
files = glob.glob("PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/*.fasta") #list of all the toxin best_hit data files
over_two = 0
file_names = []

for fasta_file in files:
    fasta = open(fasta_file, 'r')
    counter = 0 #counter to keep track of how man lines are in the file
    for line in fasta:
        counter +=1
        if counter > 2: #if there are more than 2 lines in the file (i.e. 3 lines) then that means there must be more than one toxin in the file (as a single toxin takes up two lines)
            over_two += 1 #keep track of our number of doubles
            file_names.append(os.path.basename(fasta_file)) #if there are more than two toxins, add that bad boy to our special list
            break
    fasta.close()
print "There were " + str(over_two) + " files with over two lines in them"
if over_two > 0:
    print "They were: "
    for name in file_names: #print out all the names of the fasta files that had over two toxins
        print name