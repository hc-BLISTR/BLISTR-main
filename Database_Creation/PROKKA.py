# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 10:27:27 2016

@author: Owen Neuber

Program that will run PROKKA and easyfig. PROKKA against both the full toxin
fasta and the toxin++ with easyfig against only the result from PROKKA on 
toxin++.

If the PROKKA result of a fasta file is already present, the PROKKA call will
not run on the genome.
Independent of the above, If the PROKKA result of a toxin++ file is already present, 
the PROKKA call will not run on the toxin.
(So if you want to run a fresh PROKKA on something where PROKKA has already been run,
just delete the proper toxin or fasta PROKKA folders and then run this program)

The result folders are stored in the directories:
PATH/TO/ROOT/fasta_files/PROKKA/fasta/
PATH/TO/ROOT/fasta_files/PROKKA/tox/
"""

import os
import subprocess
import glob
from tqdm import tqdm
from blessings import Terminal
from shutil import copyfile

colours = Terminal() #for terminal outputs with gorgeous colours!


def list_of_toxins(path, file_name):
    """
    Function that takes the full path to a fasta toxin file. It will then 
    determine the number of toxins in the file. It will then make a new temp
    file for evey toxin in the file (if more than on toxin, else it will return
    the orginal path it was given, in list form) and return the path to these
    files in list/tuple form with the desired file names appended to the tuple.
    """
    toxin = open(path, 'r')
    temp = []
    output =[]
    hold = ""
    counter = 0
    for item in toxin:
        if (counter % 2) == 1: #if counter is an odd number
            temp.append((hold,item)) #adding in the current 2 line pair to the list as a tuple
        counter += 1
        hold = item
    toxin.close()
    if len(temp) == 1: #if there is only one toxin
        return [(path,file_name)] #path in list form
    counter2 = 0
    for metadata, seq in temp:
        counter2 += 1
        temp_file = open('PATH/TO/ROOT/fasta_files/PROKKA/temp/temp'+str(counter2), 'w')
        temp_file.write(metadata + seq ) #metadata and seq should already have newlines on them
        temp_file.close()
        output.append(('PATH/TO/ROOT/fasta_files/PROKKA/temp/temp'+str(counter2), file_name+"."+str(counter2))) #(path, genomename.2)
    return output        
        

files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
num_files = float(len(files))
#Check against current files to prevent time consuming repeats
current_dirs = glob.glob('PATH/TO/ROOT/fasta_files/PROKKA/fasta/*')
current_tox_dirs = glob.glob('PATH/TO/ROOT/fasta_files/PROKKA/tox/*')
outdir = "PATH/TO/ROOT/fasta_files/PROKKA/fasta/"
tox_outdir = "PATH/TO/ROOT/fasta_files/PROKKA/tox/"

#list of wherethe 10 000bp extended contings will be held
extended_fasta = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/'


print colours.cyan + "Running PROKKA:" + colours.magenta
with tqdm(total=num_files) as pbar: #setting up the sweetest progressbar
    for fasta in files:          
        
        file_name = os.path.basename(fasta)[:-6]
        toxin_file = extended_fasta+file_name+'.blast.fasta'
        
        if not outdir+file_name in current_dirs: #check if the current file in question has already had a PROKKA run done on it. If so, don't run PROKKA on the genome (though check the toxin still)
            prokka = "prokka --outdir "+outdir+file_name+" --prefix "+file_name+".fasta --cpus 6 --quiet --force "+fasta
            process = subprocess.Popen(prokka, shell=True)
            process.wait() #Run proka on the file (full fasta)
        
        if os.path.isfile(toxin_file) and not tox_outdir+file_name in current_tox_dirs and not tox_outdir+file_name+".1" in current_tox_dirs: #making sure the toxin file was not a .no_hits and has not alreay been done (the .1 check is for multi toxin hits)

            for toxin_file, file_name in list_of_toxins(toxin_file, file_name):
                
                prokka_tox = "prokka --outdir "+tox_outdir+file_name+" --prefix "+file_name+".toxin --cpus 6 --quiet --force "+toxin_file
                process = subprocess.Popen(prokka_tox, shell=True)
                process.wait()
                
                headers = []  #list of all the products in the .gbk file and the number of similar entries
                par_numbers = [] #list containing numbers which acts parallel to headers
                hypo_prot_in = open(tox_outdir+file_name+"/"+file_name+".toxin.gbk", 'r')
                hypo_prot_out = '' #initializing variable to store an entire file in temparaily
                for line in hypo_prot_in:
                    if line.lstrip(" ").startswith("/product="):
                        header = line.split('"')[1] #exctract the header from a line like: /product="Clostridium P-47 protein"
                        if header in headers:
                            index = headers.index(header) #the index of where the header line is (to find the corresponding number in the parallel list)
                            par_numbers[index] += 1 #increase the list number
                            line = line.replace(header, header+str(par_numbers[index]))
                        else:
                            headers.append(header) #if it is not in our list yet, add it
                            par_numbers.append(1) #and add in a parallel number (of value one as it is the first entry)
                    hypo_prot_out = hypo_prot_out + line
                hypo_prot_in.close()
                remade = open(tox_outdir+file_name+"/"+file_name+".toxin.gbk", 'w')
                remade.write(hypo_prot_out)
                remade.close()
                
                easyfig = "python PATH/TO/Easyfig.py -filter -legend single -leg_name product -ann_height 200 -glt 15 -f CDS 173 216 230 arrow -o "+tox_outdir +file_name+"/img "+tox_outdir+file_name+"/"+file_name+".toxin.gbk"
                process = subprocess.Popen(easyfig, shell=True)
                process.wait() #Run this against the result from toxin++
                copyfile(tox_outdir +file_name+"/img", 'PATH/TO/ROOT/static/images/'+file_name+'.bmp') #Copy the outputted image to the static folder
                subprocess.call("clear") #easyfig is annoying and has an output so this should clean that up
                
                try:
                    pls_remove = glob.glob(tox_outdir+file_name+'/*')
                    for fi in pls_remove: #remove toxin related files
                        if os.path.basename(fi) == "img" or os.path.basename(fi).split(".toxin.")[1] == "gbk" or os.path.basename(fi).split(".toxin.")[1] == "faa" or os.path.basename(fi).split(".toxin.")[1] == "ffn" or os.path.basename(fi).split(".toxin.")[1] == "gff":
                            continue
                        os.remove(fi) #removes all the files we do not care about (i.e. not .gbk, ffa, ffn, gff)
                except:
                    print colours.red + "Error deleting suplimental toxin files of: " + file_name + colours.magenta           
        
        try:
            pls_remove = glob.glob(outdir+file_name+'/*')
            for fi in pls_remove: #remove dasta related files
                if os.path.basename(fi).split(".fasta.")[1] == "gbk" or os.path.basename(fi).split(".fasta.")[1] == "faa" or os.path.basename(fi).split(".fasta.")[1] == "ffn" or os.path.basename(fi).split(".fasta.")[1] == "gff":
                    continue
                os.remove(fi) #removes all the files we do not care about (i.e. not .gbk, ffa, ffn, gff)
        except:
            print colours.red + "Error deleting suplimental fasta files of: " + file_name + colours.magenta 
        
        pbar.update(1)

