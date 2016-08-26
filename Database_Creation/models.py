# -*- coding: utf-8 -*-
"""
Created on Wed May 25 07:42:15 2016

@author: Owen Neuber

Making a database filled with genomes and contegs

Our database is called BLISTR.db
To create this database, in command line type:
$ createdb "BLISTR.db"
if this database already exsits, you can remove it via:
$ dropdb BLISTR.db

Running this file in command line afeter creating an empty "BLISTR.db" database will
fill set database will empty tables ready to, in turn, be filled via extractor.py

To communicate with the database via command line, remove the  tripple quotes surrounding:
'Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
session = Session()'
and then run this program in your console (i.e. if Spyder was your IDE, just press F5) 
then you can type SQLAlchemy commands in the console to communicate with the db.
General form of a generic query (if you are interested):
session.query(Genome).filter_by(name="my_name").first() #returning the first result in the db with the genome name "my_name"

A big thank you to Peter Kruczkiewicz who developed SISTR which this app is 
influenced by. This file in particular was developed with a great deal of influence
from him (and a fair bit of the code here is copied from his SISTR app). See SISTR at:
https://lfz.corefacility.ca/sistr-app/
or see Peter's code on bitbucket at:
https://bitbucket.org/peterk87/
"""

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey , DateTime, Boolean#, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import HSTORE, JSON
#from Crypto.Random import random
#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
#from sqlalchemy.engine.url import URL
from sqlalchemy.orm import relationship, backref, sessionmaker
#from passlib.apps import custom_app_context as pwd_context


Base  = declarative_base()

#engine = create_engine("sqlite:///biowolf:Star_Gate5@localhost/BLISTR.db") #creates our database! stores it to a .db file named
#basedir = os.path.abspath(os.path.dirname(__file__))
engine = create_engine('postgresql://wolf:Halflife3@localhost/BLISTR.db')          #/' + os.path.join(basedir, 'BLISTR.db')) #guarentees we find the database
### to ignore the password requirements, I made wolf into a superuser (through psql command line)
"""
Session = sessionmaker(bind=engine) #need to execute these lines to create a queriable session
session = Session()
"""
class Genome(Base):
    __tablename__ = 'genome'
    
    id = Column(Integer, primary_key=True) #primary key
    name = Column(String(50), index=True, nullable=False) #unique genome name
    collection_date = Column(String(15)) #timestamp of date collected
    clinical_or_environmental = Column(String(13)) #displays if the source is clinical or environmental
    source_info = Column(String(200)) #user inputted information about the genome (in 200 characters or less)
    institution = Column(String(7)) #acronym of the insitution (i.e. SRA or HC) where the strain is from
    author = Column(String(50))
    is_analyzed = Column(Boolean, default=False, nullable=False) #set to False if the entry has not been added to metadata table. True otherwise
    #: HSTORE: QUAST_ determined assembly quality statistics
    quality_stats = Column(HSTORE)
    sub_type = Column(String) #i.e. A1. To be entered by the user
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    #: sqlalchemy.orm.relationship: User_ model object owner of Genome
    user = relationship('User', backref=backref('genomes', lazy='dynamic', cascade='all,delete'))
    
    def __repr__(self):
        return '<Genome(id: {id}, name: {name}, author: {author}, collection date: {collection_date}, {clinical_or_environmental}, number of contigs: {n_contigs}, source information: {source_info}, institution: {institution})>'.format(
            id=self.id,
            name=self.name,
            collection_date=self.collection_date,
            clinical_or_environmental=self.clinical_or_environmental,
            n_contigs=self.contigs.count(),
            source_info=self.source_info,
            institution=self.institution,
            author = self.author)
            
        
class Contig(Base): 
    __tablename__ = 'contig'
    #: Integer: primary_key of Contig_
    id = Column(Integer, primary_key=True)
    
    contig_number = Column(Integer, nullable=False) #intger (contig number appearing in genome)
    #: String: Nucleotide sequence
    seq = Column(String, nullable=False)
    #: Integer: ID of Genome_ that the Contig belongs to
    genome_id = Column(Integer, ForeignKey('genome.id'))#, nullable=False)
    #: sqlalchemy.orm.relationship: Genome_ model object that Contig belongs to
    genome = relationship('Genome', backref=backref('contigs', lazy='dynamic', cascade='all,delete'))

    def __repr__(self): #returns the name of the contig, it's length, and its genome of origin
        return '<Contig(contig number: {0}, {1}, {2})>'.format(self.contig_number, len(self.seq), self.genome.name)


