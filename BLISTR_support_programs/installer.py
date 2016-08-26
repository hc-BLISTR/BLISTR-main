# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 13:12:10 2016

@author: Owen Neuber

RUN this program to fully install BLISTR on your Unix system. To run this program,
cd into the directory holding this program and type:

$ python installer.py

There are additional flag options you can run with this command (see 
$ python installer.py -h    for details). Without flags, this program will
assume that all the BLISTR files have been git downloaded from *******
insert your github information here****** and that the current directory
(which your terminal is in (i.e. the result of $ pwd)) will be the root folder
for this program.
"""

import os
import glob
import subprocess
import commands
from shutil import rmtree
from blessings import Terminal
from tqdm import tqdm
import argparse

colours = Terminal()

parser = argparse.ArgumentParser()
parser.add_argument("--path", "-p", help="The path to the EMPTY (or none existant) directory you would like BLISTR to be downloaded into. Or, the path to the root directory where you already have BLISTR downloaded (this should be the directory with views.py in it). The default is your current working directory.")
parser.add_argument("--downloads", "-d", help="The path to  where you would like to receive downloads from BLISTR in the form: '/path/to/Downloads/'. The default is your Downloads directory.")
parser.add_argument("--quast", "-q", help="The path to your installed quast.py (path/to/quast.py format). If left blank, the installer will try to find an installed version of quast on your machine. If quast is not found, then one will be installed for you.")
parser.add_argument("--easyfig", "-e", help="The path to your installed easyfig.py (path/to/easyfig.py format). If left blank, the installer will try to find an installed version of easyfig on your machine. If easyfig is not found, then one will be installed for you.")
parser.add_argument("--cpus", "-c", help="Sets the number of cpus you will allow BLISTR processes to use while running the app (this excludes initial install). The default is the number of cpus your computer has")
parser.add_argument("--port", "-t", help="The localhost port number you would like BLISTR to run on. The default is 5000", type=int)
parser.add_argument("--upload_paths", "-u", help="Sets the directories from where the user can upload fasta files to BLISTR. This takes n number of arguments. You can only upload fasta files from the directories you include here (or later include in config.py). The default is the fasta files directory from the root folder.", nargs='*')
parser.add_argument("--git", "-g", help="Git clones all the desired files from github (do not use this flag if you have already git cloned BLISTR by yourself).", action="store_true")
parser.add_argument("--FastaFiles", "-ff", help="Download the fasta files that built the BLISTR database from a git repository.", action="store_true")
parser.add_argument("--updatedb", "-udb", help="Tells the installer to only update your BLISTR.db, not create a new one from scratch (you likely should not use this function. This function is for updater.py)", action="store_true")
parser.add_argument("--retain", "-r", help="Set this flag if you do not want installer.py to remove itself after completing a sucsessful installlation.", action="store_true")
parser.add_argument("--verbose", "-v", help="Disply information about every step that is taking place during the install.", action="store_true")
args = parser.parse_args()


breaker = 0
while True and breaker == 0: #making the whole thing a loop so that I can break out at any point
    breaker += 1 #ensuring that this loop will not be run a second time
    
    #setting up all the variables to be used
    verbose = False
    if args.verbose:
        verbose = True
        print "Verbose set to True"
    programs_and_helpers = [("prokka","http://bioinformatics.net.au/prokka-manual.html"), ("blastn", "http://www.ncbi.nlm.nih.gov/books/NBK52640/")] #list of programs the user will need to have installed
    to_break = False
    for program, helper in programs_and_helpers:
        check = 'hash '+program+' 2>/dev/null || { echo >&2 "void";}' #fancy check for the program being installed
        if verbose:
            print "Checking if program '" + program + "' is installed via the command line call: " + check
        p = commands.getstatusoutput(check)[1] #this returns the result of the above bash command
        if p == "void":
            print colours.red + "Prgoram '" +program+"' has not been properly installed. See '"+helper+"' for installation details. Please install it and try again (see README.txt for more information)"+ colours.normal
            to_break = True #allowing errors for all 
    if to_break:
        break
    
    downloads = commands.getstatusoutput("xdg-user-dir DOWNLOAD")[1].rstrip("/") +"/" #spits out the path to a user's downloads directory
    if args.downloads:
        downloads = "/"+str(args.downloads).lstrip("/").rstrip("/")+"/" #need to make sure that / is there
        if not os.path.isdir(downloads):
            print colours.red + downloads + " is not a valid directory" + colours.normal
            break
    if verbose:
        print "Using Downloads path: " + downloads
    
    path = str(os.getcwd()) +"/"
    if args.path:
        path = "/"+str(args.path).lstrip("/").rstrip("/")+"/"
    if not os.path.isdir(path):
        try:
            os.mkdir(path) #if their directory does not exist, I will make it
        except:
            print colours.red + path + " is not a correct working directory" + colours.normal
            break
    if len(os.listdir(path)) > 0 and args.git: #True if the directory is not empty, which is unexceptable while trying a git download
        print colours.red + path + " is not an empty directory. Select a new directory or empty out your seleced one" + colours.normal
        break
    if verbose:
        print "Using working directory: " + path
        
    port = 5000
    if args.port:
        port = args.port
    if verbose:
        print "App will be deployable on localhost:" + str(port)
    
    p = subprocess.Popen("whoami", stdout=subprocess.PIPE)
    username = str(p.stdout.read().rstrip("\n")) #extracting the username of the installing computer (needed to link the database to the user account)
    p.wait()
    if verbose:
        print "Using computer username: " + username
    
    p = subprocess.Popen("nproc", stdout=subprocess.PIPE)
    cpus = int(p.stdout.read().rstrip("\n")) #extracting the username of the installing computer (needed to link the database to the user account)
    p.wait()
    if args.cpus and int(args.cpus) <= cpus: # ensuring the user did not enter more cpus than they have
        cpus = int(args.cpus)
    if verbose:
        print "Setting number of cpus to: " + str(cpus)
        
    install_easyfig = False
    easyfig = commands.getstatusoutput("which Easyfig.py")[1] #doing a quick call to get my easyfig path
    if args.easyfig:
        easyfig = "/"+str(args.easyfig).lstrip("/").rstrip("/").rstrip(".py")+".py"#if the user entered a path/to/easyfig for us, make sure it is formatted right
    if not os.path.isfile(easyfig): #if they don't have easyfig
        easyfig = path + "Easyfig/Easyfig.py" #setting the path to easyfig.py to be the one the easyfig.py installation will result in
        install_easyfig = True
    if verbose:
        print "Using " + easyfig + " as path to Easyfig.py program"
        
    install_quast = False
    quast = commands.getstatusoutput("which quast.py")[1]
    if args.quast:
        quast = "/"+str(args.quast).lstrip("/").rstrip("/").rstrip(".py")+".py"#if the user entered a path/to/quast for us, make sure it is formatted right
    if not os.path.isfile(quast): #if they don't have quast
        quast = path + "quast-2.3/quast.py" #setting the path to quast.py to be the one the quast.py installation will result in
        install_quast = True #variable to tell us to install quast later down the line
    if verbose:
        print "Using " + quast + " as path to quast.py program"
    
    
    dendroscope = path+"Database_Outputs/dendroscope/"
    if verbose:
        print "Setting '" + dendroscope + "' as path for Dendrocsope installation directory"
    
    upload_paths = [path+"fasta_files/"] #setting a minty default
    if args.upload_paths:
        upload_paths = args.upload_paths
        if not path+"fasta_files" in upload_paths and not path+"fasta_files/" in upload_paths and not "/"+path+"fasta_files" in upload_paths and not "/"+path+"fasta_files/" in upload_paths: #all the options accounted for
            upload_paths.append(path+"fasta_files/") #if they don't add my favourite default, I will put it in myself
    to_display = ""
    for upload_path in upload_paths:
        to_display += upload_path + ", "
    to_display = to_display.rstrip(", ")
    if verbose:
        print "Allowed upload paths set to: " + to_display
    
    
    ###########################################################################    
    #That bit where I git pull the information
    if args.git:
        if verbose:
            print "Git cloning from 'https://github.com/hc-BLISTR/BLISTR-main.git' into '" + path + "'"
        git_clone = "git clone https://github.com/hc-BLISTR/BLISTR-main.git "+path
        print colours.cyan + "Starting git clone:" + colours.normal
        process = subprocess.Popen(git_clone, shell=True)
        process.wait()
    
    if not os.path.isfile(path+"views.py"): #check to see if the given path checks out
        print colours.red + "Given path " + path + " does not contain BLISTR root directory files. Did you give the correct path/git install BLISTR?" + colours.normal
        break
    
    if args.FastaFiles:
        if verbose:
            print "Removing '"+path + "fasta_files/' directory"
        rmtree(path+"fasta_files/")
        if verbose:
            print "Making '"+path + "fasta_files/' directory"
        os.mkdir(path+"fasta_files/")
        if verbose:
            print "Git cloning fasta files from 'https://github.com/hc-BLISTR/BLISTR-fasta-files.git' into '" + path + "'fasta_files/"
        git_clone = "git clone https://github.com/hc-BLISTR/BLISTR-fasta-files.git "+path+"fasta_files/"
        process = subprocess.Popen(git_clone, shell=True)
        process.wait()
    
    
    ###########################################################################
    #this is the bit where I change all the hard coded paths in the files
    change_files_lists = [glob.glob(path+"*.py"), glob.glob(path+"BLISTR_support_programs/*.py"), glob.glob(path+"Database_Creation/*.py"), glob.glob(path+"Database_Inputs/*.py"), glob.glob(path+"Database_Outputs/*.py")]
    replacements_list = [("PATH/TO/Easyfig.py", easyfig), ("PATH/TO/quast.py", quast), ("PATH/TO/ROOT/", path), ("PATH/TO/DOWNLOADS/", downloads), ("postgresql://wolf:Halflife3", "postgresql://"+username+":Halflife3"), ("'--cpus 6'", "'--cpus "+str(cpus)+"'"), ("'--cpus 5'", "'--cpus "+str(cpus-1)+"'")] #All in the above list is of the format (find, replace). The cpus bit is for prokka optimization
    if args.port:
        replacements_list.append(("BLISTR.run(debug=False)", "BLISTR.run(debug=False, port="+str(port)+")"))
    iters = len(replacements_list)*len([item for sublist in change_files_lists for item in sublist]) #the total number of sed executions
    if not verbose: #if they wisely did not select verbose, they will get a very nice loading bar
        print colours.cyan + "Applying changes to files: " + colours.magenta
        with tqdm(total=iters) as pbar:
            for list_of_files in change_files_lists:
                for file_name in list_of_files:
                    for find, replace in replacements_list: #Awwwwwwww yeah, an excuse for a triple nested for loop
                        sed = "sed -i s#{find}#{replace}#g {file_name}".format(find=find, replace=replace, file_name=file_name) #find and replacing all hard roots with the user's
                        process = subprocess.Popen(sed, shell=True)
                        process.wait()
                        pbar.update(1)
        print "" + colours.normal
    else:
        for list_of_files in change_files_lists:
            for file_name in list_of_files:
                for find, replace in replacements_list: #Awwwwwwww yeah, an excuse for a triple nested for loop
                    print "Replacing {find} with {replace} in file {file_name}".format(find=find, replace=replace, file_name=file_name) #god, this is awful, who would ever use verbose?
                    sed = "sed -i s#{find}#{replace}#g {file_name}".format(find=find, replace=replace, file_name=file_name) #find and replacing all hard roots with the user's
                    process = subprocess.Popen(sed, shell=True)
                    process.wait()
    
    
    #modifying configs.py to have the proper upload paths
    if verbose:
        "Applying allowed upload paths: " + to_display + " to file: " + path+"config.py"
    uploads = "UPLOAD_PATHS = ["
    for upload_path in upload_paths:
        if not os.path.exists(upload_path):
            print colours.red + "NOTE: upload path '"+ upload_path + "' is currently an invalid directory. See config.py to make changes to upload directories if needed. This is not a major issue" + colours.normal
        uploads+= "'"+upload_path+"', "
    uploads =uploads.rstrip(", ")+"]"
    config = open(path+"config.py",'r')
    store = ""
    for line in config:
        if line.startswith("UPLOAD_PATHS"):
            line = uploads+"\n"
        store+=line
    config.close()
    config = open(path+"config.py",'w')
    config.write(store)
    config.close()
    
    #removing the gross .keep files from places
    if verbose:
        print "Removing file '"+path+"quast_results/.keep'"
    os.remove(path+"quast_results/.keep")
    if verbose:
        print "Removing file '"+path+"Database_Creation/Past_Databases/.keep'"
    os.remove(path+"Database_Creation/Past_Databases/.keep")
    if verbose:
        print "Changing directory to: "+path+"fasta_files/"
    os.chdir(path+"fasta_files/") #change into our fasta file directory
    process = subprocess.Popen('find . -name ".keep" -type f -delete', shell=True)
    process.wait()
    if verbose:
        print "Changing directory to: "+path
    os.chdir(path)
    
    ###########################################################################
    #install quast.py if needed
    if install_quast:
        track = 0
        programs = ["wget https://downloads.sourceforge.net/project/quast/quast-2.3.tar.gz", "tar -xzf quast-2.3.tar.gz", "python "+quast+" --test"] #all the command line calls needed to install this program
        for program in programs:
            if track == 2: #on the third run through we need to change our working directory to quast's
                if verbose:
                    print "Changing directory to: "+path+"quast-2.3/"
                os.chdir(path+"quast-2.3/")
            if verbose:
                print "Running: " + program
            proc = subprocess.Popen(program, shell=True)
            proc.wait()
            track += 1
        
        if verbose:
            print "Changing directory to: "+path
        os.chdir(path)
        if verbose:
            print "Removing 'quast-2.3.tar.gz' zip file"
        os.remove("quast-2.3.tar.gz") #remove the hideous tar ball
        
    #install easyfig.py if needed
    if install_easyfig:
        program = "git clone https://github.com/mjsull/Easyfig.git"
        if verbose:
            print "Running: " + program
        proc = subprocess.Popen(program, shell=True)
        proc.wait()        
    
    #The next bid does some checks and then installs dendroscope (from the copy that should have been included with the git clone)
    if not os.path.exists(dendroscope):
        os.mkdir(dendroscope)
    if not os.path.isdir(dendroscope):
        print colours.red + "Error, dendrocope folder in Database_Outputs directory not found" + colours.normal
        break
    if not os.path.exists(path+"Database_Outputs/Dendroscope_unix_3_5_7.sh"):
        print colours.red + "Error, dendrocope set up program 'Dendroscope_unix_3_5_7.sh' in Database_Outputs directory not found" + colours.normal
        break
    print colours.cyan + "Starting Dendroscope installation: " + colours.normal
    install = path+"Database_Outputs/Dendroscope_unix_3_5_7.sh -q -dir "+dendroscope
    process = subprocess.Popen(install, shell=True)
    process.wait()
    
    #TODO: add in the database dump
    #Setting up the BLISTR database by running db_loader.py (only if they git pulled our fasta files)
    if args.FastaFiles:
        if verbose: 
            print "Setting up the BLISTR.db database ..."
        if args.updatedb:
            program = "python "+path+"Database_Creation/db_loader.py -u"
        else:
            program = "python "+path+"Database_Creation/db_loader.py"
        proc = subprocess.Popen(program, shell=True)
        proc.wait()
    
    breaker += 1 #sets breaker to 2 for end output

if breaker == 2: #if all went well
    print colours.yellow + "To start the BLISTR server, in any terminal, run $ python "+path+"views.py"
    print "To use BLISTR in your browser, type in the URL 'http://localhost:"+str(port)+"/'" + colours.normal
    if not args.retain:
        os.chdir("../") #move one directory down
        if verbose:
            print "Deleating "+os.getcwd()+"/installer.py ..."
        proc = subprocess.Popen("rm "+os.getcwd()+"/installer.py", shell=True) #deletes this file
        print colours.cyan + "done" + colours.normal
        proc.wait()
    else:
        print colours.cyan + "done" + colours.normal
else:
    print colours.yellow + "Aborting" + colours.yellow