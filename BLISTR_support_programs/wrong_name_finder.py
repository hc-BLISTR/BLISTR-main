from __future__ import print_function
#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

"""
Created on Tue Jun 28 14:47:05 2016

@author: Owen Neuber

On occasion, the file name of one of our glorious fasta files does not match the name
given after the contig ">" tag. That is unacceptable so this program will find these
nefarious files and will spit out their names so that we may hunt them down and
personally execute them!

I do not automate the fixes because the need to fix files is very infrequent and
the reasons for needing to fix them may varry. To avoid more pathetic machine 
errors, we will send in a right proper human to get the job done right!
With that said, if you want to automate the fixes, which could be clumsy
and allow you to miss an important error, set AUTOFIX to True. Alternatively,
when using this program in terminal, using the flag -a or --autofix will
set autofix to True.
"""

import os
import glob
from tqdm import tqdm
from blessings import Terminal
import argparse

AUTOFIX = False #AUTOFIX's default is False
parser = argparse.ArgumentParser()
parser.add_argument("--autofix", "-a", help="sets AUTOFIX to True. All files with improper genome names will have their genome name replaced with the proper one from the file name. Not using these flags keeps AUTOFIX off, having the program only alert the user to files with errors, instead of fixing them", action="store_true")
args = parser.parse_args()
if args.autofix: #If the flags are used, then AUTOFIX will be set to True
    AUTOFIX = True

colours = Terminal()
files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
 
fix = "off"
file_num =0
num_of_files = len(files)
files_with_errors = [] #initializing our nifty lists
error_name = []

if AUTOFIX:
    fix = "on"
print (colours.yellow + "AUTOFIX is turned " + fix) #to let the user know if things are being autofixed
    
print (colours.yellow + "Searching for errors: " + colours.magenta) #to ensure a nice coloured loading bar
with tqdm(total=num_of_files) as pbar:
    for i in files:
        extract = open(i)
        file_name = os.path.basename(i)[:-6] #file base name, minus the ".fasta"
        error = False #only if an error is detected will autofix be run
                
        for line in extract:            
            genome = line.split(",")[1] #takes the second element in the top line  
            if genome != file_name: #If the names do not match then we have a problem
                error = True
                files_with_errors.append(file_name) #adding any errous file name to our list
                error_name.append(genome) #giving what the name was but should not have been
            extract.close()
            break #we care only about the first line, so stop after it
                
        if AUTOFIX and error:            
            f = open(i,'r') #open the file and store all of the data (many slow, few impress)
            filedata = f.read()
            f.close()
            
            newdata = filedata.replace(genome, file_name) #format: ("old data", "new data")
            
            f = open(i,'w') #opens the file again and writes everything over again, but this time with the problem string replaced!
            f.write(newdata)
            f.close()
            
        pbar.update(1) #always update that loading bar            
            
#The following is just some simple user outputs:
if len(files_with_errors) == 0:
    print (colours.green + "No errors in detected" + colours.normal)
elif len(files_with_errors) == 1:
    print (colours.red + str(1) + " error detected:") #If there is only one error, I want it to say "1 error detected", not "1 errors dectected"
    print (colours.red + "File: " + files_with_errors[0] + " had genome name: " + error_name[0])
        
    if AUTOFIX:
        print (colours.yellow + "Errors have been resolved" + colours.normal)
    print (colours.yellow + "End of errors")
    
else:
    counter = 0 #counter to keep parallel lists in check
    print (colours.red + str(len(files_with_errors)) + " errors detected:")
    for error_file in files_with_errors: #primed and ready to print out the errorus files
        print (colours.red + "File: " + error_file + " had genome name: " + error_name[counter])
        counter += 1
    if AUTOFIX:   
        print (colours.yellow + "Errors have been resolved" + colours.normal)
    print (colours.yellow + "End of errors")            
        