#README

###BotuLinum In Silico Typing Resource (BLISTR)
BLISTR is a browser app designed to assist with in silico analysis of 
Clostridium Botulinum (Cbot) specimens. The app comes with a set up, 
curated, database of around 300 Cbot specimens. You may edit the 
database as you like in a user friendly fashion. When you upload a
Cbot fasta file to the app, it will be added to the database and you
may curate it as you please. During upload, [PROKKA](http://bioinformatics.oxfordjournals.org/content/early/2014/03/18/bioinformatics.btu153),
[BLAST](http://nar.oxfordjournals.org/content/25/17/3389.short), [QUAST](http://bioinformatics.oxfordjournals.org/content/29/8/1072), 
[Easyfig](http://www.ncbi.nlm.nih.gov/pubmed/21278367), and [revcomp](http://manpages.ubuntu.com/manpages/wily/man1/revcomp.1.html)
are run on the fasta file. The identity of any Cbot neurotoxins 
in the provided sample would be make known to the user. On other pages, 
you can create trees with the click of a button after selecting which 
genomes you would like to compare (the tree handling software used is
[dendroscope](http://dendroscope.org/). The trees are generated by a combination
of [muscle](http://www.ncbi.nlm.nih.gov/pubmed/15034147), Fasta2Phylip.pl, and [raxml](http://bioinformatics.oxfordjournals.org/content/30/9/1312.short)).
Other features include map generation (which places markers on a world map based off the geographic
location of the genomes) and 16S identification.

###Installation
Before installing this app, please run the following in your terminal:
- `$ ARRAY=(prokka blastn blastp python2.7 psql git apt-get, pip)`
- `$ for i in "${ARRAY[@]}";do;hash $i 2>/dev/null || { echo >&2 "$i" ;};done;`

Whatever names your terminal spits out are programs you will have to install
prior to installing BLISTR. If there are no outputs you can move on to the
installation of BLISTR.

If you received any output from the above, please follow the installation 
instructions for which ever programs you are missing:
- [prokka](http://2013-cse801.readthedocs.io/en/latest/week3/prokka-annotation.html)
- [blastn](http://www.ncbi.nlm.nih.gov/books/NBK52640/)
- [blastp](http://www.ncbi.nlm.nih.gov/books/NBK52640/)
- [python2.7](https://www.python.org/download/releases/2.7/) (available on the Ubuntu Software Centre)
- [psql](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-16-04) (available on the Ubuntu Software Centre as: postgresql)
- [git](http://www.liquidweb.com/kb/how-to-install-git-on-ubuntu-14-04/) (available on the Ubuntu Software Centre)
- apt-get (available on the Ubuntu Software Centre as: apt)
- pip (use the command: `$ sudo apt-get install python-pip`)

#####Setting up PostgreSQL to work with BLISTR
Try the command: `$ psql` ; if you get this error message:
```
psql: could not connect to server: No such file or directory
	Is the server running locally and accepting
	connections on Unix domain socket "/var/run/postgresql/.s.PGSQL.5432"?
```
Then run `$ psql --version` and you should get an output like: `psql (PostgreSQL) 9.5.3`.
It is the first two numbers that matter, in this case _9.5_. Then, with your two numbers, run `$ sudo apt-get remove --purge postgresql-9.5` followed 
by `$ sudo apt-get install postgresql-9.5` (with your two numbers replacing 9.5)

Next you need the HSTORE extension set up, to do that type `$ sudo apt-get install postgresql-contrib-9.5` where `9.5` is your
postgresql version (the first two numbers returned by `$ psql --version`)

Now try: `$ sudo pip install psycopg2` ; if you get the error message:
```
Error: You need to install postgresql-server-dev-X.Y for building a server-side extension or libpq-dev for building a client-side application.
```
Then fire off the command: `$ sudo apt-get install python-psycopg2` followed by: `$ sudo apt-get install libpq-dev`

Do the following bit using your computer's username in place of _username_. To know what your username is, type 
`$ whoami` into your terminal. The output is your username. Now, in your terminal, type the following commands 
(using your username in place of _username_):
```
$ createuser -U postgres -W -s username
Password: Halflife3    (if you get an error here, read the next paragraph for a remedy)
$ createdb BLISTR.db
$ sudo -u username psql BLISTR.db
BLISTR.db=# ALTER USER "username" WITH PASSWORD 'Halflife3';
```
Hit Ctrl+d to exit the BLISTR.db database. If you had an error with the first line, 
such as: `createuser: could not connect to database postgres: FATAL: Peer authentication failed for user "postgres"`
Then you likely need to change your authentication method temporarily. To do that, run the following: 
- `sudo find / -type f -name pg_hba.conf` and use the output of that in the following:
- `sudo sed -i 's/peer/trust/g' output` (replacing `output` with the result of the find call)
- `sudo service postgresql restart`
- `createuser -U postgres -W -s username` (using your username from above)
- `Password: Halflife3`
- `sudo sed -i 's/trust/peer/g' output` (replacing `output` with the result of the find call)
- `sudo service postgresql restart`
After all that, you can continue with the previous list of commands (starting at `$ createdb BLISTR.db`).

####Installing BLISTR
Once all the above installations are done, you can either git clone the
BLISTR-main directory or you can use installer.py to do everything.
Select one of the two following options:

One thing to note, when you use `sudo pip install -r ../requirements.txt` you will likely receive several
warning messages. This is normal. Unless you see red text you have nothing to be concerned with. If you do 
see red text, try to install that python library yourself (and then remove it from requirements.txt (which 
you can open with `$ gedit ../requirements.txt`) and then try the `sudo pip install -r ../requirements.txt`
command again)

#####Option 1: Using Only installer.py
You will need to pip install all the requirements in requirements.txt.
To do that, open a terminal where you would like BLISTR to be installed in and type:
- `$ curl -o ../requirements.txt https://raw.githubusercontent.com/hc-BLISTR/BLISTR-main/master/requirements.txt`
- `$ sudo pip install -r ../requirements.txt` (when prompted enter your administrative password)

Now to get installer.py, type:
- `$ curl -o ../installer.py https://raw.githubusercontent.com/hc-BLISTR/BLISTR-main/master/BLISTR_support_programs/installer.py`

Then to start the install, type:
- `$ python ../installer.py -u paths/to/upload_folders -g -ff`

Where 'path/to/uploads_folders' are the paths to the directories or directory
from which you plan to upload fasta files to BLISTR (this is optional, exclude
"-u paths/to/upload_folders" if you are happy uploading fasta files from
the "fasta_files" directory in BLISTR's code).

#####Option 2: Git Cloning
cd into the empty directory where you would like to install BLISTR
- Git clone this repository: `$ git clone https://github.com/hc-BLISTR/BLISTR-main.git .` (don't forget the period)
- Pip install requirements: `$ sudo pip install -r requirements.txt` (when prompted enter your administrative password)
- Move installer.py back two directories: `$ mv BLISTR_support_programs/installer.py ../`
- Use the installer: `$ python ../installer.py -u paths/to/upload_folders -ff`
Where 'path/to/uploads_folders' are the paths to the directories or directory
from which you plan to upload fasta files to BLISTR (this is optional, exclude
"-u paths/to/upload_folders" if you are happy uploading fasta files from
the "fasta_files" directory in BLISTR's code).

###Running BLISTR
Now that BLISTR is installed to run it, cd into the root directory of 
BLISTR (likely the one named "BLISTR") and type in your terminal:
`$ python views.py` (or `$ python path/to/views.py` from any working directory)
In your terminal you should see:
```
 \* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
Then, in your browser (Chromium recommended), type the URL:
`http://127.0.0.1:5000/`

__NOTE:__ you will need to have views.py running in the background whenever you are
using BLISTR. If your browser says: "localhost refused to connect.", first try
refreshing the page, if that does not work, check to see if views.py is running.
After that BLISTR should be up and running. You should be able to upload fasta
files from which ever directories you set as valid (the ones following the "-u" flag)

####Errors
If BLISTR is not running (or only some of the pages on the app are running) then you likely
have some out of date python extensions. To determine if this is the case, run the program
`$ python in_sync.py` (in the `BLISTR_support_programs` directory). If you get multiple outputs that are out of sync, then you can either
pip update them yourself or run `$ python in_sync.py -a` to automatically handle the updates for you.

If you are having issues running any of BLISTR's sub programs (such as prokka) 
and yet you have installed them, I would recommend reading this forum:
http://unix.stackexchange.com/questions/3809/how-can-i-make-a-program-executable-from-everywhere

###Backend Database Manipulations
If you are a tech savvy go-getter who would like to preform database manipulations through the 
backend (perhaps to debug some of your personal add-ons or just to try some SQLAlchemy out) 
then this is how you can get started...

First, in your preferred python editor with a built in python console (such as Spyder), open 
models.py and remove the triple quotes surrounding:
```
"""
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
session = Session()
"""
```
After you've finished that, run modles.py locally so that its variables and such will appear in
your python console (i.e. in Spyder, smash `F5`). Then in your console you are free to play with 
the database at your leisure. Some examples:

Get a list of all the genomes in the database (plus some metadata):
```
>>> session.query(Genome).all()
```
Set the information on the Genome named "E-RUSS" to the variable "g":
```
>>> g = session.query(Genome).filter_by(name="E-RUSS").first()
```
Extract the author name from the Genome named "E-RUSS":
```
>>> g.author
```
View the toxin data of the Genome named "E-RUSS":
```
>>> session.query(Toxin).filter_by(genome_id=g.id).first()
```
View what country the Genome named "E-RUSS was from":
```
>>> session.query(GeographicLocation).filter_by(genome_id=g.id).first().country
```
Change the subtype of the toxin "E-RUSS":
```
>>> t = session.query(Toxin).filter_by(genome_id=g.id).first()
>>> t.sub_type = "E3"
>>> session.add(t)
>>> sessoin.commit()
```
To see how new entries are added to the database, I would recommend looking at the code in
the file `/Database_Inputs/uploader.py`

###Why This Was Made
BLISTR was made for Health Canada (Bureau of Microbial Hazards/Food Directorate) as a way to help 
employees with biological knowledge of Clostridium Botulinum but without a great deal of computing
knowledge. Hence the user friendly interface and, I hope, easy enough installation. Unfortunately,
due to the great glories of bureaucracy, this app is only available on your computer's localhost
and not on an independent website. Perhaps one day this app will achieve the unthinkable and get its
own website, but I see this as unlikely. 

###Contributors
Almost the entirety of this app was developed by Owen Neuber (owenneuber@outlook.com). He is a University
of Waterloo nanotechnology engineering student who worked at Health Canada for a work term. If you would
like to hire him for a work term, please feel free to contact him via email.
BLISTR was completed under the supervision and support of Nicholas Petronella (Nicholas.Petronella@hc-sc.gc.ca).
Other supervisors were Jennifer Ronholm (jen.ronholm@gmail.com) and John Austin (John.Austin@hc-sc.gc.ca).
Biological expertise to aid in the refinement of BLISTR was provided by Kelly Weedmark (Kelly.Weedmark@hc-sc.gc.ca).
A fair bit of support (and some code) was from Peter Kruczkiewicz (peter.kruczkiewicz@gmail.com) 
who created the [Salmonella In Silico Typing Resource (SISTR)](https://lfz.corefacility.ca/sistr-app/),
 a similar app. See Peter's code at his [bitbucket repository](https://bitbucket.org/peterk87/).

###Other People's Code
- The tables are sortable by [sorttable.js](http://www.kryogenix.org/code/browser/sorttable/)
- My maps page was made off the backbone of Saul Burgos' [easyLocator](https://github.com/SaulBurgos/easyLocator) (which itself uses [markerclusterer.js](https://github.com/googlemaps/js-marker-clusterer))
- Also some basic table style css and instructions on converting .xlsx files to html from [sarahleejane.github.io](https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html)
- Almost all of my Flask related code was influenced by Miguel Grinberg and his [Flask Mega-Tutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
