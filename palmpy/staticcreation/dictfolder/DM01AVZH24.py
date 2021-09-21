'''
MAPPING DICTIONARIES BETWEEN DIFFERENT CLASSIFICATIONS TO PALM CLASSES
- VEGETATION CLASSES
- WATER CLASSES
- SOIL CLASSES
- PAVEMENT CLASSES

by Stefan Fluck, 24.06.2020
Usable with Stadt Zürichs Geodaten (Amtl. Vermessungsdaten)

'''

import palmpy.staticcreation.makestatictools as mst

#%% BB 2 PALM
#  BB vegetation classes to PALM vegetation types
bb2palmveg = {   21:3,
                 22:2,
                 23:2,
                 24:3,
                 25:3,
                 26:3,
                 27:3,
                 28:14,
                 29:3,
                 31:3,
                 35:17,
                 38:16,
               1001:3,
               1002:2,
               1003:1,
               1004:8,
               1005:3,
               1006:2,
               1007:2,
               2000:3,
               2001:10,
                   }


# BB water classes to PALM water types
bb2palmwat =    {   33:2,    #fliessgewaesser > river
                    32:1,   #stehendes gewaesser > lake
                }


# pavement file 8,9,10,11,12,13,14,15,17,18,19,20
pav2palmpav = {  -9999.:mst.fillvalues['pavement_type'],
                    8:  1, 
                    9:  2,
                    10: 1,
                    11: 4,
                    12: 2,
                    13: 2,
                    14: 9,
                    15: 3,
                    17: 1,
                    18: 2,
                    19: 13,
                    20: 1,
                    2001:1,
                    2002:1,
                    2003:1,
                    
                  }


#  street !only! Objektart to PALM street type
str2palmstyp =   {     
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
#(if minor and major roads overlap, the major road type is on top).
#majroads = [0,1,2,4,5,6,8,9,20,21]
#minroads = [3,10,11,12,13,15,16,17,18,19,22]

#%% PALM 2 PALM
# assign PALM soil type to PALM vegetation types
palmveg2palmsoil = {    mst.fillvalues['vegetation_type']:mst.fillvalues['soil_type'],
                        1:1,
                        2:6,
                        3:1,
                        8:2,
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
                        2:3,
                        3:3,
                        4:3,
                        5:3,
                        6:3,
                        7:3,
                        8:3,
                        9:3,
                        10:3,
                        11:3,
                        12:3,
                        13:3,
                        14:3,
                        15:3,
                    }


