# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 13:23:34 2016

@author: Owen Neuber

Program which will recursivly replace all instances of a string with another
string. Flags of the starting directory, and the names of the things to replace 
will be optional. The defualt directory is the current directory (i.e. $ pwd)
and the default replacments will be 'BITTR' with 'BLISTR'. This program will
NOT be case sensitive, by defualt, unless the case sensitive flag is deployed.
"""

import os
import subprocess
from blessings import Terminal
import argparse

colours = Terminal()

parser = argparse.ArgumentParser()
parser.add_argument("--sensitive", "-s", help="Makes the find and replace functions case sensitive. (case sensitve would mean that 'Bittr' becomes 'Blistr', all caps becomes all caps, and lowercase becomes lowercase)", action="store_true")
parser.add_argument("--path", "-p", help="Path to the directory where we would like to start our recursive find and replace")
parser.add_argument("--find", "-f", help="The string the user would like to have replaced")
parser.add_argument("--replace", "-r", help="The string the user would like to use as the replacement")
args = parser.parse_args()

path = os.getcwd()
find = 'BITTR'
replace = 'BLISTR'
if args.path:
    path = args.path
if args.find:
    find = args.find
if args.replace:
    replace = args.replace
if args.sensitive: #if they want things case sensitive
    finding = [find.upper(), find.lower(), find.capitalize()]
    replacements = [replace.upper(), replace.lower(), replace.capitalize()]
    counter = 0
    for find in finding: #the followingare just a bunch of sed calls is all
        process = subprocess.Popen("find " + path + " -type f -print0 | xargs -0 sed -i " + "'s/"+find+"/"+replacements[counter]+"/g'", shell=True)
        process.wait()
        process = subprocess.Popen("find " + path + " -type f -exec rename " + "'s/"+find+"/"+replacements[counter]+"/' '{}' \;", shell=True)
        process.wait()
        process = subprocess.Popen("find " + path + " -type f -execdir rename " + "'s/"+find+"/"+replacements[counter]+"/' '{}' \;", shell=True)
        process.wait()
        counter += 1
else:
    process = subprocess.Popen("find " + path + " -type f -print0 | xargs -0 sed -i " + "'s/"+find+"/"+replace+"/g'", shell=True) #comandline to recursivly find and replace strings in files
    process.wait()
    process = subprocess.Popen("find " + path + " -type f -exec rename " + "'s/"+find+"/"+replace+"/' '{}' \;", shell=True) #change file names
    process.wait()
    process = subprocess.Popen("find " + path + " -type f -execdir rename " + "'s/"+find+"/"+replace+"/' '{}' \;", shell=True) #change directory names
    process.wait()
        