'''
MAPPING DICTIONARIES BETWEEN DIFFERENT CLASSIFICATIONS TO PALM CLASSES
- VEGETATION CLASSES
- WATER CLASSES
- SOIL CLASSES
- PAVEMENT CLASSES

by Stefan Fluck, 15.04.2020

'''

import palmpy.staticcreation.makestatictools as mst

#%% swissTLM3D BB vegetation classes to PALM vegetation types
tlmbb2palmveg = {   int(0):int(3),    # unclassified > short grass
                    int(1):int(9),    # fels > desert
                    int(6):int(16),   # gebueschwald > deciduous shrubs
                    int(7):int(9),    # lockergestein > desert
                    int(9):int(13),   # Gletscher > ice caps and glaciers
                    int(11):int(14),  # Feuchtgebiet > bogs and marshes
                    int(12):int(17),  # Wald > mixed Forest/woodland
                    int(13):int(18),  # Wald offen > interrupted forest
                    
                    #own categories
                    1000 : 3,
                    1001 : 3,
                    1002 : 3,
                    1003 : 3,
                    1004 : 3,
                    1005 : 3,
                }

#%% swissTLM3D BB water classes to PALM water types
tlmbb2palmwat = {   int(5):int(2),    #fliessgewaesser > river
                    int(10):int(1),   #stehendes gewaesser > lake
                }

#%% assign PALM soil type to PALM vegetation types
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

#%% assign PALM soil type to PALM pavement types
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

#%% swissTLM3D street !only! Objektart to PALM street type
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


#%% swissTLM3D paved surfaces Objektart to PALM street type
tlmpaved2palmpave =   {     
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




#%% USGS 
# usgs2palm = {0:7,
#              1:12}



# CORINE
# corine2palm = {0:1,
#                1:2}