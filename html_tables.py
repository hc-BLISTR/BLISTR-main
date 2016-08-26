# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 08:30:56 2016

@author: Owen Neuber

html tables maker. This makes an html table for use with the tables html page.
This file function is called in views.py for the tables function. It has been
expanded to make the html tables of all other pages featuring an html table.
"""

from sqlalchemy import create_engine
from models import PlaceHolderToxins, PlaceHolderSubtypes
from sqlalchemy.orm import sessionmaker

def HTML_format(out):
    """
    A single function which you call to create genome_table.html for use with the 
    BLISTR app. Used to avoid issues occurring when you have {{ }} in the table
    which you wish to render. This sould be run every time before genome_table.html
    is called to be rendered.
    out is a fully formmated html table to be injected into the file
    """
    r = open('PATH/TO/ROOT/templates/genome_table.html','w')
            
    #Extremly cheesy way to get out of an even more cheesy problem
    r.write('''
    {% extends "base.html" %}
    
    {% block content %}
    <title>Genomes</title>
    <form action="" method="POST" name="result">
    {{ form.hidden_tag() }}
    
    <script language="JavaScript">
    function toggle(source) {
      checkboxes = document.getElementsByName('check');
      for(var i=0, n=checkboxes.length;i<n;i++) {
        checkboxes[i].checked = source.checked;
      }
    }
    </script>
    
    <div class=page>
      <h1>{{ title }}</h1>
      <input type=submit value=Download>
      <font size="4">
      Contig File: {{ form.contig }}<span style="margin-left:1em">
      Toxin File: {{ form.toxin }}<span style="margin-left:1em">
      Toxin++ File: {{ form.toxin_extra }}<span style="margin-left:1em">
      Genome faa: {{ form.fasta_faa }}<span style="margin-left:1em">
      Genome ffn: {{ form.fasta_ffn }}<span style="margin-left:1em">
      Toxin++ faa: {{ form.toxin_faa }}<span style="margin-left:1em">
      Toxin++ ffn: {{ form.toxin_ffn }}<span style="margin-left:1em">
      16S Sequence: {{ form.sixteenS }}<span style="margin-left:1em">
      Select All Genomes: <input type="checkbox" onClick="toggle(this)" />
      <br>
      {{ form.tree_16S }}
      <br>
      {{ form.delete }}
      <br>
      {{ form.export }}
      <br>
      Search For: {{ form.search(size=30, maxlength=400) }}
      </font>
      <input type=submit value=Search>
      ''')
    r.write(out)
    r.write('''
        </div>
    </form>
    {% endblock %})
    ''')
    r.close()
    return None
    
    
def html_place_holders_table():
    """
    Function to produce an html table armed with check boxes with the names of
    the special place holder toxins we wish to make a toxin tree with. 
    Takes in nothing but uses the BLISTR database.
    It will then extract the names of the toxin placeholders from the db
    Returns the html table used in toxin_trees.html
    """
    engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
    Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
    session = Session()
    counter = 0
    html = "<table align=\"center\"class=\"dataframe male\"><thead></thead><tbody><tr><th colspan=\"3\" ><font size=\"6\">Placeholder Toxins</font></th></tr><tr>"
    BoNT = session.query(PlaceHolderToxins).all()
    for tox in BoNT:
        html = html+"<td><font size=\"5\"><input type=checkbox name=check value="+tox.name.replace(" ","~")+" checked=\"checked\"> BoNT:"+tox.name.rstrip(" ")+",<span style=\"margin-left:1em\"> "+tox.data+"</font></td>"
        counter += 1
        if counter % 3 == 0: #every third iteration we will go down a row
            html = html + "</tr><tr>"
    html = html + "</tr></tbody></table>"
    return html
    
def HTML_format_toxin_tree(out):
    """
    A single function which you call to create toxin_trees.html for use with the 
    BLISTR app. Used to avoid issues occurring when you have {{ }} in the table
    which you wish to render. This sould be run every time before toxin_trees.html
    is called to be rendered.
    out is a list of fully formmated html tables to be injected into the file
    """
    r = open('PATH/TO/ROOT/templates/toxin_trees.html','w')
    r.write('''{% extends "base.html" %}

    {% block content %}
    <title>Genome Tree</title>
    <form action="" method="POST" name="result">
    {{ form.hidden_tag() }}
    
    <script language="JavaScript">
    function toggle(source) {
      checkboxes = document.getElementsByName('check');
      for(var i=0, n=checkboxes.length;i<n;i++) {
        checkboxes[i].checked = source.checked;
      }
    }
    </script>
    
    <div class=page>
    <h1>{{ title }}</h1>
    {{ form.tree }}<br>
    ''')
    r.write(out[0])
    r.write('''      
    <font size="5"><b>Search For:</b></font> {{ form.search(size=30, maxlength=400) }}
    <input type=submit value="Search"><br>
    Select All: <input type="checkbox" onClick="toggle(this)" />
    ''')
    r.write(out[1])
    r.write('''    
    </div>
    </form>    
    
    {% endblock %}
    ''')
    r.close()
    return None
    
    
def html_place_holders_table_for_subtypes():
    """
    Function to produce an html table armed with check boxes with the names of
    the special place holder subtypes we wish to make a subtype tree with. 
    Takes in nothing but uses the BLISTR database.
    It will then extract the names of the toxin placeholders from the db
    Returns the html table used in subtype_trees.html
    """
    engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
    Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
    session = Session()
    counter = 0
    columns = 11 # number of columns our subtype table will hold
    html = "<table align=\"center\"class=\"dataframe male\"><thead></thead><tbody><tr><th colspan=\""+str(columns)+"\" ><font size=\"6\">Placeholder Subtypes</font></th></tr><tr>"
    BoNT = session.query(PlaceHolderSubtypes).all()
    for tox in BoNT: #the name variable is set to the toxin type. This is for select all type E buttons, for example #add in checked=\"checked\" to have everything pre-checked
        html = html+"<td><font size=\"5\"><input type=checkbox name="+''.join([i for i in tox.name if not i.isdigit()])+" value="+tox.name+" > BoNT: "+tox.name+"</font></td>"#the wierd join thing just removes all numbers from the strings
        counter += 1
        if counter % columns == 0: #every third iteration we will go down a row
            html = html + "</tr><tr>"
    html = html + "</tr></tbody></table>"
    return html
    
def HTML_format_subtype_tree(out):
    """
    A single function which you call to create subtype_trees.html for use with the 
    BLISTR app. Used to avoid issues occurring when you have {{ }} in the table
    which you wish to render. This sould be run every time before subtype_trees.html
    is called to be rendered.
    out is a list of fully formmated html tables to be injected into the file
    """
    r = open('PATH/TO/ROOT/templates/subtype_trees.html','w')
    r.write('''{% extends "base.html" %}

    {% block content %}
    <form action="" method="POST" name="result">
    {{ form.hidden_tag() }}
    <div class=page>
    <h1>{{ title }}</h1>
    {{ form.tree }}<br>
    Select all subtypes of type ''')
    
    box_types = ["'A'", "'B'", "'C'", "'C/D'", "'D'", "'D/C'", "'E'", "'F'", "'G'"]
    counter289 = 0
    for box_type in box_types:
        counter289+= 1
        r.write('''
        <script language="JavaScript">
        function toggle'''+str(counter289)+'''(source) {
          checkboxes = document.getElementsByName('''+box_type+''');
          for(var i=0, n=checkboxes.length;i<n;i++) {
            checkboxes[i].checked = source.checked;
          }
        }
        </script>
        \''''+box_type+'''\': <input name="'''+box_type.rstrip("'").lstrip("'")+'''_all" type="checkbox" onClick="toggle'''+str(counter289)+'''(this)" /> <span style="margin-left:1em">''')
        
    r.write(out[0]) #this bits writes the blue table
    r.write('''      
    <font size="5"><b>Search For:</b></font> {{ form.search(size=30, maxlength=400) }}
    <input type=submit value="Search"><br>
    <script language="JavaScript">
        function toggle(source) {
          checkboxes = document.getElementsByName('check');
          for(var i=0, n=checkboxes.length;i<n;i++) {
            checkboxes[i].checked = source.checked;
          }
        }
        </script>
    Select All: <input type="checkbox" onClick="toggle(this)" />
    ''')
    r.write(out[1])
    r.write('''    
    </div>
    </form>    
    
    {% endblock %}
    ''')
    r.close()
    return None
        

def html_table(list_dictionary):
    """
    Pass in a list of dictionaries where each dictionary represents
    a row on a table. Then produce the corresponding html table to 
    match the inputs. The top bit of code will be the stuff needed to 
    save changes made to the table (i.e. edits). So it is just a bunch
    of jQuery for every line produced. This function will then produce
    an html file called tables.html for rendering.
    """
    output = '''{% extends "base.html" %}
    {% block content %}
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script type="text/javascript">
      var $SCRIPT_ROOT = {{ request.script_root|tojson|safe }};
    </script>
    <script type="text/javascript">
    '''
    row = 0
    
    
    changeable = ["Gname", "sub_type", "c_date", "s_type", "s_info", "inst", "author", "lat_lng", "country", "region"]
    output += '''
      $(function() {
        $("#submitBtn").click(function() {
        	 '''
    for das_dict in list_dictionary: #we need to do this for every row in the table we plan to output
        row += 1
        for change in changeable:
            output+= "var "+ change+str(row)+" = $('."+change+str(row)+"').html(); \n"
    row = 0 #resetting row for round 2
    output+='''
         $.ajax({
            type: "GET",
            url: $SCRIPT_ROOT + "/echo/",
            contentType: "application/json; charset=utf-8",
            data: { '''
    for das_dict in list_dictionary:
        row += 1
        for change in changeable:
            output+= change+str(row)+":"+ change+str(row) + ", "
    output = output.rstrip(", ") + '''},
                    success: function(data) {
                    $('#echoResult').text(data.value);
                }
            });     
        });
      });
    '''
    output +=  '</script><strong><div id="echoResult"></div></strong>'
    output += '''<h1>Welcome to tables!!!</h1><br>
    <table class="dataframe male">    
        <thead>
            <tr>
                <th>Genome name</th>
                <th>Toxin type</th>
                <th>SubType</th>
                <th>Collection date</th>
                <th>Source type</th>
                <th>Source information</th>
                <th>Institution</th>
                <th>Author</th>
                <th>Largest contig</th>
                <th># contigs</th>
                <th># contigs (>= 1000 bp)</th>
                <th>Total length (>= 0 bp)</th>
                <th>GC (%)</th>
                <th># N's per 100 kbp</th>
                <th>Total length (>= 1000 bp)</th>
                <th>Total length</th>
                <th># contigs (>= 0 bp)</th>
                <th>bp before toxin</th>
                <th>bp after toxin</th>
                <th>Addition Toxins</th>
                <th>Toxin sequences</th>            
                <th>Lat:Long</th>
                <th>Country</th>
                <th>Region</th>
            </tr>
        </thead>
        <tbody>
        
    '''
    counter = 0 #counter to keep download files unique
    for das_dict in list_dictionary:
        counter += 1
        output = output + '''
            <tr>
                <td><a href="temp/temp{counter}.fasta"><div class='Gname{counter}'>{Gname}</div></a></td>
                <td>{Gtype}</td>
                <td><div class='sub_type{counter}' contenteditable>{sub_type}</div></td>
                <td><div class='c_date{counter}' contenteditable>{Cdate}</div></td>
                <td><div class='s_type{counter}' contenteditable>{Stype}</div></td>
                <td><div class='s_info{counter}' contenteditable>{Sinfo}</div></td>
                <td><div class='inst{counter}' contenteditable>{inst}</div></td>
                <td><div class='author{counter}' contenteditable>{author}</div></td>
                <td>{l_contig}</td>
                <td>{n_contigs}</td>
                <td>{n_contigs1000}</td>
                <td>{tl0}</td>
                <td>{GC}</td>
                <td>{N100}</td>
                <td>{tl1000}</td>
                <td>{tl}</td>
                <td>{contigs0}</td>
                <td>{bp_before}</td>
                <td>{bp_after}</td>
                <td>{sub_tox}</td>
                <td>{toxin_downloads}</td> 
                <td><div class='lat_lng{counter}' contenteditable>{lat_lng}</td>
                <td><div class='country{counter}' contenteditable>{country}</div></td>
                <td><div class='region{counter}' contenteditable>{region}</div></td>
            </tr>
        '''.format(
        counter = str(counter),
        toxin_downloads = '<a href="temp/temptoxin{counter}.fasta">Toxin, </a><a href="temp/temptoxin++{counter}.fasta">Toxin++</a>'.format(counter = str(counter)) if das_dict.get('t_meta') != None else None, #fancy one line if statement. Removes these links if the toxin.best_hit information is None (i.e. not C/D or the like)
        Gname = das_dict.get('Gname'),
        Gtype = das_dict.get('t_meta'),
        sub_type = das_dict.get('sub_type'),
        group = das_dict.get('group'),
        Cdate = das_dict.get('Cdate'),
        Stype = das_dict.get('Stype'),
        Sinfo = das_dict.get('Sinfo'),
        inst = das_dict.get('inst'),
        author = das_dict.get('author'),
        l_contig = das_dict.get('l_contig'),
        n_contigs = das_dict.get('n_contigs'),
        n_contigs1000 = das_dict.get('n_contigs1000'),
        tl0 = das_dict.get('tl0'),
        GC = das_dict.get('GC'),
        N100 = das_dict.get('N100'),
        tl1000 = das_dict.get('tl1000'),
        tl = das_dict.get('tl'),
        contigs0 = das_dict.get('contigs0'),
        t_meta = das_dict.get('t_meta'),
        bp_before = das_dict.get('bp_before'),
        bp_after = das_dict.get('bp_after'),
        sub_tox = das_dict.get('sub_tox'),
        lat_lng = das_dict.get('lat_lng'),
        country = das_dict.get('country'),
        region = das_dict.get('region')
        )
    
    output = output + '''</tbody> \n </table> 
    {{ form.submitBtn }}<br><br>
    {% endblock %}'''
    out = open('PATH/TO/ROOT/templates/tables.html', 'w')
    out.write(output)
    out.close()
    return None #string to help the function echo to find out how many rows are being run (will use split on the Start... nonsense)
    
"""
<td><a href="{{ url_for('fasta') }}">{{ {Gname} }}</a> <a href="/temp.fasta"> (Download)</a></td>
<td><a href="{{ url_for('toxin') }}">Toxin</a> <a href="/temptoxin.fasta"> (Download)</a>, <a href="{{ url_for('toxin_extra') }}">Toxin++</a> <a href="/temptoxin++.fasta"> (Download)</a></td>
 hype1 = 'a href="{{ url_for(\'static\', filename=\'temp'+str(counter)+'.fasta\') }}"',
        hype2 = 'a href="{{ url_for(\'static\', filename=\'temptoxin'+str(counter)+'.fasta\') }}"',
        hype3 = 'a href="{{ url_for(\'static\', filename=\'temptoxin++'+str(counter)+'.fasta\') }}"',
"""

def html_genome_tree_table():
    """
    Function which outputs the html of a table which will hold a bunch of genome
    names and collection date. Check boxes will be in the front of each entry.
    I do not believe that this function will be used :(
    """
    engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db') 
    Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
    session = Session()
    counter = 0
    genomes = session.query(Genome).order_by(Genome.id.asc()).all() #list of all our genomes
    html = "<table align=\"center\"class=\"dataframe male\"><thead></thead><tbody><tr><th colspan=\"6\" ><font size=\"6\">Other Genomes</font></th></tr><tr>"
    for genome in genomes:
        html = html+"<td><font size=\"5\"><input type=checkbox name=check value="+str(genome.id)+"> "+str(genome.name)+",<span style=\"margin-left:1em\"> "+str(genome.collection_date)+"</font></td>"
        counter += 1
        if counter % 4 == 0: #every sixth iteration we will go down a row
            html = html + "</tr><tr>"
    html = html + "</tr></tbody></table>"
    return html