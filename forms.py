# -*- coding: utf-8 -*-
"""
Created on Tue May 10 09:22:09 2016

@author: Owen Neuber

Forms to support views.py and its templates. Here all the html forms have their 
functions and validators defined. Each of these forms can be seen in my html 
documents in the form of {{ form.the_form_name}}.
"""

from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, FileField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length#, NumberRange

    
class QueryForm(Form):
    query = FileField('query') #FileField(label=None, validators=None, filters=(), description=u'', id=None, default=None, widget=None, _form=None, _name=None, _prefix=u'', _translations=None)
    search = StringField('search')
    export_TSV = BooleanField('export_TSV', default=False)
    prokka_wait = BooleanField('prokka_wait', default=False)
    prokka_skip = BooleanField('prokka_skip', default=False)
    
    name = StringField('search', validators=[Length(min=0, max=50)]) #I am putting these limites on the entry lengths as anything larger will have models.py throwing errors (becuase that is how I set it up. For optimization reasons.) This will stop the user from doing something stupid
    collection_date = StringField('collection_date', validators=[Length(min=0, max=15)])
    clinical_or_environmental = SelectField('source', choices=[('None', 'None'), ('Clinical', 'Clinical'), ('Env./Food', 'Env./Food')])
    source_info = TextAreaField('source_info', validators=[Length(min=0, max=200)])
    institution = StringField('institution', validators=[Length(min=0, max=7)])
    author = StringField('author', validators=[Length(min=0, max=50)])
    lat = StringField('author', validators=[Length(min=0, max=12)])
    lng = StringField('author', validators=[Length(min=0, max=12)])
    country = StringField('author', validators=[Length(min=0, max=50)])
    region = StringField('author', validators=[Length(min=0, max=50)])
    pident = StringField('pident', default=90, validators=[Length(min=0, max=3)]) #the user can't get away with setting this one to None
    len_slen = StringField('len_slen', default=0.9, validators=[Length(min=0, max=5)])
    
    sub_type = StringField('sub_type')
        
class TableForm(Form):
    toxin = BooleanField('toxin', default=False)
    toxin_extra = BooleanField('toxin_extra', default=False)
    contig = BooleanField('contig', default=False)
    toxin_faa = BooleanField('toxin_faa', default=False)
    toxin_ffn = BooleanField('toxin_ffn', default=False)
    fasta_faa = BooleanField('fasta_faa', default=False)
    fasta_ffn = BooleanField('fasta_ffn', default=False)
    sixteenS = BooleanField('sixteenS', default=False)
    delete = SubmitField('Delete Entries')
    tree_16S = SubmitField('Create 16S Tree') #submit field makes it like a boolean submit button
    tree = SubmitField('Make Tree')
    export = SubmitField('Download table as .xlsx')
    search = StringField('search')
    
class MapForm(Form):
    toxin_type = SelectField('toxin_type', choices=[('None', 'None'), ('A', 'A'), ('B', 'B'), ('C', 'C'), ('C/D', 'C/D'), ('D', 'D'), ('D/C', 'D/C'), ('E', 'E'), ('F', 'F'), ('G', 'G')])
    
    
class EditForm(Form):
    submitBtn = SubmitField('Save Changes')

#class TSV(Form):
#    export_TSV = BooleanField('export_TSV', default=False)
    
    #remember_me = BooleanField('remeber_me', default=False) #to set up tracking cookies on the browser
    #about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])