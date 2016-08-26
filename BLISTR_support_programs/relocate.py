# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 07:16:13 2016

@author: Owen Neuber

After running the prokka script, I realized that I could use the image files in
the static/images/ directory in the BLISTR app. Thus this script is to copy and 
past those files into that directory
Was used once and never again
"""

import os
import glob
from shutil import copyfile

path_to = glob.glob("PATH/TO/ROOT/fasta_files/PROKKA/tox/*")

for path in path_to:
    base = os.path.basename(path)
    image = path+"/img"
    copyfile(image, 'PATH/TO/ROOT/static/images/'+base+'.bmp')