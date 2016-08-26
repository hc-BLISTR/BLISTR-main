# -*- coding: utf-8 -*-
"""
Created on Mon May 30 13:02:49 2016

@author: Owen Neuebr

This file is the heart of the BLISTR. All communications between front and backened
goes through here. There format of this communication is as follows:

@BLISTR.route('/home', methods=['GET', 'POST'])
@BLISTR.route('/upload', methods=['GET', 'POST']) #this forms a link for the function home to the url: localhost:5000/upload
def home(): #this is defining the home function which will communicate with home.html and also the /home url
    ...
    return render_template('home.html', title='Home', form=form, variable_to_pass_to_html=variable)  #this tells the html to render the 
    #html page 'home.html', and to pass it the variables title, form, and variable_to_pass_to_html
    
at the bottom of this document is:
BLISTR.run(debug=False) 
This tells BLISTR to run and since debug=True, you will get browser error messages when they come up (setting it to false will give you that 404 error page)
If you set BLISTR.run(port=4269, debug=False), this would have the app run on localhost:4269 (instead of the default 5000) and error message would not appear
"""

import os
import subprocess
import glob
import time
import pandas as pd
import requests
from functools import partial #these two imports are for list editing
from operator import ne
from flask import Flask, render_template, flash, url_for, redirect, request, send_from_directory, jsonify, send_file#, session
from __init__ import *
from html_tables import html_table, HTML_format, html_place_holders_table, HTML_format_toxin_tree, html_place_holders_table_for_subtypes, HTML_format_subtype_tree
from forms import QueryForm, TableForm, EditForm, MapForm
from sqlalchemy.orm import sessionmaker
from shutil import copyfile
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func
from models import Genome, GeographicLocation, Contig, Toxin, User, Searches, S_16, Prokka, PlaceHolderToxins, PlaceHolderSubtypes#, FlaA, FlaB
from blessings import Terminal

colours = Terminal()

engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
session = Session()

CURRENT_XLSX = "PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx"
CURRENT_16S_XLSX = "PATH/TO/ROOT/Database_Inputs/16S_issues.xlsx"
PROKKA_PROCESS = "" #setting up a global variables
def Prokka_Check():
    """
    Function to determine wheather PROKKA has finished or not. Will flash to
    the user if it is or not. If it has finished, it will have the metadata
    table updated to account for the changes.
    """
    global PROKKA_PROCESS
    if session.query(Genome).filter_by(name=PROKKA_PROCESS).first(): #check if it exists
        g_id = session.query(Genome).filter_by(name=PROKKA_PROCESS).order_by(Genome.id.desc()).first().id #most recent genome of that name entered
        if session.query(Prokka).filter_by(genome_id=g_id).count() > 0:    
            form = TableForm()
            PROKKA_PROCESS = "" #if the prokka name has been added to the database, make this global vaiable empty so it will alert nothing
            
            data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx')
            data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
            data.index.name=None
            pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
            #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
            out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">").replace("{","{").replace("}","}")
            HTML_format(out)
            flash('Finished processing '+PROKKA_PROCESS+'\'s PROKKA information.') 
            return render_template('genome_table.html', form=form, title="Genome Table") #create a new table and refresh the page
        else:
            flash('Currently processing '+PROKKA_PROCESS+'\'s PROKKA information. Do NOT upload any additional genomes until this is done. Please check again later') 


def unicode_list_to_str(u_code_list): #This is just a function for me. Has nothing to do with flask or anything, okay?
    """
    function to convert a list of unicode (string type) numbers to a single string
    which will output the numbers in the form: 2-3-4-1 (dashes between numbers)
    """
    out_list = ""
    for item in u_code_list:
        out_list = out_list + str(item) + "-"
    return out_list.rstrip("-") #removes the extra '-' (i.e 2-3-4-1-)
    

def remove_database_entries(genome_ids):
    """
    Takes in a LIST of genome ids that you wish to remove from our glorious database.
    If you want to remove only one entry, enter it like so: remove_database_entries([genome_id])
    which will simulate the list for the single entry.
    The function will return None.
    """
    
    for genome_id in genome_ids:
        genome_name = str(session.query(Genome).filter_by(id=genome_id).first().name) #need to set the genome's name before removing things so that we may use it later
        genome_id = int(genome_id) #ensuring no unicode buffer errors
        try:
            session.query(GeographicLocation).filter_by(genome_id=genome_id).delete()
            session.query(S_16).filter_by(genome_id=genome_id).delete()
            session.query(Prokka).filter_by(genome_id=genome_id).delete()
            session.query(Toxin).filter_by(genome_id=genome_id).delete()
            session.query(Contig).filter_by(genome_id=genome_id).delete()
            session.query(Genome).filter_by(id=genome_id).delete()
            flash("Genome '"+genome_name+"' removed from the database")
        except:
            session.rollback()
            flash("Failed to remove genome '"+genome_name+"' from the database")
    try:
        session.commit()
    except:
        session.rollback()
        flash("Error removing genomes")
    return None
    

def transeq(seq):
    """
    Takes in a toxin sequence and then returns that sequence in faa format.
    Does this by creating the file 'temp.fasta' which will hold the toxin
    sequence. The program transeq will then be run which will produce the
    file 'temp.faa', from which our new sequence will be extracted.
    """
    
    temp_file = 'PATH/TO/ROOT/Database_Outputs/temp.fasta'
    temp = open(temp_file, 'w')
    temp.write(">Just a formality \n"+seq)
    temp.close()
    
    trans = "PATH/TO/ROOT/BLISTR_support_programs/./transeq -sequence "+temp_file+" -outseq "+temp_file[:-6]+".faa"
    proc = subprocess.Popen(trans, shell=True)
    proc.wait()
    
    temp = open(temp_file[:-6]+".faa", 'r')
    new_seq = ""
    for line in temp:
        if line.startswith(">"):
            continue
        new_seq += line
    
    os.remove(temp_file)
    os.remove(temp_file[:-6]+".faa")
    
    return new_seq


