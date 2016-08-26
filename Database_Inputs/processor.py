#! /usr/bin/python2.7
#!/bin/sh
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 07:07:13 2016

@author: Owen Neuber

RUN this program to UPLOAD a signle new fasta file's data to the BLISTR.db database

Will run all the programs in the list 'programs' sequentially, waiting for each to 
finish before going onto the next. If more programs are needed to 

This program should only be called via views.py in the BLISTR app
"""

import os
import subprocess
from blessings import Terminal
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
parser.add_argument("--prokka", "-p", help="Tells the program to upload prokka data", action="store_true")
parser.add_argument("--information", "-i", help="List of all the user metadata for the genome they are uploading (the list will be separated by '-' instead of commas). An spaces originally entered will be replaced with '~'s")
parser.add_argument("--sub_type", "-s", help="The value entered in the SubType field, if applicable")
parser.add_argument("--data", "-d", help="The user entered pident, followed by Len/Slen values to be used in the BLAST call")
args = parser.parse_args()

URL = args.URL #the URL of the desired Genome to be uploaded. Will be sent as an argument to all the functions that are run below
sub_type = ""
if args.sub_type:
    sub_type = "-s "+args.sub_type+" "

colours = Terminal()

CLEAR_SCREEN = False #set to false if you don't want the screen cleared between processes
temp_fasta = 'PATH/TO/ROOT/Database_Inputs/temp.fasta'

if args.prokka: #tell the processor weather or not to run the prokka code right away
    #The psql statement is a command to add the hstore extension to our glorious database because it is needed for things to work 'cause reasons. Just trust me on this one, okay? OKAY!?
    programs = ['python PATH/TO/ROOT/Database_Inputs/temp_fasta_maker.py -i '+(args.information)+' '+ URL, \
        "python PATH/TO/ROOT/Database_Inputs/BLAST.py -d "+str(args.data)+" " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/16S_BLAST.py " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/PROKKA.py -g " + os.path.basename(URL)[:-6] +" " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/orfX_HA_BLAST.py " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/QUAST.py " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/uploader.py -p " +sub_type+ temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py" \
    ] #Just some nifty formatting to improve readbility I guess. Personally I don't like it.
    #TODO: maybe add the 16S issues table maker to the process flow both above and below here?
else:
    programs = ['python PATH/TO/ROOT/Database_Inputs/temp_fasta_maker.py -i '+(args.information)+' '+ URL, \
        "python PATH/TO/ROOT/Database_Inputs/BLAST.py -d "+str(args.data)+" " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/16S_BLAST.py " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/QUAST.py " + temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/uploader.py " +sub_type+temp_fasta, \
        "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py" \
    ]


for program in programs:
    print colours.cyan + "At: " + str(os.path.basename(program.lstrip("python ").rstrip(temp_fasta).rstrip("-p ").rstrip(".py "))).rstrip(str(args.data)).rstrip("-d ") + colours.normal #just says what is being run, as it is ran, for debuggin purposes
    process = subprocess.Popen(program, shell=True) #executes the desired program
    process.wait()
    if CLEAR_SCREEN:
        process = subprocess.Popen("clear", shell=True)
        process.wait()
    
        
