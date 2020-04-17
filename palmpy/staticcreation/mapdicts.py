'''
MAPPING DICTIONARIES BETWEEN DIFFERENT CLASSIFICATIONS TO PALM CLASSES
- VEGETATION CLASSES
- WATER CLASSES
- SOIL CLASSES
- PAVEMENT CLASSES

by Stefan Fluck, 15.04.2020

'''

import palmpy.staticcreation.makestatictools as mst

#%% swissTLM3D BB 2 PALM
# swissTLM3D BB vegetation classes to PALM vegetation types
tlmbb2palmveg = {   
                    1:9,    # fels > desert
                    6:16,   # gebueschwald > deciduous shrubs
                    7:9,    # lockergestein > desert
                    9:13,   # Gletscher > ice caps and glaciers
                    11:14,  # Feuchtgebiet > bogs and marshes
                    12:17,  # Wald > mixed Forest/woodland
                    13:18,  # Wald offen > interrupted forest
                    
                    #own categories
                    1000 : 3,
                    1001 : 3,
                    1002 : 3,
                    1003 : 3,
                    1004 : 3,
                    1005 : 3,
                }


# swissTLM3D BB water classes to PALM water types
tlmbb2palmwat = {   5:2,    #fliessgewaesser > river
                    10:1,   #stehendes gewaesser > lake
                }


# swissTLM3D assembled pavement file (from streets, vkareal, eisenbahn)
tlmpav2palmpav = {  -9999.:mst.fillvalues['pavement_type'],
                    99: 9, #eisenbahntrassees meist 99 -> gravel
                     4: 3, #perrons meist 4 -> concrete
                  }


# swissTLM3D street !only! Objektart to PALM street type
tlmstr2palmstyp =   {     
                          #-9999 : mst.fillvalues['street_type'],
                           0    : 18,
                           1    : 18,
                           2    : 17,
                           3    : 7,
                           4    : 16,
                           5    : 9,
                           6    : 9,
                           8    : 13,
                           9    : 11, 
                           10   : 8, 
                           11   : 8, 
                           12   : 7,
                           13   : 7,
                           #14   : mst.fillvalues['street_type'],
                           15   : 4,
                           16   : 3,
                           17   : 3,
                           18   : 3,
                           19   : 3,
                           20   : 13,
                           21   : 15,
                           22   : 3,
                           #99   : mst.fillvalues['street_type'],
                     }

#classification into major and minor roads: which tlm classes are major (emission relevant)
tlmmajroads = [0,1,2,4,5,6,8,9,20,21]
tlmminroads = [3,10,11,12,13,15,16,17,18,19,22]

#%% PALM 2 PALM
# assign PALM soil type to PALM vegetation types
palmveg2palmsoil = {    mst.fillvalues['vegetation_type']:mst.fillvalues['soil_type'],
                        1:1,
                        2:6,
                        3:1,
                        9:1,
                        13:1,
                        14:1,
                        16:2,
                        17:1,
                        18:1,
                    }


# assign PALM soil type to PALM pavement types
palmpav2palmsoil = {    mst.fillvalues['pavement_type']:mst.fillvalues['soil_type'],
                        0:3,
                        1:3,
                        # 2:3,
                        # 3:3,
                        # 4:3,
                        # 5:3,
                        # 6:3,
                        # 7:3,
                        # 8:3,
                        # 9:3,
                        # 10:3,
                        # 11:3,
                        # 12:3,
                        # 13:3,
                        # 14:3,
                        # 15:3,
                    }


#%% USGS 
# usgs2palm = {0:7,
#              1:12}



# CORINE
# corine2palm = {0:1,
#                1:2}