@BLISTR.route('/', methods=['GET', 'POST'])
@BLISTR.route('/home', methods=['GET', 'POST'])
@BLISTR.route('/upload', methods=['GET', 'POST'])
def home():
    #Main page function
    Prokka_Check() #quick check
    form = QueryForm() #This makes the connection to the forms.py form class QueryForm
    if form.validate_on_submit(): #only true if someone hits the 'submit' button
        
        if form.search.data and form.query.data: #checking for multiple field entries
            flash("Only one at a time please!")
            return redirect(url_for('home'))         
            
        if form.prokka_skip.data and form.prokka_wait.data: #checking for multiple field entries
            flash("You cannot both wait for PROKKA and skip it")
            return redirect(url_for('home'))    
        
        if not form.search.data and not form.query.data: #If they just hit submit without putting anything first, just refresh the page
            return redirect(url_for('home'))
            
        #######################################################################
            #Search Function
        if form.search.data: #if they used the search form, use the following to return the results from the database
            genomes = session.query(Genome).order_by(Genome.id.asc()).all()
            g_ids = ""
            counter = 0
            for g in genomes:
                if form.search.data.upper() in str(g.name).upper(): #if what we are looking for is anywhere to be found in the genome name, add its id to the search result. Also, the .upper() is to remove case sensitivity
                    g_ids = g_ids + "-" + str(g.id)
                    counter += 1
            if not g_ids: #if there was no positive result, refresh the page
                flash("No genome with the name "+ form.search.data + " was found")
                return redirect(url_for('home'))
            g_ids = g_ids.lstrip("-") #need to remove a leading dash for formatting reasons
            add = Searches(g_ids=g_ids)
            session.add(add) #add the dash separated list to the database for use with Tables
            session.commit()
            if counter == 1:
                flash("One match found")
            else:
                flash(str(counter) + " matches found")
            
            if form.export_TSV.data: #True is the check box is checked
                try:
                    tsv_exporter = 'python PATH/TO/ROOT/Database_Outputs/TSV_exporter.py'
                    process = subprocess.Popen(tsv_exporter, shell=True) #run the TSV exporter which will create the desired tsv file. Giving the argument of the genome id we want to have exported
                    process.wait()                
                    flash("Exported to TSV")
                except:
                    flash("Error exporting to TSV") #just incase something goes wrong, we will spit this error
                
            return redirect(url_for('tables'))
            
        #######################################################################
            #Upload Function
        #TODO: add/remove this functionallity as needed (to allow multiple entries of the same name, or not)
        if session.query(Genome).filter_by(name=str(form.query.data)[:-6]).first(): #This will be NoneType if the named genome is not in the database
            flash("A genome with that name already exists in the database. Change your filename or use the search function to find your genome")
            return redirect(url_for('home'))            
            
        if (not ".fasta" in form.query.data) or (".fasta" in form.query.data.rstrip(".fasta")): #If a path without ".fasta" at the end of the path (in the middle does not count!) will trigger this and the user gets an error
            flash("Invalid file selection. Make sure the file is a '.fasta'!")
            return redirect(url_for('home')) #redirects to BLISTR homepage
        """
        How im going to add the fata file pointed to via the submitted path (URL):
        1. use proc to send me to another file which will run blast and such.
        2. send that file the URL information (I will likely have to do so with flags and argparser)
        3. send a dash separated list to represent the information in the contig header via a flag.
        4. have all that information stored to the database.
        5. then return here and instead of returning the result of the search, we will spit
           out all the relovant information about the genome!       
        """
        last_search = session.query(func.max(Searches.id)).scalar() #largest search id number
        last = session.query(Searches).filter_by(id=last_search).first() #This is here so that when a user uploads a genome, the last searched for item will no longer be the defualt        
        if last: #as long as there has been a prior search
            last.searched_for = True
            session.add(last)
            session.commit() #updating the search database to tell it that the searched for item has indeed been searched for 
            
        #Genome_name,Author,Collection_date,Clinical_or_Environmental,Source_info,Institution,Lat,Long,Country,Region
        headers = ['None']*10 #initializing header variables
        headers_data = [str(form.query.data)[:-6], form.author.data, form.collection_date.data, form.clinical_or_environmental.data, form.source_info.data, form.institution.data, form.lat.data, form.lng.data, form.country.data, form.region.data]
        tracker = 0
        #the following bit will take the region and country data entered (only if not lat and lng was also entered) and then determine the lat and lng based off the given locations
        if (not form.lat.data and not form.lng.data) and (form.country.data or form.region.data):
            if str(form.country.data).capitalize() != "None":
                country = str(form.country.data).replace(" ", "") 
            if str(form.region.data).capitalize() != "None":
                region = str(form.region.data).replace("- ",",+").replace(" ","").rstrip("\n") #taking the region portion and formatting it as needed
            try:
                if country and region: #how to format it if we have both country and region
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+region+",+"+country)
                elif country: #how to format it if we only have country
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+country)
                else: #how to format it if we only have region
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address='+region)
                
                resp_json_payload = response.json() #fancy stuff that will extract our lat & lng from google
                lat_lng_dict = resp_json_payload['results'][0]['geometry']['location']
                lat = str(lat_lng_dict.get('lat'))[:12] #we only want these to have 12 characters or less
                lng = str(lat_lng_dict.get('lng'))[:12]
                headers_data[6] = lat
                headers_data[7] = lng
            except:
                pass #if it din't work, oh well
        
        for data in headers_data:
            if data: #if not None
                headers[tracker] = data.replace(",","shiaLabeoufAtTheRioOlympics2016ForGolf") #we later do a plit on this data. So if the information they put in had a comma, this will address the issue (assuming that they won't uses "shiaLabeoufAtTheRioOlympics2016ForGolf"'s in any metadata (but who would ever do that?))
                if "'" in headers[tracker] or '"' in headers[tracker]:
                    flash("Don't use quotes in your metadata") #If you ever have problems with people entering special characters that break
                    return redirect(url_for('home')) #the code, then add in exceptions here to address them (just as I have for quotes)
            else:
                headers[tracker] = 'None'
            tracker += 1
        one_string = ""
        for header in headers: #make the entire list of data into ons string separated by '-'s
            one_string = one_string + str(header).replace("-", "????") + "-"
        one_string = one_string.rstrip("-").replace(" ", "~") #remove nasty spaces and the trailing '-'
        sub = ""
        if form.sub_type.data: #if they enter the sub type...
            sub = '-s '+str(form.sub_type.data).replace("(","666").replace(")", "999").replace(" ","space").replace(",","~")+' ' #formating to allow brackets and spaces
            
        pident_len_slen = '-d '+str(form.pident.data)+"~"+str(form.len_slen.data)+' '
        
        processor = 'python PATH/TO/ROOT/Database_Inputs/processor.py -i '+one_string+' '+sub+pident_len_slen
        wait_processor = 'python PATH/TO/ROOT/Database_Inputs/processor.py -p -i '+one_string+' '+sub+pident_len_slen
        current = ""
        for path in BLISTR.config['UPLOAD_PATHS']:
            is_there = glob.glob(path+form.query.data) #searches all the allowed directories for the fasta file. If none of them have it, give a problem. Just an annoying little fix to the checkbox basename problem
            if is_there:
                path = path
                break
            current = current + path + " "
        if not is_there: #If none of the paths hold the file, this is where we will reveal it
            flash('Invalid upload path. Add your upload path to config.py to solve this issue. Currently allowed upload paths are: ' + current)
            return redirect(url_for('home'))
        flash('Processing genome data...')
        if form.prokka_wait.data:
            process = subprocess.Popen(wait_processor + path + form.query.data, shell=True) #tells the processor to wiat on the prokka data
            process.wait()
            flash('PROKKA run finished')
        else: #Otherwise the prokka stuff will be run after the processor has finished running all the other important things
            process = subprocess.Popen(processor + path + form.query.data, shell=True) #tells processor.py to run with the URL given from the form (in the webpage)
            process.wait()
            solo_prokka = 'python PATH/TO/ROOT/Database_Inputs/PROKKA.py -s -g ' + str(form.query.data)[:-6] +' ' #remove the ".fasta"
            if not form.prokka_skip.data:
                proc = subprocess.Popen(solo_prokka + ' PATH/TO/ROOT/Database_Inputs/temp.fasta', shell=True, stdin=None, stdout=None, stderr=None) #tells prokka.py to run on its own without messing up everything else (i.e. run in the background)
                flash('PROKKA will be run in the background. Check the genome page for details')
                global PROKKA_PROCESS
                PROKKA_PROCESS = str(form.query.data)[:-6] #storing a global variable of what file prokka is currently processing (you cannot use .rstrip('.fasta')!!! it will mess up with certain names. i.e. 'dwight' becomes 'dwigh' using rstrip)
                
        if form.export_TSV.data: #True is the check box is checked
            try:
                tsv_exporter = 'python PATH/TO/ROOT/Database_Outputs/TSV_exporter.py'
                process = subprocess.Popen(tsv_exporter, shell=True) #run the TSV exporter which will create the desired tsv file!
                process.wait()                
                flash("Exported to TSV")
            except:
                flash("Error exporting to TSV") #just incase something goes wrong, we will spit this error
        id_just_entered = session.query(func.max(Genome.id)).scalar()
        num_of_toxins = session.query(Toxin).filter_by(genome_id=id_just_entered).count() #counting how many toxins the newly entered genome has
        if num_of_toxins > 1: #if the genome has more than one toxin, alert the user to this
            flash("Note: the genome you just entered has " + str(num_of_toxins) + " toxins in it")
        return redirect(url_for('tables')) #sends us to which ever function's name is 'tables'
        
    
    return render_template('home.html', title='Home', form=form)
    
    
