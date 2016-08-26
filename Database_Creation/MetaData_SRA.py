#! /usr/bin/python2.7

"""
@author: Owen Neuber

File to extract desired Metatdata relating to Clostridium botulinum from NCBI.
A one time user to set up much of the database. Just here as an archive, basically.

"""

#from sys import argv
#import os
#import re
import urllib2
from time import time

List = open("ParsedSRA.list", 'r')
tot =-1.0 #-1 to account for the first line which does not count
for row in List: #quick little thing to figure out how many lines are being computed for percent purposes
    tot +=1.0
List.close()

print("The monkey has reached the computer")
mon_type = True #set up for progress tracker
mon_ban = True

out = open("ParsedSRA.list.2", 'w')
List = open("ParsedSRA.list", 'r')
search = ["<th>strain","<th>serotype", "<th>subgroup","author","<th>collection date", "Clinical", "<th>isolation source","SRA", "None", "None", "<th>geographic location" ]
count = 0 #The wierd <th> above is to ensure that the target we want, and not someting else with the same name, is extracted
c_bot = "Clostridium botulinum"
temp = "" #initializing a temporary variable

t = time() #at top for timing purposes

for row in List:
    serovar = False #used to check if the idiots who enter this stuff used serovar
    counter1 = -1 #for every line this needs to be reset
    #            name,   type,  group, author, date,   Clinical,  source,  SRA,   lat,    long, country, region
    par_list = ["None", "None", "None","None","None", "Clinical", "None","None", "None", "None", "None", "None" ] #emptying parallel list to be filled with what we want
    if(count != 0):
        #if True: #if you want to debug with out the try and catch, just comment out try: & except: and put this line back in
        try: #try out everything
            SAMN = row.split("\t")[3]
            author = row.split("\t")[1]
            #print(SAMN)
            response = urllib2.urlopen("http://www.ncbi.nlm.nih.gov/biosample/"+SAMN)
            page_source = response.read()
            man_meat =  page_source.split("messagearea")[1]
            for search_name in search:
                counter1 +=1 #keeps parallel lists in check
                """
                something that was useful and I put a lot of thought into. It is no longer useful
                if counter1 == 0: #if we are looking for genome name, do this special extract:
                    g_name = page_source.split("title>")[1][:-2] #gets just the title. "title>" is specific enough to get only too results, but not too specific to get only one. Making it perfect. The [:-2] is to remove a "</" at the end of it
                    if c_bot in g_name: #remove that pesky "Clostridium botulinum" from the start of a good name
                        g_name = g_name[22:] #c_bot is 21 chatacters + 1 for a space, so we will start without it
                    if "Str." in g_name or "str." in g_name:
                        g_name = g_name[5:] #"str. " is 5 character, so we will start after that
                    if "  - BioSample - NCBI" in g_name:
                        g_name = g_name[:20] #The unwanted string is 20 characters so this should remove it
                    par_list[0] = g_name
                    continue            
                """
                if counter1 == 5 or counter1 == 7:
                    continue #if we hit Clinical, just skip it. Do the same for HC/SRA
                elif search_name == "<th>serotype":
                    if author == "phaC": #Health Canada was dumb and entered all our serotypes as serovars, this is to account for that
                        serovar = True #set to true for later cleaving
                        search_name = "<th>serovar"                        
                    elif man_meat.find(search_name) == -1:
                        search_name = "<th>serovar" #just incase poeople are dumb, we will catch serovar entries too
                        serovar = True #set to true for later cleaving
                elif counter1 == 3: #if it is author, we want to use the author variable
                    par_list[3] = author
                    if author == "phaC": #if author is "phaC", set institution to "HC", else "SRA"
                        par_list[7] = "HC"
                    else:
                        par_list[7] = "SRA"                
                    continue #then we want to skip the rest of this
                if man_meat.find(search_name) == -1:
                    continue #we don't find it, we skip it
                    
                index = man_meat.find(search_name) + len(search_name) + 9 #the plus 9 is to account for the "</th><td>" which is always there
                par_list[counter1] = (man_meat[index:]).split(" </td>")[0] #splices into what is after the index number. Then turns this result into a list (divided at "</td>") and we take the first instance of the list (the thing we are interested in)
                
                try:
                    #the following if is a supercheck for synonyms to "None" and we will replace the synonym with "None"
                    if counter1 == 0 and " " in par_list[0]: #if there are spaces in the name, bad news bears, so replace with a "-"
                        par_list[0] = par_list[0].replace(" ", "-")
                    if par_list[counter1].startswith("<a href="): #geographic location is once again the problem child. We need to splice out the location in order to avoid annoying hyperlink nonesense
                        par_list[counter1] = par_list[counter1].split(">")[1].split("<")[0] #this takes the gross geographic location, and starts it after a ">" (which is the end of the hyperlink setup) and then it ends it after "<" (which preludes to "</a>)
                    if counter1 == 2: #if group has a space in it, remove it
                        par_list[2] = "." + par_list[2].replace(" ", "") #replace space with nothing. Add a period at the front for later formatting things
                    if counter1 == 10: #need to chop geographic location up a into country and region
                        temp = par_list[10].split(":")
                        par_list[10] = temp[0] #extracting just the country name
                        par_list[11] = temp[1].replace(", ", " - ") #extract regoin and remove any unwanted commas
                        if par_list[11].startswith(" "): #we want to cleave the front if it stars with a space
                            par_list[11] = par_list[11][1:]                        
                    if counter1 == 1: #if we are dealing with serotype, it must be modified
                        if "Type " in par_list[1] or "type " in par_list[1]:
                            if serovar: #if Ture, cleave 9 to remove "serotype"
                                par_list[1] = par_list[1][9:]
                            else:
                                par_list[1] = par_list[1][5:] #start after the first 5 characters (i.e. "type ")
                        par_list[1] = "." + par_list[1] #we always want a period before the letter because Nick said so
                    if counter1 == 6 and "," in par_list[6]:
                        par_list[6] = par_list[6].replace(", ", " - ")
                    if par_list[counter1] == "Missing" or par_list[counter1] == "missing" or par_list[counter1] == "Not applicable" or par_list[counter1] == "N/A":
                        par_list[counter1] = "None"
                except:
                    par_list[counter1] = "None" #I am not goint to allow geographic location to ruin things futher. If it does, we will just exclude it!
                """
                #The following is stuff that should work. I still think it should work. It does not work. The above stuff works
                end_index = index + man_meat.find("</td>", index) #when we hit " <" we want to stop recording </td>
                print("end: " + str(end_index))
                thing_we_want_out = man_meat[index:end_index] #only considers the characters we want
                print(thing_we_want_out)
                
                par_list[counter1] = thing_we_want_out
                """
            #has to be out of the search_name loop otherwise there will be a billion writes to the file (and that was bad news bears)
            title = par_list[0] #the defualt if group and serotype are None
            if par_list[1].startswith("."): #serotype will start with a "." so long as it is not "None"
                title = par_list[0] + par_list[1] #if we have only serotype and name, the following if will fail and the output will be name.serotype
                if par_list[2].startswith(".Group"): #group will always star with ".Group" so long as it exists
                    title = par_list[0] + par_list[1] + par_list[2] #if all goes well, the output will be name.serotype.group
            elif par_list[2].startswith(".Group"): #if we have group but not serotype, this will have ouput: name.group
                title = par_list[0] + par_list[2]
            #now for the following you may think there is a better way, but that will likely result in nested lists (bad news bears) and in terms of speed, this is quite fast
            men = [title, par_list[3], par_list[4], par_list[5], par_list[6], par_list[7], "None", "None", par_list[10], par_list[11]]
            
            finallly = "" #empty variable primed for output
            for man in men:
                finallly = finallly + man + "\t" #makes a grand, tab separated, string (the tab is on the outside ti account for the first empty instance of finallly)
            out.write((finallly + "\n"))
        except:
            out.write("ERROR with genome: " +  row.split("\t")[0] + ", SAMN: " + row.split("\t")[3] + "\n") #if there was an error somewhere (prolly an index error), shoots off an error + name of the genome and SAMN
        #if count == 17: #sets the number of line syou want to process before breaking
        #    break #add this break back in if you want to debug only the first entry
            
    per_comp = count/tot*100 #+ "%" #calculates our progess and outputs that to user
    
    if count == 2: #a fun output to estimate how long this process will likely take (2 for an average time)
        t = time() - t
        t = t * (tot-2)/60/2 #divided by 60 to convert to minutes (divided by 2 for average time)
        print("The monkey will likely take " + str(t) + " minutes to complete this task")
        
    if per_comp >= 33.33 and mon_type:
        print("The monkey is starting to type")
        mon_type = False #ensures no repeats because that would be gross
    elif per_comp >= 66.66 and mon_ban:
        print("The monkey just went bananas! Hit him with a tranq dart!")
        mon_ban = False
    count += 1 #to skip the first line of ParsedSRA.list file
    
out.close()
List.close()
print("The monkey is sleeping happily now") #script is finished