class GeographicLocation(Base): #makes an independent table which holds information about the genome's geographic location; no change
    """
    The geographic location where the Genome was isolated.
    """
    __tablename__ = 'geographic_location'

    id = Column(Integer, primary_key=True)
    #: Numeric: GPS Latitude
    lat = Column(String(12))
    #: Numeric: GPS Longitude
    lng = Column(String(12))
    #: String(100): Country where genome was isolated
    country = Column(String(50))
    #: String(100): Region within country where genome was isolated
    region = Column(String(50))
    #: Integer: ID of Genome_ that the Contig belongs to
    genome_id = Column(Integer, ForeignKey('genome.id'))#, nullable=False)
    #: sqlalchemy.orm.relationship: Genome_ model object that Contig belongs to
    genome = relationship('Genome', backref=backref('geolo', lazy='dynamic', cascade='all,delete'))
    
    """ #The following is some wierd thing from Peter's code. It gave me a bounty of errors. So now it is commented out!
    __table_args__ = (UniqueConstraint('lat',
                                       'lng',
                                       'country',
                                       'region',
                                       name='geographic_location_uc'),)
    """

    def __repr__(self):
        return '<GeographicLocation({id}, country: {country}, region: {region}, lat/lng: [{lat},{lng}], from: {genome})>'.format(
            id=self.id,
            country=self.country,
            region=self.region,
            lat=self.lat,
            lng=self.lng,
            genome=self.genome.name
        )

class Toxin(Base): #table with information about the toxin gene
    __tablename__ = 'toxin'
    #: Integer: primary_key of toxin_gene
    id = Column(Integer, primary_key=True)
        
    best_hit = Column(String, index=True) #the best_hit of toxin (this is where the toxin type is stored)
    bp_before = Column(Integer)
    bp_after = Column(Integer)
    
    orfx_ha = Column(String(20)) #the orfx/ha data
    
    toxin_type = Column(String(15)) #i.e. GroupIII.A(B). currently unused
    
    #: String: Nucleotide sequence
    seq = Column(String, nullable=False)
    
    contig_num = Column(Integer)
    
    #: Integer: ID of Genome that the Toxin belongs to
    genome_id = Column(Integer, ForeignKey('genome.id'))
    genome = relationship('Genome', backref=backref('toxin', lazy='dynamic', cascade='all,delete'))
    #: Integer: ID of the Contig that the Toxin belongs to
    contig_id = Column(Integer, ForeignKey('contig.id'))
    contig = relationship('Contig', backref=backref('toxin', lazy='dynamic', cascade='all,delete'))
    
    def __repr__(self): #returns the best_hit of toxin, it's number of base pairs, its genome of origin, and its contig of origin
        return '<Toxin(toxin data: {0}, {1}, length of sequence: {2}, genome name: {3}, contig number: {4})>'.format(self.best_hit, self.orfx_ha, len(self.seq), self.genome.name, self.contig.contig_number)
        
class FlaA(Base): #table with information about the flagellum A gene
    __tablename__ = 'flaa'
    #: Integer: primary_key of toxin_gene
    id = Column(Integer, primary_key=True)
    
    best_hit = Column(String, index=True) #the best_hit of toxin (capital T as not to confuse with python operator best_hit)
    bp_before = Column(Integer)
    bp_after = Column(Integer)
    
    serotype = Column(String(15)) #i.e. GroupIII.A(B)
    #: String: Nucleotide sequence
    seq = Column(String, nullable=False)
    #: Integer: ID of Genome that the Toxin belongs to
    genome_id = Column(Integer, ForeignKey('genome.id'))
    genome = relationship('Genome', backref=backref('flaa', lazy='dynamic', cascade='all,delete'))
    #: Integer: ID of the Contig that the Toxin belongs to
    contig_num = Column(Integer, ForeignKey('contig.id'))
    contig = relationship('Contig', backref=backref('flaa', lazy='dynamic', cascade='all,delete'))
    
    def __repr__(self): #returns the best_hit of toxin, it's number of base pairs, its genome of origin, and its contig of origin
        return '<FlaA(flagellum A data: {0}, length of sequence: {1}, genome name: {2}, contig number: {3})>'.format(self.best_hit, len(self.seq), self.genome.name, self.contig.contig_number)   
        