@BLISTR.route('/tables')
def tables():
    form = EditForm()
    
    dict_list = []
    last_search = session.query(func.max(Searches.id)).scalar() #largest search id number
    
        
    ###########################################################################
        #Search Result
    if last_search and not session.query(Searches).filter_by(id=last_search).first().searched_for: #if there is a search recorded in the database and the last search has searched_for set to False
        search_for = session.query(Searches).filter_by(id=last_search).first().g_ids.split("-") #a list of string type numbers that we want to search for
        for g_id in search_for:
            g = session.query(Genome).filter_by(id=int(g_id)).first()
            g_name = g.name
            sub_type=g.sub_type
            geo = session.query(GeographicLocation).filter_by(genome_id=g.id).first() #our basic geographic location query form
            tox = session.query(Toxin).filter_by(genome_id=g.id).first()
            if tox == None:
               t_meta, bp_before, bp_after = [None]*3 #If there was not toxin input, give these values None
            else:
               t_meta=tox.best_hit #If there was a toxin input, give the outputs their proper values
               bp_before=tox.bp_before
               bp_after=tox.bp_after
            
            genome_name = g_name.split(".")[0] #can't forget to assign that genome name too!
            
            #Set up to extract allthe QUAST data from its dictionary format
            data = g.quality_stats.values() #dictionary of the QUAST values
            quast_data = []#initializing an empty list for metadata to be added to
            for dirt in data: #the reason I'm doing this is to remove a newline which is at the end of each data entry
                quast_data.append(dirt.rstrip("\n"))
            l_contig, n_contigs, n_contigs1000, tl0, GC, N100, tl1000, tl, contigs0 = quast_data #giving each list item its own variable. n represents 'number', l represents 'length', tl represents 'total length'
            
            lat_lng = geo.lat+":"+geo.lng
            
            multi_tox = session.query(Toxin).filter_by(genome_id=g.id).all()
            counter92 = 0
            sub_tox = ""
            if len(multi_tox) < 2:
                sub_tox = None
            else:
                for t in multi_tox:
                    if counter92 == 0:
                        counter92+= 1
                        continue
                    sub_tox += t.best_hit + ", "
                sub_tox = sub_tox.rstrip(", ")
            
            dict_list.append({"Gname":genome_name, "Cdate":g.collection_date, "Stype":g.clinical_or_environmental, "Sinfo":g.source_info, \
            "inst":g.institution, "author":g.author, "l_contig":l_contig, "n_contigs":n_contigs, "n_contigs1000":n_contigs1000, "tl0":tl0, \
            "GC":GC, "N100":N100, 'tl1000':tl1000, 'tl':tl, 'contigs0':contigs0, 'lat_lng':lat_lng, 'country':geo.country, \
            'region':geo.region.rstrip("\n"), 't_meta':t_meta, 'sub_type':sub_type, 'bp_before':bp_before, 'bp_after':bp_after, 'sub_tox':sub_tox})
            
        
    ###########################################################################
        #Uploading
    else: #if there was a search in the search database that has yet to be completed, then that is what Tables will render, otherwise it will show the result of the most recent addition to the genomes database
        last = session.query(func.max(Genome.id)).scalar() #the largest genome id number (i.e. newest genome/entry)
        g = session.query(Genome).filter_by(id=last).first()
        
        #check if 16S gave a problem:
        if session.query(S_16).filter_by(genome_id=g.id).first().error != None:
            flash("16S error identified with upload. Result: " + str(session.query(S_16).filter_by(genome_id=g.id).first().error))
            issue = "python PATH/TO/ROOT/Database_Inputs/16S_issues_table_maker.py" #the 16S table is small so making a fresh one every time there happens to be an error is not too demanding
            process = subprocess.Popen(issue, shell=True) 
            process.wait()            
        
        g_name = g.name
        sub_type=g.sub_type
        geo = session.query(GeographicLocation).filter_by(genome_id=g.id).first() #our basic geographic location query form
        tox = session.query(Toxin).filter_by(genome_id=g.id).first()
        if tox == None:
           t_meta, bp_before, bp_after = [None]*3 #If there was not toxin input, give these values None
        else:
           t_meta=tox.best_hit #If there was a toxin input, give the outputs their proper values
           bp_before=tox.bp_before
           bp_after=tox.bp_after
           
        genome_name = g_name.split(".")[0] #can't forget to assign that genome name too!
        
        #Set up to extract allthe QUAST data from its dictionary format
        data = g.quality_stats.values() #dictionary of the QUAST values
        quast_data = []#initializing an empty list for metadata to be added to
        for dirt in data: #the reason I'm doing this is to remove a newline which is at the end of each data entry
            quast_data.append(dirt.rstrip("\n"))
        l_contig, n_contigs, n_contigs1000, tl0, GC, N100, tl1000, tl, contigs0 = quast_data #giving each list item its own variable. n represents 'number', l represents 'length', tl represents 'total length'
        
        lat_lng = geo.lat+":"+geo.lng
        
        multi_tox = session.query(Toxin).filter_by(genome_id=g.id).all()
        counter92 = 0
        sub_tox = ""
        if len(multi_tox) < 2:
            sub_tox = None
        else:
            for t in multi_tox:
                if counter92 == 0:
                    counter92+= 1
                    continue
                sub_tox += t.best_hit + ", "
            sub_tox = sub_tox.rstrip(", ")
        
        dict_list.append({"Gname":genome_name, "Cdate":g.collection_date, "Stype":g.clinical_or_environmental, "Sinfo":g.source_info, \
            "inst":g.institution, "author":g.author, "l_contig":l_contig, "n_contigs":n_contigs, "n_contigs1000":n_contigs1000, "tl0":tl0, \
            "GC":GC, "N100":N100, 'tl1000':tl1000, 'tl':tl, 'contigs0':contigs0, 'lat_lng':lat_lng, 'country':geo.country, \
            'region':geo.region.rstrip("\n"), 't_meta':t_meta, 'sub_type':sub_type, 'bp_before':bp_before, 'bp_after':bp_after, 'sub_tox':sub_tox})
        
    ###########################################################################
        #The rest
    temp_maker = 'python PATH/TO/ROOT/Database_Outputs/temp_maker.py '
    process = subprocess.Popen(temp_maker, shell=True) #will produce temparary files to make hyperlinks to
    process.wait()    
    
    #TODO: add in the flagellan stuff
    #The following are all the variables to be passed to the table on the tables page
    html_table(dict_list) #this quickly conjures up the tables.html page
    return render_template('tables.html', title='Tables', form=form)
    
    
