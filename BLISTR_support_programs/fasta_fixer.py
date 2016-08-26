# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 10:29:33 2016

@author: Owen Neuber

program that will take an ncbi lowercase fasta set with numbered lines and 
remove the numbers, spaces and make it uppercase. For example:
   14 atgaaa ataaataata attttaatat tgattctcta atagataata
   952741 gagatgtagc aattgttagg ggtagaaaaa cagatacttt ttttaaagta tttcaagtgg
   952801 ctcccaatat ctggattgcc ccagaaagat attatggaga atcattaaat ataaatgaag
   952861 atcaaaaatc tgacggagga atttatgatt ctaattttct ttcaacaaat gacgaaaaag
Would become:
ATGAAAATAAATAATAATTTTAATATTGATTCTCTAATAGATAATA
GAGATGTAGCAATTGTTAGGGGTAGAAAAACAGATACTTTTTTTAAAGTATTTCAAGTGG
CTCCCAATATCTGGATTGCCCCAGAAAGATATTATGGAGAATCATTAAATATAAATGAAG
ATCAAAAATCTGACGGAGGAATTTATGATTCTAATTTTCTTTCAACAAATGACGAAAAAG
"""

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("input_file", help="The path to the file which you would like to apply this program to in the form: path/to/file_to_change.fasta")
parser.add_argument("output_file", help="The path (including file name) to where you would like the result of this program to be written in the form: path/to/output_file.fasta (cannot be the same file as the input file)")
args = parser.parse_args()

old_file = str(args.input_file)
fixed_file = str(args.output_file)

if not os.path.isfile(old_file):
    print "The input file given does not have a valid path."
    assert(False) #break the program

if old_file == fixed_file:
    print "The output file cannot be the same as the input file."
    assert(False)

fasta = open(old_file, 'r') #original
new = open(fixed_file, 'w')

for line in fasta:
    if line.startswith(">") or line.startswith("\n"): #Fasta start lines are always okay and so are blank lines
        new.write(line)
        continue
    cut_line = line.lstrip(" ").split(" ")
    try:
        int(cut_line[0]) #if this is okay, then we have one of those lines with the number followed by lowercase letters separaaated by spaces
    except:
        new.write(line)
        continue #if it is not okay, then we have a regular fasta line which does not need changing
        
    line = line.lstrip(" ").lstrip(cut_line[0]).replace(" ", "").upper()
    new.write(line)

fasta.close()
new.close()

os.remove(old_file)
os.rename(fixed_file, old_file)
