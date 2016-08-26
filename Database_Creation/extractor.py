# -*- coding: utf-8 -*-
"""
Created on Thu May 26 12:46:05 2016

@author: Owen Neuber

Script orignially for extracting information from the top of a fasta file and between each contig.
It has since been expanded to extract information from blast, 16S blast, prokka, and quast output 
files. These files are from the respective directories: 'PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended',
'PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out', 'PATH/TO/ROOT/fasta_files/PROKKA/fasta' and
'PATH/TO/ROOT/fasta_files/PROKKA/tox', and 'PATH/TO/ROOT/fasta_files/QUAST_reports'.
After extraction the information will be loaded into the database BLISTR.db.
and then the files will be closed. This will repeate for all fasta files in the directory 'PATH/TO/ROOT/fasta_files'.
If a genome with the same name as a file being uploaded is already in the database,
that uploading of that file will be skipped in order to aviod duplicate entries.

For the processing of fasta files, it is imperative that the file baseneame and
the genome name given to the fasta file in the header be equivolent. To help with
identifying renagades, I created the program PATH/TO/ROOT/BLISTR_support_programs/wrong_name_finder.py
Just run that bad boy and it will find all the problems for you. Even better, 
if you use the flag --autofix, it will fix the problem for you! Easy peasy.
"""


import os
import glob
import subprocess
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Genome, GeographicLocation, Contig, Toxin, FlaA, FlaB, User, S_16, Prokka, PlaceHolderToxins, PlaceHolderSubtypes #the highlighted imports are used, but in secret, shhhhhh
from tqdm import tqdm
from blessings import Terminal
from sqlalchemy.sql.expression import func

colours = Terminal()

def reverse_comp(line):
    """checks if a line needs to have a sequence replaced with its reverse compliment"""
    if line.split("\t")[11] != "minus":
        return line #if it is not minus, it is in no need of reversing
    temp_dir = 'PATH/TO/ROOT/Database_Creation/'
    temp = open(temp_dir+'temp/temp.fasta', 'w')
    temp.write(">This is a formality\n"+line.split("\t")[12]+"\n")
    temp.close()
    revcomp = "PATH/TO/ROOT/BLISTR_support_programs/./revcomp "+temp_dir+"temp/temp.fasta > "+temp_dir+"temp/temp.rev.fasta"
    process = subprocess.Popen(revcomp, shell=True) #creates a temp.rev.fasta file that will hold the reversed sequences
    process.wait()
    temp = open(temp_dir+"temp/temp.rev.fasta", 'r')
    out_line = line.replace(line.split("\t")[12], "") #the original line minus the sequence we are reversing
    for w in temp:
        if w.startswith(">"):
            continue
        out_line = out_line + w.rstrip("\n")
    return out_line #returns the given line but flipped
    
def list_to_list_of_tuples(list1):
    output = []
    hold = ""
    counter = 0
    for item in list1:
        if (counter % 2) == 1: #if counter is an odd number
            output.append((hold,item)) #adding in the current 2 line pair to the list as a tuple
        counter += 1
        hold = item
    return output

files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta') #will prodcue a list of all fasta files in the directory
engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
extended_fastas = ['PATH/TO/ROOT/fasta_files/BLAST_outputs/Toxin_out/gene_extended/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaA_out/gene_extended/', 'PATH/TO/ROOT/fasta_files/BLAST_outputs/FlaB_out/gene_extended/']
Toxin_or_Fla = ["Toxin", "FlaA", "FlaB"]
toxin_db = 'PATH/TO/ROOT/fasta_files/databases/Toxin_db/BoNT_sequences.fasta'
subtype_db = 'PATH/TO/ROOT/fasta_files/databases/Subtype_db/BONT_DB.faa'
quast_out_dir = 'PATH/TO/ROOT/fasta_files/QUAST_reports/' #directory where all the QUAST results are stored
path_16S = 'PATH/TO/ROOT/fasta_files/BLAST_outputs/16S_out/'
path_f_prokka = 'PATH/TO/ROOT/fasta_files/PROKKA/fasta/'
path_t_prokka = 'PATH/TO/ROOT/fasta_files/PROKKA/tox/'
orfx_ha_file_path = "PATH/TO/ROOT/fasta_files/BLAST_outputs/orfX_HA_out/data/"
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session/allow session.add()
session = Session()

file_num =0
num_of_files = len(files)