@BLISTR.route('/echo/', methods=['GET'])
def echo():
    TO_FLASH = []
    #The function that will allow editing of the tables page
    changeable = ["sub_type", "c_date", "s_type", "s_info", "inst", "author", "lat_lng", "country", "region"]
    g_names = []
    counter = 0
    update_16S = False
    while True:
        counter += 1
        try: #keep going at this until we have a problem and then break
            g_names.append(request.args.get("Gname"+str(counter)))
        except:
            break
        if counter > session.query(Genome).count(): #safety net to protect against infinite loops
            break
        if request.args.get("Gname"+str(counter)) == None:
            break

    counter2 = 0
    list_of_changes = [] #a danty nested list that will have one nested list for every row availiable
    while counter2 < counter:
        counter2 +=1
        to_change =[] #need to keep resetting this value
        for change in changeable: #extract all the table information, for every row there is
            if request.args.get(change+str(counter2)) != None: #make sure None entries don't make it
                to_change.append(str(request.args.get(change+str(counter2)))) #need to stringify so that we don't get NoneType errors
        list_of_changes.append(to_change)
    
    g_names = filter(partial(ne, None), g_names) #for some reason, the list has a whole bunch of Nones in it. I have no idea why. This should address it though
    list_of_changes.remove([])
    counter3 = 0
    print list_of_changes
    for g_name in g_names:
        g = session.query(Genome).filter_by(name=g_name).first()
        geo = session.query(GeographicLocation).filter_by(genome_id=g.id).first()
        num_toxins = session.query(Toxin).filter_by(genome_id=g.id).count()
        #The following bit is accounting for changes to geographic location and genome
        #######################################################################
        if num_toxins == 0 and list_of_changes[counter3][0].lower() != "none":
            TO_FLASH.append("SubType: '"+list_of_changes[counter3][1]+"' cannot be used for a genome without any toxins.")
        else:
            g.sub_type = list_of_changes[counter3][0]
        
        if len(list_of_changes[counter3][1]) > 15: #just checks if the user entry is below 15 characters and if it is not, the changes will not be made and the user will be notified
            TO_FLASH.append("Colection date entry: '"+list_of_changes[counter3][1]+"' is too long. Reduce it to 15 characters or less.")
        else:
            g.collection_date = list_of_changes[counter3][1]
            
        if list_of_changes[counter3][2].lower() != "clinical" and list_of_changes[counter3][2].lower() != "Env./Food" and list_of_changes[counter3][2].capitalize() != "None": #making sure the user entered clinical or environmental
            TO_FLASH.append("Source type entry: '"+list_of_changes[counter3][2]+"' is invalid. Only clinical, Env./Food, or None are accepted.")
        else:
            g.clinical_or_environmental = list_of_changes[counter3][2].lower()
            
        if len(list_of_changes[counter3][3]) > 200: 
            TO_FLASH.append("Source information entry: '"+list_of_changes[counter3][200]+"' is too long. Reduce it to 200 characters or less.")
        else:
            g.source_info = list_of_changes[counter3][3]
            
        if len(list_of_changes[counter3][4]) > 7: 
            TO_FLASH.append("Institution entry: '"+list_of_changes[counter3][4]+"' is too long. Reduce it to 7 characters or less.")
        else:
            g.institution = list_of_changes[counter3][4]
            
        if len(list_of_changes[counter3][5]) > 50: 
            TO_FLASH.append("Author entry: '"+list_of_changes[counter3][5]+"' is too long. Reduce it to 50 characters or less.")
        else:
            g.author = list_of_changes[counter3][5]
        
        if list_of_changes[counter3][6].find(":") == -1:
            TO_FLASH.append("Lat/Long entry: '"+list_of_changes[counter3][6]+"' Needs to have a colon seperating lat and lng.")
        elif len(list_of_changes[counter3][6].replace(" ", "").split(":")[0]) > 12 or len(list_of_changes[counter3][6].replace(" ", "").split(":")[1]) > 12: 
            TO_FLASH.append("Lat/Long entry: '"+list_of_changes[counter3][6]+"' is too long. Reduce both lath and long to 12 characters or less.")
        else:
            geo.lat = list_of_changes[counter3][6].replace(" ", "").split(":")[0]
            geo.lng = list_of_changes[counter3][6].replace(" ", "").split(":")[1]
            
        if len(list_of_changes[counter3][7]) > 50: 
            TO_FLASH.append("Country entry: '"+list_of_changes[counter3][7]+"' is too long. Reduce it to 50 characters or less.")
        else:
            geo.country = list_of_changes[counter3][7]
        
        if len(list_of_changes[counter3][8]) > 50: 
            TO_FLASH.append("Region entry: '"+list_of_changes[counter3][8]+"' is too long. Reduce it to 50 characters or less.")
        else:
            geo.region = list_of_changes[counter3][8]
        #######################################################################

        g.is_analyzed = False #letting the genome know it has yet to have it's new change added to the metadata table
        session.add(g)
        session.add(geo)
        session.commit()
            
        counter3 += 1
        error=""
        for item in TO_FLASH:
            error = error +"-->"+item+"\n"
        if error == "":
            error = "-All changes saved"
            
        if session.query(S_16).filter_by(genome_id=g.id).first().error != None: #update the 16S table if need be (only run it after all the saves have been considered (no need to waist time running this more than once)
            update_16S = True
            
    if update_16S:
        print colours.cyan + "updating 16S issues table..." 
        issue = "python PATH/TO/ROOT/Database_Inputs/16S_issues_table_maker.py" #the 16S table is small so making a fresh one every time there happens to be an error is not too demanding
        process = subprocess.Popen(issue, shell=True) 
        process.wait() 
        
    print colours.cyan + "updating Genomes table..." + colours.normal
    update_table = 'python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py'
    process = subprocess.Popen(update_table, shell=True)
    process.wait() #Then update the main metadata table as well
            
    return jsonify({"value":error}) #this is used for outputting our flash messages to our user. I know right? pretty stupid. But i spent an hour trying to get this to work and this was the only thing that did so deal bro.
        
    
#The following declarations are for download links (the links frim the tables page)
#You could try the send_file function: http://stackoverflow.com/questions/23354314/python-flask-downloading-a-file-returns-0-bytes
@BLISTR.route('/temp/temp<version>.fasta')
def temp(version):
    temp = "PATH/TO/ROOT/static/temp/"
    return send_from_directory(directory=temp, filename='temp'+str(version)+'.fasta')
    
@BLISTR.route('/temp/temptoxin<version>.fasta')
def temptoxin(version):
    temp = "static/temp/temptoxin"+str(version)+".fasta"
    return send_file(temp, as_attachment=True) #just another way of doing the same thing
    
@BLISTR.route('/temp/temptoxin++<version>.fasta')
def temptoxin_extra(version):
    temp = "PATH/TO/ROOT/static/temp/"
    return send_from_directory(directory=temp, filename='temptoxin++'+str(version)+'.fasta')
    
