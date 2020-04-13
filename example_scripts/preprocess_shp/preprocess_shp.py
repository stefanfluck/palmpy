# -*- coding: utf-8 -*-
"""
preprocess shapefiles for make_static.py routine.
Stefan Fluck, 12.04.2020

"""
import geopandas as gpd
import numpy as no
import matplotlib.pyplot as plt


#%% general information
#cut downloaded shapefiles to an extent (a bit larger than domain extents, 
#   so domain positions can be varied slightly)
xmin = 530704.
xmax = 543086.
ymin = 172570.
ymax = 185989.


#%% process 
