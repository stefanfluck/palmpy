'''
MAPPING DICTIONARIES BETWEEN DIFFERENT CLASSIFICATIONS TO PALM CLASSES
- VEGETATION CLASSES
- WATER CLASSES
- SOIL CLASSES
- PAVEMENT CLASSES

for LULC dataset unige, see https://doi.org/10.3390/land11050615

'''

import palmpy.staticcreation.makestatictools as mst

#%% Land Use 2 PALM types
#  land use vegetation classes to PALM vegetation types
bb2palmveg = { 0:mst.fillvalues['vegetation_type'],   
                27:3,
                31:3,
                32:3,
                33:3,
                34:3,
                35:3,
                36:6,
                37:6,
                38:8,
                39:11,
                40:2,
                41:8,
                42:2,
                43:11,
                44:8,
                45:8,
                46:10,
                47:12,
                48:3,
                49:17,
                50:17,
                51:18,
                52:18,
                53:18,
                54:18,
                55:18,
                56:16,
                57:15,
                58:17,
                59:17,
                60:15,
                64:10,
                65:15,
                66:14,
                67:3,
                68:9,
                70:9,
                71:3,
                72:13,
                   }



# land use water classes to PALM water types
bb2palmwat =    {   0:mst.fillvalues['water_type'],
                    61:1,
                    62:2,
                }


# pavement land uses to PALM pavement types
pav2palmpav = {-9999.:mst.fillvalues['pavement_type'],
                    1:1,
                    2:1,
                    3:1,
                    4:1,
                    5:1,
                    6:1,
                    7:1,
                    8:1,
                    9:1,
                    10:1,
                    11:1,
                    12:1,
                    13:1,
                    14:1,
                    15:2,
                    16:2,
                    17:2,
                    18:2,
                    19:1,
                    20:11,
                    21:10,
                    22:3,
                    23:3,
                    24:3,
                    25:3,
                    26:3,
                    28:9,
                    29:1,
                    30:2,
                    63:2,
                    69:9
                    }



#  street !only! Objektart to PALM street type (not implemented for this!)
str2palmstyp =   {   0:0,
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
                        4:2,
                        5:2,
                        6:2,
                        7:2,
                        8:2,
                        9:1,
                        10:3,
                        11:1,
                        12:3,
                        13:1,
                        14:1,
                        15:2,
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