@BLISTR.route('/images/<file_name>') #Ideally this will be for downloading names
def images(file_name):
    images = "PATH/TO/ROOT/static/images/"
    return send_from_directory(directory=images, filename=file_name)


#This next one is what creates our glourious genome tables
@BLISTR.route('/genomes', methods=['GET', 'POST'])
def genomes():
    global CURRENT_XLSX
    form = TableForm()
    #Quick check on the status of the most recent prokka call
    Prokka_Check() 
    
    if form.validate_on_submit(): #if they hit the download button 
    
        to_download = request.form.getlist("check") #unicode/string list of all the genome ids that the user wants to download (the boxes they checked)
        c = "" #setting up which flags to pass processor. Only passes these flags if the user checked the boxes on the genome table page
        t = ""
        e = ""
        ffaa = ""
        fffn = ""
        tfaa = ""
        tffn = ""
        s = ""
        num_files = 0
        #The following is to check which things the user wants to download
        if form.contig.data:
            c = " -c "
            num_files += 1
        if form.toxin.data:
            t = " -t "
            num_files += 1
        if form.toxin_extra.data:
            e = " -e "
            num_files += 1
        if form.fasta_faa.data:
            ffaa = " --ffaa "
            num_files += 1
        if form.fasta_ffn.data:
            fffn = " --fffn "
            num_files += 1
        if form.toxin_faa.data:
            tfaa = " --tfaa "
            num_files += 1
        if form.toxin_ffn.data:
            tffn = " --tffn "
            num_files += 1
        if form.sixteenS.data:
            s = " -s"
            num_files += 1
            
        if num_files == 0 and not form.search.data and not form.tree_16S.data and not form.delete.data and not form.export.data: #yell at user if they do not select enough things but don't do it if they used the search function
            flash("You must select at least one type of file to export")
        elif len(to_download) == 0 and not form.search.data and not form.tree_16S.data and not form.delete.data and not form.export.data:
            flash("You must select at least one genome to export")
        elif num_files > 0 and len(to_download) > 0:#if they choose to download stuff...
            downloading = unicode_list_to_str(to_download)
            downloader = "python PATH/TO/ROOT/Database_Outputs/genome_downloader.py "
            process = subprocess.Popen(downloader + downloading + c + t + e + ffaa + fffn + tfaa + tffn + s, shell=True) #tells processor.py to run with the URL given from the form (in the webpage)
            process.wait()
            if len(to_download) == 1 and num_files == 1:
                flash("One file downloaded")
            else:
                flash("Files downloaded")
                
        if form.tree_16S.data: #if they choose to produce a 16S tree
            basedir = 'PATH/TO/ROOT/Database_Outputs/'
            db = 'PATH/TO/ROOT/fasta_files/databases/16S_db/16s_contigs.fasta'
            concat = basedir + '16S_temp.fasta'
            to_colour = "" #initializing colouring set
            db_f = open(db, 'r')
            new_file = open(concat, 'w') #file that will hold the original 16S database and the 16S information in question
            for line in db_f:
                new_file.write(line) #copyt out the original db
            db_f.close()
            for g_id in to_download: #write to file the genome name followed by the 16S sequence
                if session.query(S_16).filter_by(genome_id=int(g_id)).first().seq: #make sure the sequence exists
                    new_file.write(">" + str(session.query(Genome).filter_by(id=int(g_id)).first().name) + "\n" + str(session.query(S_16).filter_by(genome_id=int(g_id)).first().seq) + "\n")
                    to_colour = to_colour + "find searchtext=" + str(session.query(Genome).filter_by(id=int(g_id)).first().name) +";"
                else:
                    flash("Genome: "+str(session.query(Genome).filter_by(id=int(g_id)).first().name)+" skipped in 16S Tree as it has no 16S sequence")
            new_file.close()
            programs_16S = ['PATH/TO/ROOT/BLISTR_support_programs/./muscle -in '+concat+' -out '+basedir+'16S_temp2.fasta', 'PATH/TO/ROOT/Database_Outputs/Fasta2Phylip.pl '+basedir+'16S_temp2.fasta '+basedir+'16S_temp2.phy', 'PATH/TO/ROOT/BLISTR_support_programs/./raxmlHPC -m GTRGAMMA -s '+basedir+'16S_temp2.phy -n 16s_Tree -p 12345 -x 12345 -w '+basedir+' -N 10 -f a', \
            "'PATH/TO/ROOT/Database_Outputs/dendroscope/Dendroscope' -x \"open file='PATH/TO/ROOT/Database_Outputs/RAxML_bipartitions.16s_Tree';set drawer=RectangularPhylogram;"+to_colour+"set labelcolor=225 0 0;expand direction=horizontal;expand direction=vertical;expand direction=vertical;expand direction=vertical;expand direction=vertical;\""]
            for program in programs_16S:
                process = subprocess.Popen(program, shell=True)
                process.wait()
                if program.startswith('PATH/TO/ROOT/BLISTR_support_programs/./muscle'):
                    copyfile(basedir+'16S_temp2.fasta', 'PATH/TO/DOWNLOADS/16S_alignment_'+str(time.strftime("%H:%M:%S-%d-%m-%Y"))+'.fasta')
            #The user has gotten their desired outputs, now we need to remove all these temporary files!
            to_remove = ['16S_temp.fasta', '16S_temp2.fasta', '16S_temp2.phy', '16S_temp2.phy.reduced', 'RAxML_bipartitions.16s_Tree', 'RAxML_bestTree.16s_Tree', 'RAxML_bipartitionsBranchLabels.16s_Tree', 'RAxML_bootstrap.16s_Tree', 'RAxML_info.16s_Tree']
            for gtfo in to_remove:
                os.remove(basedir+gtfo) #This clean up is needed to allow users to create a new Tree as the above programs do not allow for over writting files
            flash("Alignment sequence download")
                
        if form.delete.data:
            remove_database_entries(to_download) #removes all checked entries and generates a new metadata table
            out = ""
            for g_id in to_download:
                out+=str(g_id)+"-"
            out = out.rstrip("-")
            clean_table = 'python PATH/TO/ROOT/Database_Inputs/metadata_table_maker.py -d ' + out
            process = subprocess.Popen(clean_table, shell=True)
            process.wait()
            
        if form.export.data:
            flash("Genome table downloaded")
            copyfile(CURRENT_XLSX, "PATH/TO/DOWNLOADS/genomes.xlsx") #exports our table to the downloads folder            

        if form.search.data: #If they used the search function, return the search table instead of the default one
            CURRENT_XLSX = "PATH/TO/ROOT/Database_Inputs/temp.xlsx" #updating which .xlsx file should be downloaded
            temp_maker = 'python PATH/TO/ROOT/Database_Inputs/temp_xlsx_maker.py '
            process = subprocess.Popen(temp_maker + str(form.search.data).replace("-","~").replace(" ","-"), shell=True) #create the search result table. Replaces blank spaces with dashes so that the user can enter multiple words
            process.wait()
            data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/temp.xlsx')
            data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
            data.index.name=None
            pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
            #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
            out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">") 
            HTML_format(out)
            return render_template('genome_table.html', form=form, title="Search Result for: "+str(form.search.data))
            
    
    """ Thanks to https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html for major contributions to this following bit """
    data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx')
    data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
    data.index.name=None
    pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
    #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
    out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">").replace("{","{").replace("}","}")
    HTML_format(out)
    CURRENT_XLSX = "PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx"
    return render_template('genome_table.html', form=form, title="Genome Table") #tables=[out],