list_of_database_data = [(toxin_db, 'Placeholder Toxins'), (subtype_db, 'Placeholder Subtypes')]
for toxin_db, error_position in list_of_database_data: #since we are doing the exact same thing twice, it just makes sense to loop it
    try:
        already_there = False
        t_db = open(toxin_db, 'r')
        counter19 = 0 #ridiculous counter number which has no chance of being used elsewhere
        for prakhar in t_db:
            if prakhar.startswith(">"): #count how many toxins we have in the toxin db (to be comaped with how many place holders we have loaded in the BLISTR.db)
                counter19 += 1
        t_db.close()
        if error_position == 'Placeholder Toxins':
            if counter19 <= int(session.query(PlaceHolderToxins).count()): #little check to see if we have already uploaded our placeholder toxins
                already_there = True
        else:
            if counter19 <= int(session.query(PlaceHolderSubtypes).count()): #little check to see if we have already uploaded our placeholder toxins
                already_there = True
        data = [] #empty list which we will store variables in
        BoNT = []
        sequence = []
        seq = ""
        counter7 = 0
        t_db = open(toxin_db, 'r')
        for line in t_db:
            if already_there: #if our place holder toxins have already been uploaded, skip this step
                break
            if not line.startswith(">"): #we don't caare about any lines that are not headers
                seq = seq + line.rstrip("\n") #compile a big sequence for each contig in the file
                continue
            if counter7 != 0: #skip the first run through
                sequence.append(seq)
                seq = ""
            if error_position == 'Placeholder Toxins':
                line = line.lstrip(">").replace("Cphage", "Cbot").split("Cbot") #make the line into a list of useful components
                data.append(line[0])
                BoNT.append(line[1].split("str.")[0]) #extracts just the BoNT information from the secon half
            else:
                line = line.lstrip(">").replace("|","~",1).split("~") #make the line into a list of useful components
                data.append(line[1].rstrip("\n"))
                BoNT.append(line[0])
            counter7+= 1
        sequence.append(seq) #can't forget that last sequence
        t_db.close()
        counter8 = 0
        for tox in BoNT:
            if error_position == 'Placeholder Toxins':
                name = tox.lstrip(" BoNT").lstrip(":").rstrip("\n").rstrip(" ") #extracts the name (like A1 or C/D)
                to_add = PlaceHolderToxins(name=name, data=data[counter8], seq=sequence[counter8]) #add in the placeholder toxin data
            else:
                name = tox.lstrip("BoNT").lstrip("/").rstrip("\n").rstrip(" ") #extracts the name (like A1 or C/D)
                to_add = PlaceHolderSubtypes(name=name, data=data[counter8], seq=sequence[counter8]) #add in the placeholder subtype data
            counter8 += 1
            session.add(to_add)
            session.commit()
    
    except:
        print colours.red + "error at "+error_position + colours.magenta
        session.rollback()
    
try:
    error_position = "UserName" #this is at the front of this program as EVERYTHING is hooked up to the same user, 'sistr'
    if session.query(User).filter_by(name = 'sistr').count() < 1: #only add 'sister' if there is no user, 'sistr', in the database
        user = User(name='sistr', password_hash="Halflife3") #, selections=header[0]
        session.add(user)
        session.commit() #simply assigning all entries the user name 'sistr'
except:
    print colours.red + "error at the UserName bit. That is quite depressing" + colours.magenta
    session.rollback()

