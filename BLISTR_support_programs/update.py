# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 14:18:43 2016

@author: Owen Neuber

Program to update your current version of BLISTR to the newest version of BLISTR.
If you don't move this program out of the BLISTR_support_programs dirctory, then
running this program (with your termial locally opened in the BLISTR_support_programs 
dirctory) will fully update your copy of BLISTR. A simple command of:
$ python update.py
"""

import os
from shutil import rmtree
from blessings import Terminal
import subprocess

colours = Terminal()


working_directory = str(os.getcwd()) #get their working directory and make sure they did not cheat
if not working_directory.endswith("BLISTR_support_programs"):
    print colours.red + "Your current working directory is not ~/BLISTR_support_programs. cd into /BLISTR_support_programs to proceed" + colours.normal
    assert(False)

path_to_root = working_directory.split("BLISTR_support_programs")[0]
rmtree(path_to_root) #removes our current BLISTR tree

os.mkdir(path_to_root)

os.chdir(path_to_root) #move into the new empty folder
#download installer.py into the current parent directory
proc = subprocess.Popen("curl -o ../installer.py https://raw.githubusercontent.com/hc-BLISTR/BLISTR-main/master/BLISTR_support_programs/installer.py", shell=True)
proc.wait()
proc = subprocess.Popen("python ../installer.py -g -ff -udb", shell=True)
proc.wait()