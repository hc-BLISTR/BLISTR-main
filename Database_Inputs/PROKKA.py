# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 10:27:27 2016

@author: Owen Neuber

Program that will run PROKKA and easyfig. PROKKA against both the full toxin
fasta and the toxin++ with easyfig against only the result from PROKKA on 
toxin++. This file should be run against newly entered files uploaed via BLISTR

If you have PROKKA running in the background of BLISTR, do not make changes to 
the backend as that will crash the app.
"""

import os
import subprocess
import glob
from blessings import Terminal
from shutil import copyfile

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("URL", help="The URL to the file we want to retrive information about")
parser.add_argument("--solo", "-s", help="Tells this program that it will have to upload information to the database itself", action="store_true")
parser.add_argument("--genome", "-g", help="The name of the genome this PROKKA action is based around")
args = parser.parse_args()
URL = args.URL

colours = Terminal() #for terminal outputs with gorgeous colours!

def list_of_toxins(path, file_name):
    """
    Function that takes the full path to a fasta toxin file. It will then 
    determine the number of toxins in the file. It will then make a new temp
    file for evey toxin in the file (if more than one toxin, else it will return
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


outdir = "PATH/TO/ROOT/fasta_files/PROKKA/fasta/"
tox_outdir = "PATH/TO/ROOT/fasta_files/PROKKA/tox/"

#list of wherethe 10 000bp extended contings will be held
extended_fasta = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/'

           
file_name = os.path.basename(URL)[:-6]
toxin_file = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/'+file_name+'.blast.fasta'

prokka = "prokka --outdir "+outdir+file_name+" --prefix "+file_name+".fasta --cpus 6 --quiet --force "+URL
if args.solo:
    prokka = "prokka --outdir "+outdir+file_name+" --prefix "+file_name+".fasta --cpus 5 --quiet --force "+URL #if running as a background process, keep it quiet
process = subprocess.Popen(prokka, shell=True)
process.wait() #Run proka on the file


if os.path.isfile(toxin_file): #making sure the toxin file was not a .no_hits
    for toxin_file, file_name in list_of_toxins(toxin_file, file_name):
        prokka_tox = "prokka --outdir "+tox_outdir+file_name+" --prefix "+file_name+".toxin --cpus 5 --quiet --force "+toxin_file
        process = subprocess.Popen(prokka_tox, shell=True)
        process.wait()
        
        headers = []  #list of all the products in the .gbk file and the number of similar entries
        par_numbers = [] #list containing numbers which acts parallel to headers
        #counter = 1 #need to replace all "hypothetical protein" with "hypothetical protein[counter]"
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
        remade.write(hypo_prot_out) #rewrite the file with our changes
        remade.close()
        
        easyfig = "python PATH/TO/Easyfig.py -filter -legend single -leg_name product -ann_height 200 -glt 15 -f CDS 173 216 230 arrow -o "+tox_outdir +file_name+"/img "+tox_outdir+file_name+"/"+file_name+".toxin.gbk"
        process = subprocess.Popen(easyfig, shell=True)
        process.wait() #Run this against the result from toxin++
        
        try:
            genome_name = str(args.genome)+"."+file_name.split(".")[1] #take the second instance in this list (which would be the counter number (i.e. temp.1 <-- in the case of multiple toxins))
        except:
            genome_name = str(args.genome)
        copyfile(tox_outdir +file_name+"/img", 'PATH/TO/ROOT/static/images/'+genome_name+'.bmp') #Copy the outputted image to the static folder
        
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
    
if args.solo: #will upload the PROKKA information immediatly after the PROKKA finishes running
    #it is this feature that allows PROKKA to run in the background and still be uploaded to the db after being completed independently of processor.py
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from models import Genome, Prokka, Toxin
    engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
    Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session/allow session.add()
    session = Session()
    
    path_f_prokka = 'PATH/TO/ROOT/fasta_files/PROKKA/fasta/'
    path_t_prokka = 'PATH/TO/ROOT/fasta_files/PROKKA/tox/'
    file_name = os.path.basename(URL)[:-6] #file_name has since been changed and thus needs to be redefined
    add_bool = True
    
    g_id = int(session.query(Genome).filter_by(name=str(args.genome)).first().id)
    #take one liners of the prokka fasta files
    f_faa = open(path_f_prokka+file_name+"/"+file_name+".fasta.faa")
    out_f_faa = ""
    for p in f_faa:
        out_f_faa = out_f_faa + p # We want to keep the newlines in there for later extration formating
    f_faa.close()
    f_ffn = open(path_f_prokka+file_name+"/"+file_name+".fasta.ffn")
    out_f_ffn = ""
    for a in f_ffn:
        out_f_ffn = out_f_ffn + a
    f_ffn.close()
    #Check if the toxin folder exists
    if os.path.isdir(path_t_prokka+file_name):
        tox_exists = True
        t_faa = open(path_t_prokka+file_name+"/"+file_name+".toxin.faa")
        out_t_faa = ""
        for p in t_faa:
            out_t_faa = out_t_faa + p
        t_faa.close()
        t_ffn = open(path_t_prokka+file_name+"/"+file_name+".toxin.ffn")
        out_t_ffn = ""
        for a in t_ffn:
            out_t_ffn = out_t_ffn + a
        t_ffn.close()
        #Now that the toxin data has been extracted, we have to remove their temp files
        #this process has been moved to orfX_HA_BLAST.py
        
    elif  os.path.isdir(path_t_prokka+file_name+".1"): #checking if we have a fabled multi fata result
        tox_exists = True
        out = ""
        toxins_prokka_path = glob.glob(path_t_prokka+file_name+".[0-9]*") #this will be a list off all the files with the desired name.number
        toxins_prokka_path.sort()
        for path in toxins_prokka_path: #need to reverse the order of the list so that the older files (lower numbers) show up first
            num = os.path.basename(path).split(".")[-1] #extracts the number our current iteration is on
            t_faa = open(path+"/"+file_name+"."+num+".toxin.faa")
            out_t_faa = ""
            for p in t_faa:
                out_t_faa = out_t_faa + p
            t_faa.close()
            t_ffn = open(path+"/"+file_name+"."+num+".toxin.ffn")
            out_t_ffn = ""
            for a in t_ffn:
                out_t_ffn = out_t_ffn + a
            t_ffn.close()
            add = Prokka(fasta_faa=out_f_faa, fasta_coding_genes=str(out_f_faa).count(">"), fasta_ffn=out_f_ffn, fasta_ORFs=str(out_f_ffn).count(">"), tox_exists=tox_exists, tox_faa=out_t_faa, tox_coding_genes=str(out_t_faa).count(">"), tox_ffn=out_t_ffn, tox_ORFs=str(out_t_ffn).count(">"), genome_id=g_id) #add it on the spot so we don't have to use eval
            session.add(add)
            session.commit()
            
            #Now that the toxin files have been added, we have to remove their temp files
            #this process has been moved to orfX_HA_BLAST.py
        add_bool = False
    else:
        tox_exists = False
        out_t_faa = None
        out_t_ffn = None
    
    if add_bool: #to make sure we don't add the multiple option again
        add = Prokka(fasta_faa=out_f_faa, fasta_coding_genes=str(out_f_faa).count(">"), fasta_ffn=out_f_ffn, fasta_ORFs=str(out_f_ffn).count(">"), tox_exists=tox_exists, tox_faa=out_t_faa, tox_coding_genes=str(out_t_faa).count(">"), tox_ffn=out_t_ffn, tox_ORFs=str(out_t_ffn).count(">"), genome_id=g_id)
        session.add(add)
        session.commit()
        
        
    print colours.cyan + "Finished PROKKA" +colours.normal
    
    orfX_HA_BLAST = "python PATH/TO/ROOT/Database_Inputs/orfX_HA_BLAST.py -c " + URL #now that prokka is done, run orf/ha blast
    process = subprocess.Popen(orfX_HA_BLAST, shell=True)
    process.wait()
    
    
    ts = session.query(Toxin).filter_by(genome_id=g_id).all()
    counter28 = 0 #counter to keep track of which toxin we are working on (for naming it)
    orfx_ha_file_path = "PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/data/"
    for t in ts:
        counter28 += 1
        if len(ts) > 1: #if we have multiple toxins, we will have the temp.number naming scheme
            try:
                orfx_ha_file = open(orfx_ha_file_path+file_name+"."+str(counter28)+".no_hits", 'r') #try to use the no hits and if not, we will use the proper one
                t.orfx_ha = "None"
                session.add(t)
                session.commit()
                orfx_ha_file.close()
                os.remove(orfx_ha_file_path+file_name+"."+str(counter28)+".no_hits") #need to keep things clean
                continue #we do not want to consider anything more
            except:
                to_remove = orfx_ha_file_path+file_name+"."+str(counter28)+".orfX_HA.tsv"
                orfx_ha_file = open(to_remove, 'r') #open up our orfx_ha files
        else:
            try: #hope to fail on this one so that we use the proper toxin file, otherwise oh well, to the next iteration
                orfx_ha_file = open(orfx_ha_file_path+file_name+".no_hits", 'r') #if we can read this without error, then we know this is the case
                t.orfx_ha = "None"
                session.add(t)
                session.commit()
                orfx_ha_file.close()
                os.remove(orfx_ha_file_path+file_name+".no_hits") 
                continue #we do not want to do any orfx_ha manipulations on a .no_hit file
            except:
                to_remove = orfx_ha_file_path+file_name+".orfX_HA.tsv"                          
                orfx_ha_file = open(to_remove, 'r') #the proper toxin file
        for pickles_of_15_years in orfx_ha_file: #pickles_of_15_years is just equivolent to line (i.e. for line in file)
            if pickles_of_15_years.split("\t")[0].startswith("ha"): #if we have an ha
                orfx_ha = "HA: " #start things off nicely
                for pickle in pickles_of_15_years.split("\t"): #now add every number option there was in the file
                    orfx_ha += pickle.lstrip("ha")+", " #i.e. we would have ha: 17, 33, ...
            elif pickles_of_15_years.split("\t")[0].startswith("orf"):
                orfx_ha = "ORF: " #start things off nicely
                for pickle in pickles_of_15_years.split("\t"): #now add every number option there was in the file
                    orfx_ha += pickle.lstrip("orf-").upper()+", " #we want ot add in capital X1, X2 ...
            else:
                orfx_ha = "None" #playing it safe
            orfx_ha = orfx_ha.rstrip(", ") #remove that last pesky comma   
        t.orfx_ha = orfx_ha #set up and add our changes to the db
        session.add(t)
        session.commit()
        orfx_ha_file.close()
        #now we need to remove our temp orfx_ha_files so that we don't have any conflicts of interest later down the line
        os.remove(to_remove)
    
    g = session.query(Genome).filter_by(id=g_id).first()
    g.is_analyzed = False #tell the db that if you update the metadat table, then our new genome here needs an update
    session.add(g)
    session.commit()
    
    print colours.cyan + "ORFX/HA Computations Finished" +colours.normal
    
    #need to update the Genome table:
    update_table = 'python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py' #run the genome table update program
    process = subprocess.Popen(update_table, shell=True)
    process.wait()
    print colours.cyan + "Metadata Table Updated" +colours.normal
    