print colours.cyan + "Loading files into the database: " + colours.magenta
with tqdm(total=num_of_files) as pbar:
    for i in files:
        
        file_num += 1 #also convienetly our genome_id !!!
        
        file_name = os.path.basename(i)[:-6] #file base name, minus the ".fasta"
        repeat = session.query(Genome).filter_by(name=file_name).count() #counts the number of genome.name entries with the same name as the file being put in
        if repeat >= 1: #if the file is already in the database, skip it
            #print("Genome " + file_name + " already processed")
            pbar.update(1)
            continue
            
            #NOTE: In order for this to work, the file was 43243.Group3.2009.fasta renammed to 43243.Group3.D_C.fasta
        
        extract = open(i) #will open all the files individually
        """
        Need to do all of the legwork of putting the desired file information 
        to the database here. Then and the end of the loop instance you need
        to close the file so things don't get overloaded
        """
        contig = "" #all these variables are reset when we enter a new file
        contigs = []
        counter = 0
        counter2 = 0
        counter3 = 0
        breaker = 0
        temp = "" #initializing temp variable
        out = "["
        
        
        for line in extract:
            #buff.append(line)        
            counter += 1
            if counter == 1: #only extract the jucy headder information for the first line of the file
                #header stores all the information which goes into the columns, with the exception of the contigs
                
                header = line.split(",") #makes a list of elements where the elements initally had commas between them 
                #store all this information until the contig has been fully extracted
                header = header[1:] #skips the first entry in the contig header (which is the contig number)
                #header[0] = header[0][1:] #removes the first ">" from the headline
    
            elif line.startswith(">") and counter != 1: #this means we finished coppying a contig and it's time to lock it in
                contigs.append(contig)
                contig = "" #now we need to reset contig for the next contig to be processed
                
            else: #if the line does not start with a ">" it must therefore be part of a conteg!
                #run this until the entire contig has been processed
                contig += line[:-1] #+ "\n" #adds all the contig lines together separated by lines
            
        contigs.append(contig) #need to add that final contig to contigs!
    
        #up to here works as desired
        
        #We now have all the information we need to add this genome and its metadata to the database
        error_position = ""
        #if True: #staement to allow testing without try an except
        #Uncomment this IF to get the actual compiler error
        try:            
            error_position = "Genome"
            quast = open(quast_out_dir + file_name + ".QUAST.tsv", "r") #path to the freshly processed quast reports
            quast_data = {} #initializing quast dictionary
            for l in quast: #run for every line in the QUAST.tsv file
                l = l.split("\t")
                dic = {l[0] : l[1]} #settiing a dictionary up to be added to our quast dictionary
                quast_data.update(dic) #update is like append for lists, but with dictionaries! Pretty cool eh?
            quast.close()
                       
            temp = Genome(name=header[0], author=header[1], collection_date=header[2], clinical_or_environmental=header[3], source_info=header[4], institution=header[5], is_analyzed=True, quality_stats=quast_data, user_id=1, sub_type=None) #the user_id is 1 as sistr is user #1 and we only care about sistr here
            session.add(temp)
            session.commit() #adding the genomic metadata to the database
                    
            error_position = "Contig"
            for j in contigs:
                counter2 += 1
                #the following will add all the contig information into one huge line of code to be put into the database in a single run!
                out = out + "Contig(contig_number="+str(counter2)+", seq='"+j+"'), "
                
            out = out[:-2] + "]" #need that filnal close brace at the end #the [:-2] removes the last 2 character (", ") from the end, which must be removed
            temp.contigs = eval(out) #will then evaluate the string's code
            session.add(temp)
            session.commit() #adding all the contig information
            
            """ A quick note: using the above eval statement for a missive one liner may seem idiotic and pointlessly time consuming, but
            it should be noted that the proper way of adding the genomic data to the database, which is having
                c = Contig(contig_number=counter2, seq=j, genome_id=g_id)
                session.add(c)
                session.commit()
            inside the above for loop takes around 0.9 to 1 seconds to fully add in the contig, whereas using the eval statement takes
            around 0.6-0.65 seconds, which is significantly faster.
            """
            
            error_position = "GeographicLocation"
            temp.geolo = [GeographicLocation(lat=header[6], lng=header[7], country=header[8], region=header[9])] #notice how things are in square brackets??? Very important!!! unless it is the primary table (the one the foreign keys hook up to), you need the square brackets
            session.add(temp)
            session.commit() #adding the geographic location data to the database
                       
            extract.close()           
            
            #The following bit is to add 16S data into the database            
            error_position = "16S"
            try:
                s16 = open(path_16S + file_name + ".blast.tsv") #will fail to open if the file is a .no_hits
                c = 0
                error = None #setting a defualt for error
                for m in s16:
                    if c == 0:
                        best_hit = m.split("\t")[1] #the best hit data is always in the first line
                        seq = reverse_comp(m).split("\t")[12]
                    c += 1
                    if not "cbot" in m.split("\t")[1]:
                        error = m.split("\t")[1] #We don't care about multiple errors. If we get one in the top 5, we will put any of them here
                        break
                
                temp.s_16 = [S_16(best_hit=best_hit, error=error, seq=seq)]
                s16.close()
            except:
                temp.s_16 = [S_16(best_hit=None, error="16S Not found", seq=None)]               
            
            session.add(temp)
            session.commit()
            
            error_position = "PROKKA" #adding PROKKA infrormation into the database
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
            base = 'Prokka(fasta_faa="""'+out_f_faa+'""", fasta_coding_genes='+str(str(out_f_faa).count(">"))+', fasta_ffn="""'+out_f_ffn+'""", fasta_ORFs='+str(str(out_f_ffn).count(">"))+',' #I am stringing the objects being counted to avoid NoneType errors. The second layer of str() is to allow concatnation of strings and ints
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
                out = base+'tox_exists='+str(tox_exists)+', tox_faa="""'+out_t_faa+'""", tox_coding_genes='+str(str(out_t_faa).count(">"))+', tox_ffn="""'+out_t_ffn+'""", tox_ORFs='+str(str(out_t_ffn).count(">"))+')]' #the tripple quotes are to allow newlines to be in th3e original string
                
            elif os.path.isdir(path_t_prokka+file_name+".1"): #checking if we have a fabled multi fata result
                tox_exists = True
                out = ""
                toxins_prokka_path = glob.glob(path_t_prokka+file_name+".[0-9]*") #this will be a list off all the files with the desired name.number
                toxins_prokka_path.sort()
                for tox_path in toxins_prokka_path: 
                    num = os.path.basename(tox_path).split(".")[-1] #extracts the number our current iteration is on
                    t_faa = open(tox_path+"/"+file_name+"."+num+".toxin.faa")
                    out_t_faa = ""
                    for p in t_faa:
                        out_t_faa = out_t_faa + p
                    t_faa.close()
                    t_ffn = open(tox_path+"/"+file_name+"."+num+".toxin.ffn")
                    out_t_ffn = ""
                    for a in t_ffn:
                        out_t_ffn = out_t_ffn + a
                    t_ffn.close()
                    out = out+base+'tox_exists='+str(tox_exists)+', tox_faa="""'+out_t_faa+'""", tox_coding_genes='+str(str(out_t_faa).count(">"))+', tox_ffn="""'+out_t_ffn+'""", tox_ORFs='+str(str(out_t_ffn).count(">"))+'), '
                out = out.rstrip(", ") + "]" #formatting our output once we have finished running through all the toxin files
            else:
                tox_exists = False
                out_t_faa = "None"
                out_t_ffn = "None"
                out = base+'tox_exists='+str(tox_exists)+', tox_faa="""'+out_t_faa+'""", tox_coding_genes='+str(str(out_t_faa).count(">"))+', tox_ffn="""'+out_t_ffn+'""", tox_ORFs='+str(str(out_t_ffn).count(">"))+')]'

            out = "["+out
            temp.prokka = eval(out) 
            session.add(temp)
            session.commit()
            check_it = out
            
            
            #the following bit is to send the toxin and FlaA&B data into the database (other than the name of the above closed file, this is independedt of that file)
            for path in extended_fastas:
                error_position = Toxin_or_Fla[counter3]
                fail = False
                try: #try to open the designated file. If error, then it must have been a .no_hits file
                    fasta = open(path + file_name + ".blast.fasta") #opens the blasted equivolents to the original file
                except:
                    fail = True
                    out = "["+Toxin_or_Fla[counter3] + "(best_hit="+"None)]" #The funny thing about my setup here is that, due to the following break, this will never be added to the session. But since the result is None, no one cares
                    #print("file failed to open")
                    #TODO replace this break with a continue once the other databases have been added
                    break #just skip this input this time and add nothing to the database. It is easier this way
                if not fail:
                    l = [] #initialize a list that will grow one size for every line in a fasta file
                    for k in fasta: #extracting all the information from our toxin fasta files and storing them in a list
                        l.append(k) #adding to our mighty list
                    fasta.close() #everyting has been saved locally, we can now close it
                    
                    out = "[" #starting the output sequence
                    counter789 = 0 #counter to keep track of which toxin we are processing (if there is more than one toxin)
                    for metadata, seq in list_to_list_of_tuples(l):
                        counter789 += 1
                        best_hit = metadata.split("\t")[1] #extracts the best hit information from the list
                        bp_before = metadata.split("\t")[2]
                        bp_after = metadata.split("\t")[3]
                        contig_num = metadata.split(",")[0].lstrip(">") #gets the contig number from the fasta first line
                        #conting_num is hooked up via forign key to a contig id (not the number in the fasta file, like this number could be 2087, representing the 2087th uniquely entered contig, independent of genome name)
                        #Since this entry has to be the newest entry to the db, I can simply count how many contigs there are in the db
                        #and then add contig_number to that to generate the appropriate contig id number.
                        #sudden change of plans, I am going to hook up another variable, contig_id for forign key purposes, and keep contig_num where it lies
                        contig_id = int(contig_num)  + int(session.query(func.max(Contig.id)).scalar()) - int(session.query(Contig).filter_by(genome_id=session.query(func.max(Genome.id)).scalar()).count()) #need to subtract our current fasta's contig number from the count too            
                        
                        #The following bit is orfx_ha manipulation stuff
                        if len(list_to_list_of_tuples(l)) > 1: #if there are more than one toxin, we will have to react differently
                            try:
                                orfx_ha_file = open(orfx_ha_file_path+file_name+"."+str(counter789)+".no_hits", 'r') #try to use the no hits and if not, we will use the proper one
                                out = out+Toxin_or_Fla[counter3] + "(best_hit=\'"+str(best_hit.lstrip(">").replace("Cphage", "Cbot").split("Cbot")[1].split("str.")[0].split("sub:")[0].lstrip(" BoNT").rstrip(" ").lstrip(":"))+"\', contig_num="+str(contig_num)+", contig_id="+str(contig_id)+", bp_before="+str(bp_before)+", bp_after="+str(bp_after)+", orfx_ha='None', seq=\'"+str(seq).rstrip("\n")+"\'), " #the rstrip is likely not needed, but just making sure. As of a recent update to the toxin files, the rstrip is now very needed
                                orfx_ha_file.close()
                                continue #we do not want to do any orfx_ha manipulations on a .no_hit file
                            except:
                                orfx_ha_file = open(orfx_ha_file_path+file_name+"."+str(counter789)+".orfX_HA.tsv", 'r') #open up our orfx_ha files
                        else:
                            try: #hope to fail on this one so that we use the proper toxin file, otherwise oh well, to the next iteration
                                orfx_ha_file = open(orfx_ha_file_path+file_name+".no_hits", 'r')
                                out = out+Toxin_or_Fla[counter3] + "(best_hit=\'"+str(best_hit.lstrip(">").replace("Cphage", "Cbot").split("Cbot")[1].split("str.")[0].split("sub:")[0].lstrip(" BoNT").rstrip(" ").lstrip(":"))+"\', contig_num="+str(contig_num)+", contig_id="+str(contig_id)+", bp_before="+str(bp_before)+", bp_after="+str(bp_after)+", orfx_ha='None', seq=\'"+str(seq).rstrip("\n")+"\'), " #the rstrip is likely not needed, but just making sure. As of a recent update to the toxin files, the rstrip is now very needed
                                orfx_ha_file.close()
                                continue #we do not want to do any orfx_ha manipulations on a .no_hit file
                            except:                                
                                orfx_ha_file = open(orfx_ha_file_path+file_name+".orfX_HA.tsv", 'r') #the proper toxin file
                        for pickles_of_15_years in orfx_ha_file:
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
                        orfx_ha_file.close()
                        #now the bit where we set the toxin up to be added to the db
                        out = out+Toxin_or_Fla[counter3] + "(best_hit=\'"+str(best_hit.lstrip(">").replace("Cphage", "Cbot").split("Cbot")[1].split("str.")[0].split("sub:")[0].lstrip(" BoNT").rstrip(" ").lstrip(":"))+"\', contig_num="+str(contig_num)+", contig_id="+str(contig_id)+", bp_before="+str(bp_before)+", bp_after="+str(bp_after)+", orfx_ha='"+orfx_ha+"', seq=\'"+str(seq).rstrip("\n")+"\'), " #the rstrip is likely not needed, but just making sure. As of a recent update to the toxin files, the rstrip is now very needed
                    out = out.rstrip(", ") + "]" #The above ridculousness with best_hit is just to ensure that the metadata originally put in with it is replaced with a clean letter type (like A1)
                    
                #we need to determine which table we are going into
                if counter3 == 0:                
                    temp.toxin = eval(out) #the eval Will properly execute the string code as if I had typed it myself
                elif counter3 == 1:                
                    temp.flaa = eval(out)
                elif counter3== 2:                
                    temp.flab = eval(out)
                    
                session.add(temp)
                session.commit()
                counter3 += 1     
                #TODO: remove this break once the other databases have been added                      
                break #this break is here until we add in the flaA&B databases
        
        except:
            session.rollback() #if we have a proble, 'cause reasons, this should undo all the broken stuff we did
            print colours.red + "ERROR. The session has been rolled back."
            print colours.red + "Skipped genome: " + file_name + " at: " + error_position + colours.magenta
            if error_position == Toxin_or_Fla[counter3]:
                fasta.close() #to ensure we don't have any memory leaks
            if breaker > 5:
                break #if there are 5 errors when running this code, something must be up! Stop this nonsense at once!
            breaker +=1 #keep count of how many errors occured this run
        
        pbar.update(1)
        #break #this break is just for testing a singular genome
    