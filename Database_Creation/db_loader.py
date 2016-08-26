#! /usr/bin/python2.7
#!/bin/sh
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 07:07:13 2016

@author: Owen Neuber

RUN this program to UPLOAD all fasta files' data to the BLISTR.db database

Python executable that will execute other scripts in order to fully upload files from:
PATH/TO/ROOT/fasta_files into the BLISTR database, fully formated and 
with metadata extracted.

Will run all the programs in the list 'programs' sequentially, waiting for each to 
finish before going onto the next.

This program will delete the current BLISTR.db (if exists) and then create a new
BLISTR.db from scratch (That is the default. See other flags for additional functionallity)

BEFORE RUNNING: make sure that no windows that have any relationship to the BLISTR.db 
database are open/running (i.e. you can't have the BLISTR app running and if you ran
modles.py in spyder to debug some database stuff then you will need to close spyder)
"""
import os
import subprocess
import time
import glob
from blessings import Terminal
from shutil import copyfile
import argparse

colours = Terminal()

main_models_last_mod_date = time.ctime(os.path.getmtime('PATH/TO/ROOT/models.py')) #get the last update time for modles.py
local_models_last_mod_date = time.ctime(os.path.getmtime('PATH/TO/ROOT/Database_Creation/models.py'))

if main_models_last_mod_date!=local_models_last_mod_date: #check to see if the models are up to date
    print colours.cyan + "Syncing other models.py to the main models.py file (in the BLISTR directory)..." + colours.normal
    copyfile('PATH/TO/ROOT/models.py', 'PATH/TO/ROOT/Database_Creation/models.py')
    copyfile('PATH/TO/ROOT/models.py', 'PATH/TO/ROOT/Database_Inputs/models.py') #syncing the other models while we're at it
    copyfile('PATH/TO/ROOT/models.py', 'PATH/TO/ROOT/Database_Outputs/models.py')

#The psql statement is a command to add the hstore extension to our glorious database because it is needed for things to work 'cause reasons. Just trust me on this one, okay? OKAY!?
programs = ["dropdb \'BLISTR.db\'", "createdb \'BLISTR.db\'", \
    "psql -d BLISTR.db -c 'CREATE EXTENSION hstore'", \
    "python PATH/TO/ROOT/Database_Creation/models.py", \
    "python PATH/TO/ROOT/Database_Creation/BLAST.py", \
    "python PATH/TO/ROOT/Database_Creation/16S_BLAST.py", \
    "python PATH/TO/ROOT/Database_Creation/QUAST.py", \
    "python PATH/TO/ROOT/Database_Creation/PROKKA.py", \
    "python PATH/TO/ROOT/Database_Creation/orfX_HA_BLAST.py", \
    "python PATH/TO/ROOT/Database_Creation/extractor.py", \
    "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py -n", \
    "python PATH/TO/ROOT/Database_Inputs/16S_issues_table_maker.py" \
] #Just some nifty formatting to improve readbility I guess. Personally, I don't like it.

#The following are just the argument parsers for the purpose of allowing flags
parser = argparse.ArgumentParser()
parser.add_argument("--update", "-u", help="Updates the database to incorporate all the files from PATH/TO/ROOT/fasta_files into the database. This option will result in the BLISTR database NOT being destroyed and re-created and will therefore run much faster than the default settings", action="store_true")
parser.add_argument("--save", "-s", help="Will save the current BLISTR database to a database file. This will allow you to go back to past databases if need be. It will be stored in the directory PATH/TO/ROOT/Database_Creation/Past_Databases/", action="store_true")
parser.add_argument("--restore", "-r", help="Will destroy the current database and load the most recent database in its place. Cannot be used in tandem with the update flag nor the load flag", action="store_true")
parser.add_argument("--models", "-m", help="Will have this program ONLY update the models.py to match the root models. Nothing will happen in relation to databases", action="store_true")
parser.add_argument("--load", "-l", help="Will destroy the current database and load the user inputted database file in its place (accepts the full path to the database file, the full database file name, or the time stamp of the past database file). Cannot be used in tandem with the update flag nor the restore flag. Returns an error if a duplicated file is called")
args = parser.parse_args()
#TODO: add a flag option to allow the user to point to the directory where the fasta files they want to upload into the database are

if args.update and args.restore: #The following is to ensure that the user is not messing around with my flags
    print colours.red + "Not so fast cowboy, you can't use the restore and update flags at the same time. See -h of --help for more information" + colours.normal
    assert(False) #throws an error to crash the script
if args.update and args.load:
    print colours.red + "Not so fast little man, you can't use the load and update flags at the same time. See -h of --help for more information" + colours.normal
    assert(False)
if args.restore and args.load:
    print colours.red + "Not so fast Speedy Gonzales, you can't use the restore and update flags at the same time. See -h of --help for more information" + colours.normal
    assert(False)
if args.save and (args.restore or args.load or args.update or args.models):
    print colours.red + "Not so fast Sanic, you can't use the save flag at the same time as any other flags. Heisenberg's uncertainty principle says that until my code receives your flags it will not know in which state the flags are present (be it safe, load, or other) but the principle does not allow for both to occur at the same time. See -h of --help for more information" + colours.normal
    assert(False)

if args.update: #If the update flag is used, the database will not be destroyed
    programs = ["python PATH/TO/ROOT/Database_Creation/BLAST.py", \
        "python PATH/TO/ROOT/Database_Creation/16S_BLAST.py", \
        "python PATH/TO/ROOT/Database_Creation/QUAST.py", \
        "python PATH/TO/ROOT/Database_Creation/PROKKA.py", \
        "python PATH/TO/ROOT/Database_Creation/orfX_HA_BLAST.py", \
        "python PATH/TO/ROOT/Database_Creation/extractor.py", \
        "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py -n", \
        "python PATH/TO/ROOT/Database_Inputs/16S_issues_table_maker.py" \
    ] #Just some nifty formatting to improve readbility I guess. Personally I don't like it.

if args.save: #do a database dump
    print colours.cyan + 'Saving past database in file: '+colours.yellow+'PATH/TO/ROOT/Database_Creation/Past_Databases/BLISTR.db-'+time.strftime("%H:%M:%S-%d-%m-%Y") + colours.noraml
    programs = ["pg_dump BLISTR.db > PATH/TO/ROOT/Database_Creation/Past_Databases/BLISTR.db-"+time.strftime("%H:%M:%S-%d-%m-%Y")] #will store the old database in the file BLISTR.db-currenttimeanddate

if args.restore:
    files = glob.glob('PATH/TO/ROOT/Database_Creation/Past_Databases/BLISTR.db-*')
    basenames = ""
    current_time = ""
    past_time = "00:00:00-00-00-0000"
    no_files = True
    for i in files: #A loop to determine which database file is the most recent
        no_files = False
        our_file = i #The name of the current file
        current_time = os.path.basename(i) #time listed on the current file being considered
        current_time_l = current_time.replace(":", "-").split("-") #creates a list that holds each individual time data [hour, min, sec, day, month, year]
        past_time_l = past_time.replace(":", "-").split("-")
        counter = 5
        while True: #check all the time values against one another, from greates value to least, and if the current_time ever beats the past_time, it will take its place
            if current_time_l[counter] < past_time_l[counter]:
                break
            elif current_time_l[counter] > past_time_l[counter]:
                past_time = current_time
                break
            if counter >=3: #all this nonesense is just to have our checkers scheking in the proper order
                counter -= 1
            elif counter == 3:
                counter = 0
            else:
                counter += 1
                if counter == 3:
                    break #once we have done all the needed checking, break here
    if no_files:
        print colours.red + "Not so fast Shia Labeouf, you can't restore to an older database file if there are no database files! See -h of --help for more information" + colours.normal
        programs = []
    else:
        last_save = 'PATH/TO/ROOT/Database_Creation/Past_Databases/'+past_time
        programs = ["dropdb \'BLISTR.db\'", "createdb \'BLISTR.db\'", "psql BLISTR.db < "+last_save, "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py"]

if args.load:
    all_good = True
    if os.path.exists(args.load): #if true, it means the user entered an absolute path
        load = args.load
    elif len(glob.glob('PATH/TO/ROOT/Database_Creation/Past_Databases/'+args.load)) == 1: #if true, it means the user entered the full name of the database file, but not the path
        load = 'PATH/TO/ROOT/Database_Creation/Past_Databases/'+args.load
    elif len(glob.glob('PATH/TO/ROOT/Database_Creation/Past_Databases/BLISTR.db-*'+args.load)) == 1: #if true, it means the user entered the time stamp of the desired database file
        load = 'PATH/TO/ROOT/Database_Creation/Past_Databases/BLISTR.db-'+args.load
    else:
        print colours.red + "Not so fast Quentin Tarantino, it seems that your file either does not exist or there are duplicates of it. See -h of --help for more information" + colours.normal
        all_good = False
        programs = []
    if all_good: #as long as there was not an error, this will run
        programs = ["dropdb \'BLISTR.db\'", "createdb \'BLISTR.db\'", "psql BLISTR.db < "+load, "python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py"]

if args.models:
    programs = [] #so that nothing will happen

for program in programs: #The bit that actually runs all the programs
    process = subprocess.Popen(program, shell=True) #executes the desired program
    process.wait()
        
print colours.cyan + 'done' #every professional program ends with the sole output 'done', therefore mine must do that too!