#A copy of the Genomes table that shows all the entries with issues regarding their 16S results
@BLISTR.route('/issues', methods=['GET', 'POST'])
def issues():
    global CURRENT_16S_XLSX
    form = TableForm()
    if form.validate_on_submit(): #if they hit the download button 
    
        to_download = request.form.getlist("check") #unicode/string list of all the genome ids that the user wants to download (the boxes they checked)
        c = "" #setting up which flags to pass processor. Only passes these flags if the user checked the boxes on the genome table page
        t = ""
        e = ""
        num_files = 0
        if form.contig.data:
            c = " -c "
            num_files += 1
        if form.toxin.data:
            t = " -t "
            num_files += 1
        if form.toxin_extra.data:
            e = " -e"
            num_files += 1
        if num_files == 0 and not form.search.data and not form.export.data: #yell at user if they do not select enough things but don't do it if they used the search function
            flash("You must select at least one type of file to export")
        elif len(to_download) == 0 and not form.search.data and not form.export.data:
            flash("You must select at least one genome to export")
        else:                
            downloading = unicode_list_to_str(to_download)
            downloader = "python PATH/TO/ROOT/Database_Outputs/genome_downloader.py "
            process = subprocess.Popen(downloader + downloading + c + t + e, shell=True) #tells processor.py to run with the URL given from the form (in the webpage)
            process.wait()
            if len(to_download) == 1 and num_files == 1:
                flash("One file downloaded")
            else:
                flash(str(num_files*len(to_download))+" files downloaded")
                
        if form.export.data:
            flash("16S table downloaded")
            copyfile(CURRENT_16S_XLSX, "PATH/TO/DOWNLOADS/16S_data.xlsx") #exports our table to the downloads folder 
                
        if form.search.data: #If they used the search function, return the search table instead of the default one
            CURRENT_16S_XLSX = "PATH/TO/ROOT/Database_Inputs/temp.xlsx"
            temp_maker = 'python PATH/TO/ROOT/Database_Inputs/temp_xlsx_maker.py '
            process = subprocess.Popen(temp_maker + str(form.search.data).replace("-","~").replace(" ","-") + ' -i', shell=True) #create the search result table
            process.wait()
            data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/temp.xlsx')
            data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
            pd.set_option('display.max_colwidth', -1)
            data.index.name=None
            #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
            out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">") 
            return render_template('issues.html', tables=[out], form=form, title="Search Result for: "+str(form.search.data))
            
    
    """ Thanks to https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html for major contributions to this bit """
    data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/16S_issues.xlsx')
    data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
    data.index.name=None
    pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
    #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
    out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">") 
    CURRENT_16S_XLSX = "PATH/TO/ROOT/Database_Inputs/16S_issues.xlsx"
    return render_template('issues.html', tables=[out], form=form, title="16S Issue Table")
    
    
@BLISTR.route('/toxin_trees', methods=['GET', 'POST'])
def toxin_trees():
    form = TableForm()
    if form.validate_on_submit():
        
        try:
            int(request.form.getlist("check")[-1]) #test to see if the last entry is a number (i.e. they clicked a checkbox)
            test = True
        except:
            test = False        
        if form.tree.data and test:
            boxes = request.form.getlist("check")
            place_holders = []
            genome_ids = []
            #This following bit is to extract the palce holder genes and the genome ids from the boxes list
            for value in boxes:
                try:
                    genome_ids.append(int(value)) #if it is a genome, the value will be an int and this will work. If it is a placeholder, this value will be a string and an error will be thrown
                except:
                    place_holders.append(str(value))
            
            basedir = 'PATH/TO/ROOT/Database_Outputs/'
            concat = basedir + 'toxin_tree_temp.fasta'
            to_colour = "" #initializing colouring set
            new_file = open(concat, 'w')
            for place_holder in place_holders:
                p = session.query(PlaceHolderToxins).filter_by(name=place_holder.replace("~"," ")).first() #picks out the place holders we want from the db. The rstrip on placeholder is just to make sure that the formatting is okay
                what_we_want = ">"+p.name.replace(" ","-").replace(":","-")+"--"+p.data.replace(":","-")+"\n"+p.seq+"\n" #formats the placeholder's data to be outputeed to a big file to make a tree from
                new_file.write(what_we_want)
            
            for g_id in genome_ids: #write to file the genome name followed by the toxin sequence from the database
                toxins = session.query(Toxin).filter_by(genome_id=int(g_id)).all()
                counter = 0
                for tox in toxins:
                    extra = ""
                    if counter > 0:
                        extra = "_"+str(counter+1)+"-"+tox.best_hit #genome_2-B, for example
                    new_file.write(">" + str(session.query(Genome).filter_by(id=int(g_id)).first().name)+extra + "\n" + tox.seq[tox.bp_before:-tox.bp_after] + "\n")
                    to_colour = to_colour + "find searchtext=" + str(session.query(Genome).filter_by(id=int(g_id)).first().name) +";"
                    counter += 1
            new_file.close()
            programs_tox = ['PATH/TO/ROOT/BLISTR_support_programs/./muscle -in '+concat+' -out '+basedir+'tox_temp2.fasta', 'PATH/TO/ROOT/Database_Outputs/Fasta2Phylip.pl '+basedir+'tox_temp2.fasta '+basedir+'tox_temp2.phy', 'PATH/TO/ROOT/BLISTR_support_programs/./raxmlHPC -m GTRGAMMA -s '+basedir+'tox_temp2.phy -n tox_Tree -p 12345 -x 12345 -w '+basedir+' -N 10 -f a', \
            "'PATH/TO/ROOT/Database_Outputs/dendroscope/Dendroscope' -x \"open file='PATH/TO/ROOT/Database_Outputs/RAxML_bipartitions.tox_Tree';set drawer=RectangularPhylogram;"+to_colour+"set labelcolor=225 0 0;expand direction=horizontal;expand direction=vertical;expand direction=vertical;expand direction=vertical;expand direction=vertical;\""]
            for program in programs_tox:
                process = subprocess.Popen(program, shell=True)
                process.wait()
                if program.startswith('PATH/TO/ROOT/BLISTR_support_programs/./muscle'):
                    copyfile(basedir+'tox_temp2.fasta', 'PATH/TO/DOWNLOADS/toxin_alignment_'+str(time.strftime("%H:%M:%S-%d-%m-%Y"))+'.fasta')
            #The user has gotten their desired outputs, now we need to remove all these temporary files!
            to_remove = ['toxin_tree_temp.fasta', 'tox_temp.fasta', 'tox_temp2.fasta', 'tox_temp2.phy', 'tox_temp2.phy.reduced', 'RAxML_bipartitions.tox_Tree', 'RAxML_bestTree.tox_Tree', 'RAxML_bipartitionsBranchLabels.tox_Tree', 'RAxML_bootstrap.tox_Tree', 'RAxML_info.tox_Tree']
            for gtfo in to_remove:
                try:
                    os.remove(basedir+gtfo)
                except:
                    pass
            
            flash("Alignment sequence download")
                
        elif form.search.data: #If they hit the search button:
            out_tables = [] #the tables we will output
            out_tables.append(html_place_holders_table())
            
            temp_maker = 'python PATH/TO/ROOT/Database_Inputs/temp_xlsx_maker.py '
            process = subprocess.Popen(temp_maker + str(form.search.data).replace("-","~").replace(" ","-"), shell=True) #create the search result table
            process.wait()
            data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/temp.xlsx')
            data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
            data.index.name=None
            pd.set_option('display.max_colwidth', -1)
            #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
            out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" align=\"center\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">")
            out_tables.append(out)
            HTML_format_toxin_tree(out_tables)
            return render_template('toxin_trees.html', form=form, title="Search Result for: "+str(form.search.data))
            
        else:
            flash("You must select at least one genome from the Genome table")
        
    out_tables = [] #the tables we will output
    out_tables.append(html_place_holders_table()) #just generates the placholders table
    
    data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx')
    data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
    data.index.name=None
    pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
    #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
    out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" align=\"center\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">")
    out_tables.append(out)   
    HTML_format_toxin_tree(out_tables)
    
    return render_template('toxin_trees.html', form=form, title="Toxin Trees")     
    
