# -*- coding: utf-8 -*-
"""
Saeed Rahimi
V 1.0 Date 04/04/2023
This script prepares the monitoring sites data:
    Reads the rData sources
    Extracs the Water Quality Variables
    Merges adds these variables with their relevant sites
"""

import pyreadr
import json
import os
import pandas as pd
import geopandas as gpd

try:
    import cPickle as pickle
except ImportError:  # Python 3.x
    import pickle

## Set the current directory
c_dir = 'D:/Work/Imaginative AI/WaterQualityApp'
os.chdir(c_dir)

## Read the RData file
r_data_dir = './Data/CleanedRiverData_Nov21.rdata'
r_data = pyreadr.read_r(r_data_dir)
print(r_data.keys()) # let's check what objects we got

## Write the data into a python pikle and save it
out_f_dir = './Data/WQ_Data_Nov2021.p'
with open(out_f_dir, 'wb') as f:
    pickle.dump(r_data, f, protocol=pickle.HIGHEST_PROTOCOL)

in_f_dir = './Data/WQ_Data_Nov2021.p'
## Read the pikle data
with open(in_f_dir, 'rb') as f:
    dat_dic = pickle.load(f)
    
in_f_dir = './Data/REC_CZ_Modiffied_merged.shp'
gpd_cz = gpd.read_file(in_f_dir)
gpd_cz.keys()
    
# dat_dic['metadataWQ'][dat_dic['metadataWQ'].keys()[18]].unique()
# dat = dat_dic['metadataWQ'][['sID', 'nzsegment', 'lat', 'long']]
# dat.to_csv('./Temp/SitesPts.csv')

# dat_dic['metadataWQ'] = pd.merge(dat_dic['metadataWQ'], gpd_cz[['nzsegment', 'geometry']],
#                 how='inner', on='nzsegment')
# dat_dic['metadataWQ'].keys()
# out_f_dir = './Data/WQ_Data_Nov2021.p'
# with open(out_f_dir, 'wb') as f:
#     pickle.dump(dat_dic, f, protocol=pickle.HIGHEST_PROTOCOL)

data = pd.DataFrame()
site_id = dat_dic['metadataWQ']['nzsegment'].get(0)
site_dat = dat_dic['StackFrame'][dat_dic['StackFrame']['nzsegment']
                                   == site_id]
site_sampling_dates = pd.DataFrame()
for d in site_dat['myDate'].unique():
    site_sampling_dates['sampeling_date'] = d
