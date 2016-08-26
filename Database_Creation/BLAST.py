# -*- coding: utf-8 -*-
"""
Created on Mon May 30 09:32:05 2016

@author: Owen Neuber

Python application to execute local BLAST

Will run BLAST against all files from the directory: PATH/TO/ROOT/fasta_files
with relations to the Toxin, FlaA, and FlaB gene databases found in the respective directories:
PATH/TO/ROOT/fasta_files/databases/Toxin_db , PATH/TO/ROOT/fasta_files/databases/FlaA_db , 
PATH/TO/ROOT/fasta_files/databases/FlaB_db

The results from the BLAST will be stored in the folder: BLAST_outputs in the directory: 
PATH/TO/ROOT/fasta_files/BLAST_outputs
Inside this directory there will be three folders, Toxin_out, FlaA_out, and FlaB_out
where the outputs for the three different BLASTs will go.

Progess bars are used to track progress

NOTE: ENSURE THAT ALL FASTA FILE NAMES HAVE NO SPACES NOR SPECIAL CHARACTERS IN THEM
"""
import os
import subprocess
import glob
from tqdm import tqdm
from blessings import Terminal

colours = Terminal() #for terminal outputs with gorgeous colours!

def select_worse_toxin(line1, line2):
    """
    Function which determines which of two toxin hits is the worst.
    This is mostly based off of gaps and missmatches because they already 
    passed our len/slen and pident tests.
    Takes the complete blast result lines of two toxins already in list form
    Returns the list of the worse of the two.
    """
    gaps1, gaps2 = int(line1[7]), int(line2[7])
    mis1, mis2 = int(line1[6]), int(line2[6])
    if abs(gaps1-gaps2) > 5: #if the difference in gaps is greater than 5, that is too many for mismatches to make up for
        if gaps1 > gaps2:
            return line1
    elif abs(mis1-mis2) > 30: #if the difference in missmatches is greater than 30, that is too many
        if mis1 > mis2:
            return line1
    elif abs(gaps1-gaps2) > 3:
        if gaps1 > gaps2:
            return line1
    elif abs(mis1-mis2) > 15:
        if mis1 > mis2:
            return line1
    elif abs(gaps1-gaps2) > 2:
        if gaps1 > gaps2:
            return line1
    elif mis1 > mis2:
        return line1
    
    return line2 #if line 1 can't lose the contest, then it must be line 2
    
def is_overlapping(line1, line2):
    """
    Function which determies if two toxins are overlapping in position.
    Takes the two toxin line lists.
    Returns True if the two toxins are overlapping, false otherwise.
    """
    start_dif = abs(int(line1[8]) - int(line2[8]))
    end_dif = abs(int(line1[9]) - int(line2[9]))
    middle1 = (int(line1[9]) + int(line1[8]))/2
    middle2 = (int(line2[9]) + int(line2[8]))/2
    if start_dif < 500:
        return True
    elif end_dif < 500:
        return True
    elif middle1 < int(line2[9]) and middle1 > int(line2[8]): #the middle of 1 is smaller in value than the end of 2 but larger than 2's start
        return True
    elif middle2 < int(line1[9]) and middle2 > int(line1[8]):
        return True
    return False #if it passes all the tests, return False
    
def order_list_of_toxins(list_of_lines):
    """
    Function that takes in a list of good hit toxin data and then 
    sorts the list in order of quality (best to worst). This sorted
    list is the return of this function.
    This sort will not bee too eficient as there is only one known
    case where the genome had over 2 toxins
    """
    num_lines = len(list_of_lines)
    if num_lines < 2: #if there is nothing to sort
        pass #nothing to do here and I just really want to use the pass keyword
    elif num_lines == 2:
        loser = select_worse_toxin(list_of_lines[0], list_of_lines[1])
        list_of_lines.remove(loser) #removing the loser from which ever point in the list it was
        list_of_lines.append(loser) #then adding it back in (to the end of the list)
    else: # num_lines > 2
        check = False
        current_line = 0
        temp = ""
        change = True
        while change:
            if current_line == num_lines-1:
                current_line = 0
                if not check: #if no changes were maade during a full run through, end it
                    break
                check = False #reset the check variable so that it must be set to True again by a change occuring
                continue
            if list_of_lines[current_line] == select_worse_toxin(list_of_lines[current_line], list_of_lines[current_line+1]): #this logic statement seems wrong to me, but it gives the correct result in practice so whatever
                temp = list_of_lines[current_line+1] #store the value of the next line
                list_of_lines[current_line+1] = list_of_lines[current_line]
                list_of_lines[current_line] = temp #the two lines have been swapped
                check = True #keeps tract of if a change was made this full run through
            current_line += 1 #always increasing unless it hits the end of the list
            
    return list_of_lines
    

