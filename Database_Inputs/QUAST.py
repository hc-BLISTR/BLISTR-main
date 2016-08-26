# -*- coding: utf-8 -*-
#! /usr/bin/python2.7
"""
Created on Mon Jun 27 10:15:39 2016

@author: Owen Neuber

Poor man's version of QUAST.py from Database_Creation. Basically the same but 
scaled down to only handle singular fasta files (with the path to that file
provided by processor.py).
"""

import os
import subprocess
from blessings import Terminal

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
args = parser.parse_args()
URL = args.URL

colours = Terminal()

QUAST = 'python PATH/TO/quast.py ' #change this to match the quast path on a different computer
quast_temp_dir = 'PATH/TO/ROOT/fasta_files/quast_results' #where we will store the original quast reports
report_tsv = 'PATH/TO/ROOT/fasta_files/quast_results/report.tsv' #path to the most recent quast report
out_dir = 'PATH/TO/ROOT/fasta_files/QUAST_reports/' #the path to where the result files will be transported


file_name = os.path.basename(URL)[:-6] #.rstrip(".fasta") #extracts the filename of the file being processed & removes the ".fasta"


cmdln = QUAST + URL + " -o " + quast_temp_dir + " --no-plots" #the QUAST commandline call. Removes plots for greater speed!
process = subprocess.Popen(cmdln, shell=True) #executes the desired program
process.wait() #waits until the command has finished processing before ending
process = subprocess.Popen("clear", shell=True) #cleans up the disgusting terminal outputs produced by QUAST
process.wait()

report = open(report_tsv, 'r') #opening our report file in the 'latest' directory
out_report = open(out_dir + file_name + ".QUAST.tsv", 'w') #creating the output tsv file with the right path and 'originalfasta.QUAST' format

counter = 0
for line in report:
    counter += 1
    if counter < 2 or counter > 9 and counter != 14: #we do not care about any of the values from the excluded lines, thus we skip them
        continue
    
    line = line.split("\t") #This splits the columns into list form so that I may manipulate the data inside            
    
    out_report.write(line[0] + "\t" + line[1]) #writing what we care about to our new file, with metadata in column 0 and data in column 1, they are separated by a tab
    
report.close() #closing the files
out_report.close() 
    