@BLISTR.route('/maps', methods=['GET', 'POST'])
def maps(): #function for a super sweet, increadibly pointless, map
    #Thanks to Saul Burgos for his fabulous google maps things. See his github at: https://github.com/SaulBurgos/easyLocator
    form = MapForm()
    print form.errors
    if form.validate_on_submit(): #map with only the specifyed type in it
        #I'm doing up the html I will write to maps.html
        to_write ='''{% extends "base.html" %}
    
            {% block content %}
              <form action="" method="POST" name="result">
              {{ form.hidden_tag() }}
              {{ form.csrf_token }}
              Map type: {{ form.toxin_type }}
              <input type="submit" value="Submit">
              </form>
            
              <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js"></script>
              <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
              <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
            
              <script type=text/javascript src="{{  url_for('static', filename='markerclusterer.js') }}"></script>
              <script type=text/javascript src="{{  url_for('static', filename='easyLocator.js') }}"></script>
              <link rel=stylesheet type=text/css href="{{ url_for('static', filename='easyLocator.css') }}">
              
            
            <div id="locatorList" style="height:875px"></div>
            	<script>
                  var data = ['''
        
        genomes = session.query(Genome).all()
        out_list = []
        for g in genomes:
            if not session.query(Toxin).filter_by(genome_id=g.id).first(): #if it doesn't have a toxin, we don't want it
                if form.toxin_type.data == "None" and not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lat).lower() == "none" and not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lng).lower() == "none": #unless, of course, they were looking for None type
                    out_list.append(g) 
                continue
            elif not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lat).lower() == "none" and not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lng).lower() == "none" and str(session.query(Toxin).filter_by(genome_id=g.id).first().best_hit) == form.toxin_type.data:
                out_list.append(g) #filter out all the poor soles without lattitudes or longitudes
                
        for g in out_list: #start again with our new genomes
            to_write+="{"#doing this here because python gets angry if I do it in the line below
            to_write+='''title: '{genome_name} type:{t_type}',
            description: 'Source information: {source_info}, Institution: {institution}, Author: {author}, Source type: {clinical_or_environmental}',
            lat: {latitude},
            lng: {longitude}'''.format(
            genome_name=g.name,
            t_type= "None" if session.query(Toxin).filter_by(genome_id=g.id).first() == None else session.query(Toxin).filter_by(genome_id=g.id).first().best_hit,
            source_info=g.source_info,
            institution=g.institution,
            author=g.author,
            clinical_or_environmental=g.clinical_or_environmental,
            latitude=session.query(GeographicLocation).filter_by(genome_id=g.id).first().lat,
            longitude=session.query(GeographicLocation).filter_by(genome_id=g.id).first().lng
            )
            to_write += "},\n"
        #can't forget to get rid of that last pesky comma
        to_write = to_write.rstrip(",\n")+'''
                  ];
                  $( document ).ready(function() {
                    $('#locatorList').easyLocator({
                       myLocations: data
                    });
                  });
               </script>
            
            {% endblock %}
        '''
        
        maps = open("PATH/TO/ROOT/templates/maps.html", 'w')
        maps.write(to_write)
        maps.close()
        
        return render_template('maps.html', form=form, title="Maps")        
    
    else:
        #A big ol' map of everything
        to_write ='''{% extends "base.html" %}
    
            {% block content %}
              <form action="" method="POST" name="result">
              {{ form.hidden_tag() }}
              {{ form.csrf_token }}
              Map type: {{ form.toxin_type }}
              <input type="submit" value="Submit">
              </form>
            
              <script type="text/javascript" src="https://maps.googleapis.com/maps/api/js"></script>
              <meta content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" name="viewport">
              <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
            
              <script type=text/javascript src="{{  url_for('static', filename='markerclusterer.js') }}"></script>
              <script type=text/javascript src="{{  url_for('static', filename='easyLocator.js') }}"></script>
              <link rel=stylesheet type=text/css href="{{ url_for('static', filename='easyLocator.css') }}">
              
            
            <div id="locatorList" style="height:875px"></div>
            	<script>
                  var data = ['''
        
        genomes = session.query(Genome).all()
        out_list = []
        for g in genomes:
            if not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lat).lower() == "none" and not str(session.query(GeographicLocation).filter_by(genome_id=g.id).first().lng).lower() == "none":
                out_list.append(g) #filter out all the poor soles without lattitudes or longitudes
                
        for g in out_list: #start again with our new genomes
            t_type = "None"
            if session.query(Toxin).filter_by(genome_id=g.id).all() >= 1:
                t_type = "" #setting up toxins to handle n number of toxins. (not doing this for reduced maps, however)
                for tox in session.query(Toxin).filter_by(genome_id=g.id).all():
                    if tox.best_hit == None or tox.best_hit.lower() == "none":
                        t_type += "None, "
                        continue
                    t_type += tox.best_hit + ", "
                t_type = t_type.rstrip(", ")
            if t_type == "":
                t_type = "None"
                
            to_write+="{"#doing this here because python gets angry if I do it in the line below
            to_write+='''title: '{genome_name} type:{t_type}',
            description: 'Source information: {source_info}, Institution: {institution}, Author: {author}, Source type: {clinical_or_environmental}',
            lat: {latitude},
            lng: {longitude}'''.format(
            genome_name=g.name,
            t_type= t_type,
            source_info=g.source_info,
            institution=g.institution,
            author=g.author,
            clinical_or_environmental=g.clinical_or_environmental,
            latitude=session.query(GeographicLocation).filter_by(genome_id=g.id).first().lat,
            longitude=session.query(GeographicLocation).filter_by(genome_id=g.id).first().lng
            )
            to_write += "},\n"
        #can't forget to get rid of that last pesky comma
        to_write = to_write.rstrip(",\n")+'''
                  ];
                  $( document ).ready(function() {
                    $('#locatorList').easyLocator({
                       myLocations: data
                    });
                  });
               </script>
            
            {% endblock %}
        '''
        
        maps = open("PATH/TO/ROOT/templates/maps.html", 'w')
        maps.write(to_write)
        maps.close()
        
        return render_template('maps.html', form=form, title="Maps")
        

