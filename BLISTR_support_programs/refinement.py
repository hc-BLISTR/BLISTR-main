# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 09:15:24 2016

@author: Owen Neuber

Program that will take in all of our fasta files from the fasta file directory
and create a tsv of all the file names with their toxin types and group information
removed while having that removed information in the column adjacent to the name 
(however the group number will be dropped entirely). Then all the fasta files will
be renamed to reomve the toxin data from the name and the same adjustiment will
be made with the contigs. Any contigs with less than 500 characters will be
removed from the fasta files. The above will be the default. 
optional flags will be:
-f will make only the file of changes while not doing the changes
-c will not make the file of changes but will do the changes
This program was used during a formatting migration period. It will likely have little
application purposes any more
"""

import os
import glob
from blessings import Terminal
from tqdm import tqdm
import argparse

colours = Terminal()

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="The path to the directory where you would like the result of this program to be written in the form: path/to/directory")
parser.add_argument("--file", "-f", help="The program will only make a tsv file of all the fasta files' names and the toxin type that was appended to their names", action="store_true")
parser.add_argument("--change", "-c", help="The program will only remove all the toxin and group data from fasta files' names and contig headers. Also any contigs under 500 bp will be removed", action="store_true")
args = parser.parse_args()

if args.change and args.file:
    print colours.red + "If you want to create both the file and make the changes, do not enter any flags (the default). Change and file flags cannot be used in tandem. See -h or --help for more details." + colours.normal

folder = "/"+str(args.dir).rstrip("/").lstrip("/")+"/" #make sure formatting is good

if not os.path.isdir(folder):
    print colours.red + "The provided directory is not a valid path. Please change it to a valid path."
    assert(False)

path = "PATH/TO/ROOT/fasta_files/"
files = glob.glob(path+"*.fasta")
TSV_out = folder+"name_and_types.tsv"
counter = 2
while os.path.isfile(TSV_out): #just a quick loop to ensure we don't override anything
    TSV_out = folder+"name_and_types."+str(counter)+".tsv"
    counter += 1
    
num_files = len(files)*2
if args.change or args.file:
    num_files = int(num_files/2)

print colours.cyan + "Processing..." + colours.magenta
with tqdm(total=num_files) as pbar:
    #Creating the TSV file
    if not args.change: #If they are using default values or -f, they can't be using -c
        TSV = open(TSV_out, 'w')
        for fasta in files:
            g_name = os.path.basename(fasta).split(".")
            if len(g_name) == 2: #i.e. no type information like: 111.fasta (instead of 111Delta.B.fasta)
                pbar.update(1)
                continue #no need for a change in these cases (other than the 500 bp thing)
                
            g_type = "" #initializing             
            if len(g_name) == 4: # i.e. 12LNRI-CD.A-B-.GroupIII.fasta
                g_only = g_name[0]
                g_type = g_name[1] #the type always comes before the group number if both are present
                g_group = g_name[2]
            elif len(g_name) == 3:
                if g_name[1].upper().startswith("GROUP"): #checking if group is in the second list entry
                    pbar.update(1)
                    continue #we don't care about group related things
                else:
                    g_type = g_name[1]
                    g_only = g_name[0]
                    
            TSV.write(g_only+"\t"+g_type+"\n")
            pbar.update(1)
            
            
    #Reducing fasta files to have contigs with only 500 bp and up. Also switching file names and contig headers to obmit types and groups
    if not args.file:
        for fasta in files:
            old_name = os.path.basename(fasta)
            new_name = os.path.basename(fasta).split(".")[0] + ".fasta" #ensuring something of the type 111.fasta (regardless of types and groups)
            old = open(fasta, 'r')
            headers = []
            seqs = []
            seq = "5"*508
            broken = False #keeps track of wheather or not I used a break
            for line in old:
                if line.startswith(">"):
                    if len(seq) < 500: #if the contig is too small
                        headers.remove(headers[len(headers)-1]) #remove the last contig header from the list
                        broken = True
                        break
                    seq= seq.rstrip("5") #remove those rediculous fives
                    headers.append(line.replace(old_name[:-6],new_name[:-6])) #swapping the old name with the types for the new one and removing the .fasta
                    seqs.append(seq)
                    seq = ""
                    continue
                seq = seq + line
            if not broken and len(seq) >= 500: #if things meet our criteria, add them to the list
                seqs.append(seq)
            seqs.remove("") #remove that strating annoyance
            old.close()
            new = open(fasta, 'w')
            counter = 0
            for header in headers: #write out our stuff to the files
                new.write(header)
                new.write(seqs[counter])       
                counter += 1
            new.close()
            
            os.rename(path+old_name,path+new_name)
            pbar.update(1)
print colours.cyan + "done" + colours.normal