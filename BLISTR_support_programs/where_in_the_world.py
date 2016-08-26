# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 08:34:12 2016

@author: Owen Neuber

a script that will take all of our genome files, extract the locational information 
from those files and then with that locational information, slap on a latitude and 
longitude to replace None,None on all contig headers. This program will skip any
files that already have not latitude and longitude and files without any reginal
or national geogrphic location.
"""

import os
import requests
import glob
import subprocess
from tqdm import tqdm

files = glob.glob('PATH/TO/ROOT/fasta_files/*.fasta')
num_of_files = len(files)
errorus_files = []

with tqdm(total=num_of_files) as pbar:
    for fi in files:
        fasta = open(fi, 'r')
        skip = False #setting up a variable to let us know if we broke out of the following for loop
        first_line = True #variable to let us know if we are on the first line of the file or not
        new_file_data = "" #variable which will stored all of the data which will go into a modified file (if applicable)
        for line in fasta:
            if first_line:
                first_line = False #so we don't come back here
                #if not lat & lng are None and country or region are not None (i.e. check if they do not meet our criteria)
                if not ((line.split(",")[7].capitalize() == "None" or line.split(",")[8].capitalize() == "None") and (line.split(",")[9].capitalize() != "None" or line.split(",")[10].capitalize() != "None")):
                    skip = True
                    break
                #now if we get here, we have all that we need to do our work...
                country, o_country, region, o_region = [None]*4 #set up variables that will be None if we have no information on country or region
                if line.split(",")[9].capitalize() != "None":
                    o_country = line.split(",")[9] #what country was before I modified it
                    country = line.split(",")[9].replace(" ", "") 
                if line.split(",")[10].capitalize() != "None":
                    o_region = line.split(",")[10] #what region was before I modified it
                    region = line.split(",")[10].replace("- ",",+").replace(" ","").rstrip("\n") #taking the region portion and formatting it as needed
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
                    
                    new_header = line.replace("None,None,"+str(o_country)+","+str(o_region), lat+","+lng+","+str(o_country)+","+str(o_region)).replace(">1","").rstrip("\n")+"\n" #changing the old header to the one we will use now. Also removing the number 1 from it so that contig numbers can be adapted more easliy
                except:
                    print "There was an Error with the fasta file: " + os.path.basename(fi) #It does not work on all files. I got 2 error out of 294 files (pretty good though I'd say)
                    print "You will need to edit that file's lat/lng manually."
                    print "Its location is: " + o_region + ", "+ o_country
                    errorus_files.append(os.path.basename(fi)) #store a list of all the files that had problems to be spit out at the end

            if line.startswith(">"):
                line = line.split(",")[0]+new_header #replace our old header with our new one (with the old header's contig number)
            
            new_file_data += line #finally, adding our information to the big string that will be outputted via fasta.write()
                
        fasta.close()
        if skip:
            pbar.update(1)
            continue # skip the rest of the data manipulation for this file
            
        fasta = open(fi, 'w') #now just rewriting out to the file!
        fasta.write(new_file_data)
        fasta.close()
        p = subprocess.Popen("clear", shell=True)
        p.wait() #claer our gritty screen
        pbar.update(1)

print "cleaning up..."      
process = subprocess.Popen("find PATH/TO/ROOT/fasta_files/ -type f -print0 | xargs -0 sed -i " + "'s/33.8499292,-88.4509873/None,None/g'", shell=True) #for some reason, fasta with None,None for country and region got 33.8499292,-88.4509873 for lat and lng. this should revert that
process.wait()

if len(errorus_files) > 0: #if there were any problems
    print "Errors with the following files: "
    for error in errorus_files: #tell the user which files there were problems with
        print error
    print "You will have to manually change their header information"

print "done"