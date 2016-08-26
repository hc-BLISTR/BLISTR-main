# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 14:09:17 2016

@author: Owen Neuber

Program to determine if the user's python libaries are up to date with BLISTR's.
If their versions are newer than BLISTR's, it will be assumed that they will
work just fine.
"""

import os
import subprocess
from blessings import Terminal
import argparse

colours = Terminal()

parser = argparse.ArgumentParser()
parser.add_argument("--autofix", "-a", help="All the discrepencies determined by this function will be automatically resolved by this program when this flag is used", action="store_true")
parser.add_argument("--path", "-p", help="The path to the BLISTR requirements.txt file in the form path/to/requirements.txt (the default path is your current working directory")
args = parser.parse_args()

path = str(os.getcwd()) + "/"
if args.path: #get the path to the requirements.txt file
    path = "/"+str(args.path).lstrip("/").rstrip("/requirements.txt").rstrip("/")+"/"

path += "requirements.txt"
if not os.path.isfile(path):
    print colours.red + path + " is not a valid path. Please change working directories to the one containing requirements.txt or use the flag -p with the correct path to requirements.txt" + colours.normal
    assert(False) #throw an error
    
#create a file to compare with
p = subprocess.Popen("pip freeze > shialabeoufwinninggoldatthe1984olyimpics.txt", shell=True) #create a file with their python extensions to compare against (a file they defintly don't already have) 
p.wait()

    
requirements = open(path, 'r')
they_have = open("shialabeoufwinninggoldatthe1984olyimpics.txt", 'r')

full_requirements_name_list = []
full_requirements_version_list = [] #parallel list to the above list to hold the corresponding requirements version
for line in requirements:
    line = line.rstrip("\n")
    full_requirements_name_list.append(line.split("==")[0])
    full_requirements_version_list.append(line.split("==")[1])
requirements.close()

things_to_update = []

for line in they_have:
    line = line.rstrip("\n")
    current_package = line.split("==")[0]
    current_package_version = line.split("==")[1]
    if current_package in full_requirements_name_list: #check if their current package is one of BLISTR's needed ones
        index = full_requirements_name_list.index(current_package) #if it is, find where in the list of BLISTR packages it lies
        if int(current_package_version < full_requirements_version_list[index]): #if their version is less than or equal to our version
            things_to_update.append((line, current_package+"=="+full_requirements_version_list[index])) #adding what needs to be updated and what it needs to be updated to to our list
            if args.autofix:
                p = subprocess.Popen("sudo pip install --upgrade " + current_package, shell=True) #if they want me to fix it for them, this should update it
                p.wait()
                
os.remove("shialabeoufwinninggoldatthe1984olyimpics.txt") #remove that ridiculous file

#output to the user what we did
if len(things_to_update) == 0:
    print colours.green + "All packages are up to date" + colours.normal
elif args.autofix:
    for one, two in things_to_update:
        print colours.green + "Package: " + one + " was updated to the most recent version" + colours.normal
else:
    for one, two in things_to_update:
        print colours.yellow + "Package: " + one + " should be updated to " + two + " or an even newer package"
        
print "done"