# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 08:41:28 2016

@author: Owen Neuber

Program to run a 16S BLAST call against a user inputted file (inputted to BLISTR app)

The top 5 hits will be considered and of those hits, only results with 
lenth/slen >= 0.85 and pident >= 85% will be considered.

"""

import os
import subprocess
from blessings import Terminal

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
args = parser.parse_args()
URL = args.URL

colours = Terminal() #for terminal outputs with gorgeous colours!

database = "PATH/TO/ROOT/fasta_files/databases/16S_db/16s_contigs.fasta"
out_dir = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out/'

LENSLEN = 0.85
PIDENT = 85.0


file_change = False
file_name = os.path.basename(URL)[:-6] #extracts the filename of the file being processed & removes the last 6 character (i.e. '.fasta')

BLAST_outputs = out_dir + file_name + ".tsv" #sets up the correct output directory, parallel to the database being processed
        
cmdln = "blastn -query " + URL + " -db " + database + " -max_target_seqs 5 -outfmt '6 qseqid stitle qlen slen length nident pident mismatch gaps qstart qend sstrand qseq' > " + out_dir + file_name + ".blast.tsv"
process = subprocess.Popen(cmdln, shell=True) #executes the desired program
process.wait() #waits until the command has finished processing before ending

blast_file = open(out_dir + file_name + ".blast.tsv", 'r') 
line_num = 0
counter = 0
current = []
rev = {}
for line in blast_file:
    current.append("") #to make our current list match whatever number of rows our file may have
    current[counter] = line
    line = line.split("\t") #make the first line of tsv into a list
    #quality variables
    slen = float(line[3])
    length = float(line[4])
    pident = float(line[6])
    sstrand = line[11]
    if length/slen < LENSLEN or pident < PIDENT: #if it does not meet our criteria, set it to None and then remove None from our list
        current[counter] = None
        current.remove(None)
        counter -= 1
        file_change = True
    elif sstrand != "plus": #if we have the minus strand that is bad news bears so we must note that for changes. It is an ellif because we don't want to bother flipping sequences if they are not worthy
        rev.update({line_num:line[12]}) #{counter: qseq}
        
                 
    counter += 1
blast_file.close()

if rev: #if the reverse dictionary has been populated
    temp = open(out_dir+'temp/temp.fasta', 'w')
    for num in rev: #write the name as the line number (1-5)
        temp.write(">"+str(num)+"\n"+str(rev.get(num))+"\n")
    temp.close()
    revcomp = "PATH/TO/ROOT/BLISTR_support_programs/./revcomp "+out_dir+"temp/temp.fasta > "+out_dir+"temp/temp.rev.fasta"
    process = subprocess.Popen(revcomp, shell=True) #creates a temp.rev.fasta file that will hold the reversed sequences
    process.wait()
    temp = open(out_dir+"temp/temp.rev.fasta", 'r')
    count = -1
    seq = ""
    first_num = -1
    replace ={}
    for l in temp:
        if l.startswith(">"):
            if count != -1:
                replace.update({first_num: seq})
                seq = "" #can't forget to reset seqence to nothing for the next contig
            first_num = int(l.lstrip(">"))
            count += 1
            continue
        seq = seq+l.rstrip("/n")
    replace.update({first_num: seq}) #can't forget about that last sequence to add
    temp.close()
    blast_file = open(out_dir + file_name + ".blast.tsv", 'w')  #now for the bit where I actually fix this problem
    count = 0
    for line in current:
        if replace.get(count):
            old_seq = line.split("\t")[12]
            line = line.replace(old_seq, replace.get(count).replace("\n","")) #swap out the minus sequence with the plus sequence
            line = line.replace("minus", "reversed to plus")
        blast_file.write(line+"\n")
        count += 1
    blast_file.close()

if file_change: #if one of our results is bad, we will have to recreate the file with our changes
    blast_file = open(out_dir + file_name + ".blast.tsv", 'w') 
    for line in current:
        blast_file.write(line)
    blast_file.close()                
        
x = os.path.getsize(out_dir + file_name + ".blast.tsv") #checking if a file is empty and if it is, renaming the empty file to display this
if x ==0:
    os.rename(out_dir + file_name + ".blast.tsv", out_dir + file_name + ".no_hits")
    out_file = open(out_dir + file_name + ".no_hits", 'w')
    out_file.write("No hits")
    out_file.close()