counter = -1 #counter to keep database and out_dirs lists in parallel

LENSLEN = 0.9 #the thresholds on the blast results
PIDENT = 90

files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
num_files = float(len(files))
#Check against current files to prevent time consuming repeats
current_files_tox = glob.glob('PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/*')
current_files_flaA = glob.glob('PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaA_out/gene_extended/*')
current_files_flaB = glob.glob('PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaB_out/gene_extended/*')
current_files = [current_files_tox, current_files_flaA, current_files_flaB] #set up to be a parallel list to databases

#list of wherethe 10 000bp extended contings will be held
extended_fastas = ['PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaA_out/gene_extended/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaB_out/gene_extended/']

#list of all our databases (should likely be replaced with the actual database from Nick)
databases = ["PATH/TO/ROOT/fasta_files/databases/Toxin_db/BoNT_sequences.fasta", "PATH/TO/ROOT/fasta_files/databases/FlaA_db", "PATH/TO/ROOT/fasta_files/databases/FlaB_db"]
out_dirs = ['PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaA_out/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaB_out/']


for database in databases:
    counter += 1
    #TODO: remove this continue when other databases have been loaded up
    if counter > 0: #I only have the NoTN database to play with right now. Take out when FlaA&B databases are added
        continue
    if counter == 0:
        print colours.cyan + "Processing the toxin database:" + colours.magenta
    elif counter == 1:
        print colours.cyan + "Processing the FlaA database:" + colours.magenta
    else:
        print colours.cyan + "Processing the FlaB database:" + colours.magenta
        
    with tqdm(total=num_files) as pbar: #setting up the sweetest progressbar
        for fasta in files:            
            file_name = os.path.basename(fasta)[:-6] #extracts the filename of the file being processed & removes the last 6 character (i.e. '.fasta')
            
            if extended_fastas[counter]+file_name+".blast.fasta" in current_files[counter] or extended_fastas[counter]+file_name+".no_hits" in current_files[counter]: #checks the current fasta to be processed against ones already processed. It can only be done against the whole path so that is why this if statement is so disgusting
                pbar.update(1) #can't forget to update that sexy loadin bar
                continue #if it has already been processed, skip it            
            
            BLAST_outputs = out_dirs[counter] + file_name + ".tsv" #sets up the correct output directory, parallel to the database being processed
                    
            cmdln = "blastn -query " + fasta + " -db " + databases[counter] + " -outfmt '6 qseqid stitle qlen slen length pident mismatch gaps qstart qend qseq sstrand' > " + out_dirs[counter] + file_name + ".blast.tsv"
        
            process = subprocess.Popen(cmdln, shell=True) #executes the desired program
            process.wait() #waits until the command has finished processing before ending
            
            x = os.path.getsize(out_dirs[counter] + file_name + ".blast.tsv") #checking if a file is empty and if it is, creating a new empty file to display this
            if x ==0:
                out_file = open(extended_fastas[counter] + file_name + ".no_hits", 'w')
                out_file.write("No hits")
            else: #very ugly but it seems to be the only solution to the wierdest problem ever

                #Now we start the part where we get the 10 000bp before and the 10 000bp after       
                blast_file = open(out_dirs[counter] + file_name + ".blast.tsv", 'r') 
                original_fasta = open(fasta, 'r')
                out_file = open(extended_fastas[counter] + file_name + ".blast.fasta", 'w') #writes to a new file where the extended contig will be stored   
                lines_we_care_about = []
                for line in blast_file: 
               
                    first = line
                    line = line.split("\t") #make the first line of tsv into a list
                    #quality variables
                    slen = float(line[3])
                    length = float(line[4])
                    pident = float(line[5])
                    #######################################
                    #we don't want no stinking trash reads#
                    if (length/slen) > LENSLEN and pident >= PIDENT: #if the line's metadata sucks, then we toss everything about that line into the abyss
                        num_to_compare = len(lines_we_care_about)
                        counter117 = 0
                        if num_to_compare > 0:
                            for compare_line in lines_we_care_about: #compare the newly cleared line against all other cleared lines to avoid douplicates with the same indexes
                                counter117 +=1
                                if line is compare_line: #avoid odd duplicates
                                    break
                                if is_overlapping(line, compare_line):
                                    loser = select_worse_toxin(line, compare_line)
                                    if loser is line: #if our current line loses, stop this maddness and go on to the next line to find a true champion!
                                        break
                                    lines_we_care_about.remove(loser) #If the toxins are overlapping, remove the worse of the two   
                                    lines_we_care_about.append(line) #if the new line passes all the tests, add it to our list
                                    break
                                    
                                if counter117 == num_to_compare: #if our line makes it through the long haul, add it in
                                    lines_we_care_about.append(line)
                        else:
                            lines_we_care_about.append(line)
                            
                lines_we_care_about = order_list_of_toxins(lines_we_care_about) #sort our lines so that the things are ordered approprietly
                        
                for line in lines_we_care_about:
                    #If everything checks out, set up regular outfile                    
                    contig_num = int(line[0].split(",")[0]) #extract the contig number from the title of the first line
                    contig_size = int(line[2])
                    start_index = int(line[8]) #all these lines are impoted as string type, so we need to change these numbers to int type
                    end_index = int(line[9])
                    sstrand = line[11] #This one needs to be 'plus'
                    
                    #determine how many bp before the toxin we can start. start is our starting index (for splicing purposes)
                    start = start_index - 10000
                    if start < 0: #if the above is negative, start at bp zero
                        start = 0
                    num_before = start_index - start #the number of bp we managed to get ahead of the toxin 
                    
                    #determine how many bp after the toxin we can end. end is our ending index (for splicing purposes)
                    end = end_index + 10000
                    if end > contig_size: #if the ending index point is larger than our contig size, it will be reduced just to the end of the contig
                        end = contig_size 
                    num_after = end - end_index #the number of bps we got extra after the toxin
                    
                    #now we find the original file hosting the toxin, find the contig the toxin is held in, and output how much 
                    #before and after this contig we want (in one line to please the almighty postgres)
                    run = False #if run is set true, we will start recording the contig to a string
                    full_contig = ""
                    for l in original_fasta:
                        if run and l.startswith('>'): #if run is already true, then we have already extracted our contig (as we would only enter this space again if the line started with ">")
                            run = False
                            break
                        
                        elif l.startswith('>') and int(l.split(",")[0][1:]) == contig_num: #if the line starts with a ">" tag and the contig number at the start of that line is the contig we want, then set run to true
                            run = True
                        
                        elif run:
                            full_contig = full_contig + l.rstrip("\n") #concatenate all the lines while removing the endlines
                            
                        else: #if we have not started extracting our contig, skip the current line
                            continue
                    original_fasta.close() #need to close and re-open this so that new searches may start from the top of the file
                    original_fasta = open(fasta, 'r')
                    
                    up_down_toxin = full_contig[start:end] #extracting only the desired bps before and after the toxin
                    
                    #If the toxin is in the minus direction, we must reverse it
                    if sstrand.rstrip("\n") == "minus":
                        num_before, num_after = num_after, num_before #switch the values of bp_before/after because revcomp filps the whole sequcence. Thus the toxin poisition changes (unless bp_before/after were equal, of course)
                        temp = open(out_dirs[counter]+'temp/temp.fasta', 'w')
                        temp.write(">This,is,just,a,formality \n" + up_down_toxin)
                        temp.close()
                        revcomp = "PATH/TO/ROOT/BLISTR_support_programs/./revcomp "+out_dirs[counter]+"temp/temp.fasta > "+out_dirs[counter]+"temp/temp.rev.fasta"
                        process = subprocess.Popen(revcomp, shell=True) #creates a temp.rev.fasta file that will hold the reversed sequences
                        process.wait()
                        temp = open(out_dirs[counter]+"temp/temp.rev.fasta", 'r')
                        f_line = 0
                        up_down_toxin = ""
                        for q in temp: #for line in temp
                            if f_line == 0: #skip the first line
                                f_line += 1
                                continue
                            up_down_toxin = up_down_toxin + q.lstrip("\n").rstrip("\n") #effectivly reverses the toxin sequence
                        temp.close()
                    to_write = ">" + line[0] + "\t" + line[1] + "\t" + str(num_before) + "\t" + str(num_after) + "\n" + up_down_toxin + "\n"#adding the expanded toxin gene to the original blast tsv for the desired end result
                    
                    out_file.write(to_write) #actually writing to file
            
                blast_file.close()
                out_file.close()
                if os.path.getsize(extended_fastas[counter] + file_name + ".blast.fasta") == 0: #if the output file is empty
                    os.rename(extended_fastas[counter] + file_name + ".blast.fasta", extended_fastas[counter] + file_name + ".no_hits")
                original_fasta.close() 
            pbar.update(1)
