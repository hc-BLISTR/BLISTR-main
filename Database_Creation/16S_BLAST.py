# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 08:41:28 2016

@author: Owen Neuber

Program to run a 16S BLAST call against files in the folder:
PATH/TO/ROOT/fasta_files The BLAST database to be used is:
"PATH/TO/ROOT/fasta_files/databases/16S_db/16s_contigs.fasta"
and the outputs of this program will go to the directory:
'PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out/'

The top 5 hits will be considered and of those hits, only results with 
lenth/slen >= 0.85 and pident >= 85% will be considered.

"""

import os
import subprocess
import glob
from tqdm import tqdm
from blessings import Terminal

colours = Terminal() #for terminal outputs with gorgeous colours!

files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
num_files = float(len(files))
#Check against current files to prevent time consuming repeats
current_files = glob.glob('PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out/*')

database = "PATH/TO/ROOT/fasta_files/databases/16S_db/16s_contigs.fasta"
out_dir = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out/'

LENSLEN = 0.85
PIDENT = 85.0


print colours.cyan + "Processing the 16S database:" + colours.magenta
with tqdm(total=num_files) as pbar: #setting up the sweetest progressbar
    for fasta in files:
        file_change = False
        file_name = os.path.basename(fasta)[:-6] #extracts the filename of the file being processed & removes the last 6 character (i.e. '.fasta')
        
        if out_dir+file_name+".blast.tsv" in current_files or out_dir+file_name+".no_hits" in current_files: #checks the current fasta to be processed against ones already processed. It can only be done against the whole path so that is why this if statement is so disgusting
            pbar.update(1) #can't forget to update that sexy loadin bar
            continue #if it has already been processed, skip it      
        
        
        BLAST_outputs = out_dir + file_name + ".tsv" #sets up the correct output directory, parallel to the database being processed
                
        cmdln = "blastn -query " + fasta + " -db " + database + " -max_target_seqs 5 -outfmt '6 qseqid stitle qlen slen length nident pident mismatch gaps qstart qend sstrand qseq' > " + out_dir + file_name + ".blast.tsv"
        process = subprocess.Popen(cmdln, shell=True) #executes the desired program
        process.wait() #waits until the command has finished processing before ending
        
        
        
        blast_file = open(out_dir + file_name + ".blast.tsv", 'r') 
        line_num = 0
        counter = 0
        current = []
        rev = {}
        for line in blast_file:
            current.append("") #to make our current list match whatever number of rows our file may have
            current[counter] = line
            line = line.split("\t") #make the first line of tsv into a list
            #quality variables
            slen = float(line[3]) #extracting data from the quast results
            length = float(line[4])
            pident = float(line[6])
            sstrand = line[11]
            if length/slen < LENSLEN or pident < PIDENT: #checking if our stuff does not pass our requirements
                current[counter] = None #if not, set it to none
                current.remove(None) #then remove entrys set to None
                counter -= 1 #set our counter back one (to account for removing an entry from our list)
                file_change = True #Tell the program that the file will need to be changed (i.e. some of the top 5 removed). We do this only in the event of failure to reduce on required processing
            elif sstrand != "plus": #if we have the minus strand that is bad news bears so we must note that for changes. It is an elif because we don't want to bother flipping sequences if they are not worthy
                rev.update({line_num:line[12]}) #{counter: qseq}
            line_num +=1
                         
            counter += 1
        blast_file.close()
        
        #The following is for flipping the genetic code
        if rev: #if the reverse dictionary has been populated
            temp = open(out_dir+'temp/temp.fasta', 'w')
            for num in rev: #write the name as the line number (1-5)
                temp.write(">"+str(num)+"\n"+str(rev.get(num))+"\n")
            temp.close()
            revcomp = "PATH/TO/ROOT/BLISTR_support_programs/./revcomp "+out_dir+"temp/temp.fasta > "+out_dir+"temp/temp.rev.fasta" #rub revcomp
            process = subprocess.Popen(revcomp, shell=True) #creates a temp.rev.fasta file that will hold the reversed sequences
            process.wait()
            temp = open(out_dir+"temp/temp.rev.fasta", 'r')
            count = -1 #counter to skip the first line
            seq = ""
            first_num = -1 #place holder
            replace ={}
            for l in temp:
                if l.startswith(">"):
                    if count != -1:
                        replace.update({first_num: seq}) #add the newly flipped sequence to our dictionary with a key corresponding to its contig number
                        seq = "" #can't forget to reset seqence to nothing for the next contig
                    first_num = int(l.lstrip(">"))
                    count += 1
                    continue
                seq = seq+l.rstrip("/n")
            replace.update({first_num: seq}) #can't forget about that last sequence to add
            temp.close()
            blast_file = open(out_dir + file_name + ".blast.tsv", 'w')  #now for the bit where I actually fix this problem
            count = 0
            for line in current:
                if replace.get(count):
                    old_seq = line.split("\t")[12] #extract our old sequence (only to be replaced)
                    line = line.replace(old_seq, replace.get(count).replace("\n","")) #swap out the minus sequence with the plus sequence
                    line = line.replace("minus", "reversed to plus") #just a little note so you know
                blast_file.write(line+"\n")
                count += 1
            blast_file.close()
        
        if file_change: #if one of our results is bad, we will have to recreate the file
            blast_file = open(out_dir + file_name + ".blast.tsv", 'w') 
            for line in current:
                blast_file.write(line)
            blast_file.close()                
                
        x = os.path.getsize(out_dir + file_name + ".blast.tsv") #checking if a file is empty and, if it is, renaming the empty file to reflect this
        if x ==0:
            os.rename(out_dir + file_name + ".blast.tsv", out_dir + file_name + ".no_hits")
            out_file = open(out_dir + file_name + ".no_hits", 'w')
            out_file.write("No hits")
            out_file.close()

        pbar.update(1)