class FlaB(Base): #table with information about the flagellum A gene
    __tablename__ = 'flab'
    #: Integer: primary_key of toxin_gene
    id = Column(Integer, primary_key=True)
    
    best_hit = Column(String, index=True) #the best_hit of toxin (capital T as not to confuse with python operator best_hit)
    bp_before = Column(Integer)
    bp_after = Column(Integer)
    
    serotype = Column(String(15)) #i.e. GroupIII.A(B)
    #: String: Nucleotide sequence
    seq = Column(String, nullable=False)
    #: Integer: ID of Genome that the Toxin belongs to
    genome_id = Column(Integer, ForeignKey('genome.id'))
    genome = relationship('Genome', backref=backref('flab', lazy='dynamic', cascade='all,delete'))
    #: Integer: ID of the Contig that the Toxin belongs to
    contig_num = Column(Integer, ForeignKey('contig.id'))
    contig = relationship('Contig', backref=backref('flab', lazy='dynamic', cascade='all,delete'))
    
    def __repr__(self): #returns the best_hit of toxin, it's number of base pairs, its genome of origin, and its contig of origin
        return '<FlaB(flagellum B data: {0}, length of sequence: {1}, genome name: {2}, contig number: {3})>'.format(self.best_hit, len(self.seq), self.genome.name, self.contig.contig_number)
 
class User(Base): #User table and associated functions; no change
    __tablename__ = 'user'
    #: Integer: primary_key of User
    id = Column(Integer, primary_key=True)
    #: String(64): Unique user name
    name = Column(String, index=True, nullable=False, default="sistr")
    #: UserRole_: User's role (e.g. admin, temporary, registered (unimplemented))
    role = Column(String, nullable=False, default='<admin>')
    #: String: Unique email address if not null
    #email = Column(String, nullable=True)
    #: DateTime: Date and time when the user was last seen or when the user last accessed their data.
    last_seen = Column(DateTime)
    #: String(128): Cryptographically hashed User_ password
    password_hash = Column(String(128))
      

class Searches(Base): #additional tables used for storing search quries. Implemented to work with views.py. views.py
    __tablename__ = 'searches'
    __searchable__ = ['search']
    id = Column(Integer, primary_key=True)
    
    g_ids = Column(String, nullable=False) #the genome id of the searched for genome will be stored here
    searched_for = Column(Boolean, default=False) #if this is false, Tables will show the result of the search, otherwise it will act normally
    
    def __repr__(self):
        return '<Searches({0}, {1})>'.format(self.g_ids, self.searched_for)

class S_16(Base):
    __tablename__ = '16S'
    id = Column(Integer, primary_key=True)
    
    best_hit = Column(String) #the best_hit of toxin (capital T as not to confuse with python operator best_hit)
    error = Column(String, default=None) #If there is a non cbot, put the concern here
    seq = Column(String)
    
    genome_id = Column(Integer, ForeignKey('genome.id'))
    genome = relationship('Genome', backref=backref('s_16', lazy='dynamic', cascade='all,delete'))
    def __repr__(self): #returns the best_hit of toxin, it's number of base pairs, its genome of origin, and its contig of origin
        return '<S_16(best_hit: {0}, error: {1}, genome: {2})>'.format(self.best_hit, self.error, self.genome.name)
        
class Prokka(Base):
    __tablename__ = 'prokka'
    id = Column(Integer, primary_key=True)
    
    fasta_faa = Column(String) #the .faa file of the fasta
    fasta_coding_genes = Column(Integer)
    fasta_ffn = Column(String)
    fasta_ORFs = Column(Integer)
    
    tox_exists = Column(Boolean) #True if there was a toxin++ file to begin with, false if not (implying the below 2 columns will be empty)
    tox_faa = Column(String) #the .faa file of the toxin
    tox_coding_genes = Column(Integer)
    tox_ffn = Column(String)
    tox_ORFs = Column(Integer)
    #There is no need for concern about the immage files as they are safely in the static image folder in the BLISTR app
    
    genome_id = Column(Integer, ForeignKey('genome.id'))
    genome = relationship('Genome', backref=backref('prokka', lazy='dynamic', cascade='all,delete'))
    def __repr__(self): #returns the best_hit of toxin, it's number of base pairs, its genome of origin, and its contig of origin
        return '<Prokka(toxin data present: {0}, genome: {1})>'.format(self.tox_exists, self.genome.name)
        
class PlaceHolderToxins(Base):
    __tablename__ = 'place_holder_toxins'
    id = Column(Integer, primary_key=True)
    name = Column(String(15)) #i.e. A1
    data = Column(String) #gi number and such
    seq = Column(String)
    
    def __repr__(self):
        return '<PlaceHolderToxins(name: {0}, metadata: {1})>'.format(self.name, self.data)
        
class PlaceHolderSubtypes(Base):
    __tablename__ = 'place_holder_subtypes'
    id = Column(Integer, primary_key=True)
    name = Column(String(15)) #i.e. A sub:A2    
    data = Column(String) #gi number and such
    seq = Column(String)
    
    def __repr__(self):
        return '<PlaceHolderSubtypes(name: {0}, metadata: {1})>'.format(self.name, self.data)
 
Base.metadata.create_all(engine) #you need to execute this everytime you make a new table