#README

##Uploading fasta files to the database through the backend
If you have multiple fasta files, say over 5 you would like to add to the database all at once,
or say you want to clean out the database of all the stuff you added and go back to older more reliable
stuff then look no further than `db_loader.py`. For help with its usages (and there are many), enter `$ python db_loader.py -h`

If you want to upload new genomes through the backend, move your fasta files into the `~/BLISTR/fasta_files`
directory. Once there, ensure that their contig headers have the format of:
```
>Contig_number,Genome_name,Author,Collection_date,Clinical_or_Environmental,Source_info,Institution,Lat,Long,Country,Region
```
To help you with that, you could use the program `format_fasta.py` (found in the `BLISTR_support_programs` directory).
You also have to ensure that the `Genome_name` in the contig header matches the fasta file name (i.e. a genome name of
Iwate2008 goes with the file named Iwate2008.fasta). To help with that you can use the program `wrong_name_finder.py`
which (found in the `BLISTR_support_programs` directory) will inform you of any fasta files with this problem and if
you use the flag `--autofix` then the program will also resolve those problems for you. Something else to note is that
you must ensure that the contig header only has 10 commas, no more, no less. It is imperative that this rule be followed.
Another function you may wish to capitalise on (though this is not important), if your fasta files have a country and/or
regional entry but no latitude nor longitude entries, then you can run the program `where_in_the_world.py` (also found
in the `BLISTR_support_programs` directory). This program will edit all the contig headers to put in you country/region's
latitude and longitude information (which the program determines itself).

####Uploading only new entries
If you wish to upload new entries to the BLISTR database (while not remaking the thing from scratch) simply run 
`$ python db_loader.py -u` after having your fasta files meet the above requirements and re in the `~/BLISTR/fasta_files` directory.

####New database from scratch
If you wish to destroy and the recreate the BLISTR database with the fasta files in the directory `~/BLISTR/fasta_files` 
then simply run `$ python db_loader.py`

####Database Backup
To back up your current BLISTR database  run `$ python db_loader.py -s`

####Restore database from a previous backup
To restore your database from a past database backup, run `$ python db_loader.py -r` to restore to the most recent
database backup. Alternatively, you can use `$ python db_loader.py -l path/to/past_backup` to select which backup 
you would like to load BLISTR from.
