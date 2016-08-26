# -*- coding: utf-8 -*-
#! /usr/bin/python2.7
"""
Created on Mon Jun 27 10:15:39 2016

@author: Owen Neuber

Application to run QUAST against all the fasta files from 'PATH/TO/ROOT/fasta_files' 
The report.tsv files will be renammed after their original fasta file name in the form of:
'originalfasta.QUAST'. These outputed files will be stored in the directory:
'PATH/TO/ROOT/fasta_files/QUAST_reports'.
This will later be used for extration of quality data to be loaded into the BLISTR database via extractor.py

Quite fortunitly, the most recent QUAST report is stored in the 'quast_results' directory when using the -o command.
Capitilizing on this, all QUAST reports that we call will always be from the path:
'PATH/TO/ROOT/fasta_files/quast_results/report.tsv'
This will result in all QUAST reports being overwritten through each iteration.
This will keep our file systems clean and keep the reports we process up to date.

From the report.tsv fasta files, we only care about the data from the second column in rows
2 through 9 and 14. All other rows will be obmitted when this data is transfered.

The file, quast.py, that actually does the quasting is stored in this directory:
'PATH/TO/quast.py'
"""

import os
import subprocess
import glob
from tqdm import tqdm
from blessings import Terminal

colours = Terminal()

QUAST = 'python PATH/TO/quast.py ' #change this to match the quast path on a different computer
files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
done_files = glob.glob('PATH/TO/ROOT/fasta_files/QUAST_reports/*.QUAST.tsv') #list of files that have already had their reports extracted
num_files = float(len(files)) #number of files being processed
quast_temp_dir = 'PATH/TO/ROOT/fasta_files/quast_results' #where we will store the original quast reports
report_tsv = 'PATH/TO/ROOT/fasta_files/quast_results/report.tsv' #path to the most recent quast report
out_dir = 'PATH/TO/ROOT/fasta_files/QUAST_reports/' #the path to where the result files will be transported

print colours.cyan + "Processing QUAST reports: " + colours.magenta
with tqdm(total=num_files) as pbar: #setting up the sweetest progressbar
    for fasta in files:
        file_name = os.path.basename(fasta)[:-6] #.rstrip(".fasta") #extracts the filename of the file being processed & removes the ".fasta". the rstrip does not work as it turns "111Delta.fasta" into '111Del'
        
        if (out_dir + file_name + ".QUAST.tsv") in done_files: #if the full path & filename is present in the directory of our output files, skip this particular iteration
            pbar.update(1) #can't forget to update the progress bar even if your skipping data
            continue
        
        cmdln = QUAST + fasta + " -o " + quast_temp_dir + " --no-plots" #the QUAST commandline call. Removes plots for greater speed!
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
        pbar.update(1) #updating the super slick progress bar
    