@BLISTR.route('/subtype_trees', methods=['GET', 'POST'])
def subtype_trees():
    form = TableForm()
    if form.validate_on_submit():
        
        genome_ids = request.form.getlist("check")
        As = request.form.getlist("A")
        Bs = request.form.getlist("B")
        Cs = request.form.getlist("C")
        CDs = request.form.getlist("CD")
        Ds = request.form.getlist("D")
        DCs = request.form.getlist("DC")
        Es = request.form.getlist("E")
        Fs = request.form.getlist("F")
        Gs = request.form.getlist("G")
        
        nested_selection = [As, Bs, Cs, CDs, Ds, DCs, Es, Fs, Gs]
        
        if form.tree.data and len(genome_ids) >0:
            
            basedir = 'PATH/TO/ROOT/Database_Outputs/'
            concat = basedir + 'toxin_tree_temp.fasta'
            to_colour = "" #initializing colouring set
            new_file = open(concat, 'w')
            for selection in nested_selection:
                for subtype in selection:
                    p = session.query(PlaceHolderSubtypes).filter_by(name=subtype).first() #picks out the place holders we want from the db. The rstrip on placeholder is just to make sure that the formatting is okay
                    what_we_want = ">"+p.name+"--"+p.data.replace(":","-").replace(" ","-")+"\n"+p.seq+"\n" #formats the placeholder's data to be outputeed to a big file to make a tree from
                    new_file.write(what_we_want)
            
            #The following bit can be takes as is from toxin_trees as nothing need be changed
            for g_id in genome_ids: #write to file the genome name followed by the toxin sequence from the database
                toxins = session.query(Toxin).filter_by(genome_id=int(g_id)).all()
                counter = 0
                for tox in toxins:                    
                    extra = ""
                    if counter > 0:
                        extra = "_"+str(counter+1)+"-"+tox.best_hit.replace(" ","") #genome_2-B, for example
                    seq = tox.seq[tox.bp_before:-tox.bp_after] 
                    #IF YOU ARE GETTING WONKY TREES, IT LIEKLY HAS TO DO WITH THE SPLICING OF THE TOXIN++ SEQUENCE
                    if seq.startswith("TG"):
                        seq = "A"+seq
                    elif not seq.startswith("ATG"):
                        print colours.red + "NOTE: Toxin '"+tox.best_hit + "' of Genome '"+str(session.query(Genome).filter_by(id=int(g_id)).first().name)+extra +"' did not start with ATG (nor TG)" + colours.normal
                    seq = transeq(seq)
                    new_file.write(">" + str(session.query(Genome).filter_by(id=int(g_id)).first().name).replace(" ","")+extra + "\n" + seq + "\n")
                    to_colour = to_colour + "find searchtext=" + str(session.query(Genome).filter_by(id=int(g_id)).first().name) +";"
                    counter += 1
            new_file.close()
            programs_tox = ['PATH/TO/ROOT/BLISTR_support_programs/./muscle -in '+concat+' -out '+basedir+'tox_temp2.fasta', 'PATH/TO/ROOT/Database_Outputs/Fasta2Phylip.pl '+basedir+'tox_temp2.fasta '+basedir+'tox_temp2.phy', 'PATH/TO/ROOT/BLISTR_support_programs/./raxmlHPC -m PROTGAMMALG -s '+basedir+'tox_temp2.phy -n tox_Tree -p 12345 -x 12345 -w '+basedir+' -N 20 -f a', \
            "'PATH/TO/ROOT/Database_Outputs/dendroscope/Dendroscope' -x \"open file='PATH/TO/ROOT/Database_Outputs/RAxML_bipartitions.tox_Tree';set drawer=RectangularPhylogram;"+to_colour+"set labelcolor=225 0 0;expand direction=horizontal;expand direction=vertical;expand direction=vertical;expand direction=vertical;expand direction=vertical;\""]
            for program in programs_tox:
                process = subprocess.Popen(program, shell=True)
                process.wait()
                if program.startswith('PATH/TO/ROOT/BLISTR_support_programs/./muscle'):
                    copyfile(basedir+'tox_temp2.fasta', 'PATH/TO/DOWNLOADS/subtype_alignment_'+str(time.strftime("%H:%M:%S-%d-%m-%Y"))+'.fasta')
            #The user has gotten their desired outputs, now we need to remove all these temporary files!
            to_remove = ['toxin_tree_temp.fasta', 'tox_temp.fasta', 'tox_temp2.fasta', 'tox_temp2.phy', 'tox_temp2.phy.reduced', 'RAxML_bipartitions.tox_Tree', 'RAxML_bestTree.tox_Tree', 'RAxML_bipartitionsBranchLabels.tox_Tree', 'RAxML_bootstrap.tox_Tree', 'RAxML_info.tox_Tree']
            for gtfo in to_remove:
                try:
                    os.remove(basedir+gtfo)
                except:
                    pass
            
            flash("Alignment sequence download")
                
        elif form.search.data: #If they hit the search button:
            out_tables = [] #the tables we will output
            out_tables.append(html_place_holders_table_for_subtypes())
            
            temp_maker = 'python PATH/TO/ROOT/Database_Inputs/temp_xlsx_maker.py '
            process = subprocess.Popen(temp_maker + str(form.search.data).replace("-","~").replace(" ","-"), shell=True) #create the search result table
            process.wait()
            data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/temp.xlsx')
            data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
            data.index.name=None
            pd.set_option('display.max_colwidth', -1)
            #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
            out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" align=\"center\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">")
            out_tables.append(out)
            HTML_format_subtype_tree(out_tables)
            return render_template('subtype_trees.html', form=form, title="Search Result for: "+str(form.search.data))
            
        else:
            flash("You must select at least one genome from the Genome table")
        
    out_tables = [] #the tables we will output
    out_tables.append(html_place_holders_table_for_subtypes()) #just generates the placholders table
    
    data = pd.read_excel('PATH/TO/ROOT/Database_Inputs/metadata_table.xlsx')
    data.set_index(['Check boxes'], inplace=True) #sets which column will be all blue (checkbox column)
    data.index.name=None
    pd.set_option('display.max_colwidth', -1) #The integer sets how many characters can be shown in a single cell on the table. -1 means as many as you would like
    #this is to allow the "<"s to show up as they should when they are rendered by this table maker. Otherwise they are their speceial character equivolents which do not work. Also the other replaces are to get desired formatting so that is something
    out = data.to_html(classes='male').replace("&lt;", "<").replace("&gt;", ">").replace("<table border=\"1\" class=\"dataframe male\">", "<table border=\"1\" align=\"center\" class=\"sortable\">").replace("<tr style=\"text-align: right;\">", "<tr style=\"text-align: center;\">")
    out_tables.append(out)   
    HTML_format_subtype_tree(out_tables)
    
    return render_template('subtype_trees.html', form=form, title="Subtype Trees")
        
        
#The following bit are error handlers. So when there is an error you will get one of these custom pages instead of the ugly default error page
@BLISTR.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
@BLISTR.errorhandler(500)
def program_error(error):
    print colours.yellow + "Oh dear... there seems to be an error. This is what we got: " + colours.red
    import traceback
    print traceback.print_exc()
    print colours.normal
    return render_template('500.html'), 500

if __name__ == '__main__':
    BLISTR.run(debug=False) #set this to True if you would like to see all errors (True also has an saves you make to the backend immediatly being applied to the app)
    #ALWAYS make sure this is set to False when doing a demonstration!!!
