"""
Created on Thu Jan 30 10:13:51 2020
STATIC CREATION FILE TURNED INTO FUNCTIONS


TODO: ADD CHECKS THAT ORIGINS OF DOMAIN AND CHILD DOMAIN ARE COMPATIBLE (NESTING
NAMELIST LLX LLY COORDINATES TEILBAR DURCH PAREND DXY)

"""
import numpy as np



fillvalues = {
   "lat": float(-9999.0),
   "lon": float(-9999.0),
   "E_UTM": float(-9999.0),
   "N_UTM": float(-9999.0),   
   "zt": float(-9999.0),
   "buildings_2d": float(-9999.0),
   "buildings_3d": np.byte(-127),
   "bridges_2d": float(-9999.0),
   "building_id": int(-9999),
   "bridges_id": int(-9999),
   "building_type": np.byte(-127),
   "nsurface_fraction": int(-9999),
   "vegetation_type": np.byte(-127),
   "vegetation_height": float(-9999.0),
   "pavement_type": np.byte(-127),
   "water_type": np.byte(-127),
   "street_type": np.byte(-127), 
   "street_crossings": np.byte(-127),   
   "soil_type": np.byte(-127),
   "surface_fraction": float(-9999.0),
   "building_pars": float(-9999.0),
   "vegetation_pars": float(-9999.0),
   "water_pars": float(-9999.0),
   "pavement_pars": float(-9999.0),
   "buildings_pars": float(-9999.0),
   "soil_pars": float(-9999.0),
   "albedo_pars": float(-9999.0),
   "tree_data": float(-9999.0),
   "tree_type": np.byte(-127)
   }


def loadascgeodata(filename):
    '''
    either use geodatatools which return an array anyway or use this to import from .asc files.
    loads a <filename>.asc geodata file and returns the data as a numpy array, the x and y coordinates
    of the origin (lower left corner of the area) and its resolution (pixel size). 
    Returns tuple (array, xll, yll, res). 
    
    Example usage: topo,xorig,yorig,_ = loadascgeodata('test.asc')
    -> Imports the data from test.asc and drops the altitude info in topo, its origin to xorig and yorig
    and omits the output of the resolution (by specifying "_"),
    
    Parameters
    ----------
    filename : string
        file name or path to file respectively.

    Returns
    -------
    arr : np.array
        raster information as numpy array.
    xll : float
        x coordinate of the lower left corner of the data in the file.
    yll : float
        y coordinate of the lower left corner of the data in the file.
    res : float
        pixel width of the data contained in the file.
        
    '''
    import numpy as np
    arr = np.loadtxt(filename, skiprows=6) #a ascii geodata file has 6 header rows with metadata
    xll = np.loadtxt(filename, max_rows=6, usecols=(1))[2] #x coord of lower left point
    yll = np.loadtxt(filename, max_rows=6, usecols=(1))[3] #x coord of lower left point
    res = np.loadtxt(filename, max_rows=6, usecols=(1))[4] #x coord of lower left point
    print('\nLoaded Geodata contained in File:\t'+str(filename)+'\nCoordinates of LL corner:\t\t '+str(xll)+
          ' / '+str(yll)+'\nGrid Resolution:\t\t\t'+str(res)+'\nArray Shape:\t\t\t\t'+str(arr.shape))
    return arr,xll,yll,res


def shifttopodown(arr, ischild, shift=None):
    '''
    shifts topography array down so lowest value is 0. Subtracts the minimum value from the specified input array.

    example usage: topo,origin_z = shifttopodown(topo,ischild) #when using it for a parent/root
                   topo,origin_z = shifttopodown(topo,ischild,shift=origin_z) #when used for child
    
    Parameters
    ----------
    arr : np.array
        Topography as numpy array.
    ischild: int
        info if the domain is the root or a child.
    shift : float
        how much domain shall be shifted. only taken into account if ischild not 0. Default = None.

    Returns
    -------
    normed : np.array
        Array shifted down by amount.
    amount : float
        Array shifted down by this amount.        
    '''
    import numpy as np
    if ischild == 0:
        amount = arr.min()
        normed = arr - amount
        print('Shifted the input array downwards by '+str(np.round(amount,3))+' meters.')
        
    else:
        amount = shift
        normed = arr - amount
        print('Performed on child domain. Array shifted down by value provided in fcn call "shift": '+str(shift)+' meters.')
        
    return normed, amount


def childifyfilename(fileout, ischild):
    '''
    Modifies filename according to ischild identifier (if child 1 -> _N02) addendm to filename.

    Parameters
    ----------
    fileout : str
        original fileoutname (<RUN>_static).
    ischild : int
        running number of child ID.

    Returns
    -------
    newname : str
        added _NXX to the fileout name.

    '''
    if ischild != 0:
        newname = fileout+'_N0'+str(ischild+1)
    else:
        newname = fileout
    return newname


tlm2palmvegdict = {
    int(0):int(3),    # unclassified > short grass
    int(1):int(9),    # fels > desert
    int(6):int(16),   # gebueschwald > deciduous shrubs
    int(7):int(9),    # lockergestein > desert
    int(9):int(13),   # Gletscher > ice caps and glaciers
    int(11):int(14),  # Feuchtgebiet > bogs and marshes
    int(12):int(17),  # Wald > mixed Forest/woodland
    int(13):int(18),  # Wald offen > interrupted forest
    } 

tlm2palmwatdict = {
    int(5):int(2),    #fliessgewaesser > river
    int(10):int(1),   #stehendes gewaesser > lake
    }
#TODO: to be added and implement in the mapbbclasses

def mapbbclasses(bbarr):
    '''
    Take the TLM bodenbedeckung as numpy array (see geodatatools.py or loadascgeodata())
    and translate the tlm classes into palm classes. This works based on the Bodenbedeckung-
    Dataset so far. The pavement-array is empty for now - use other functions to define pavements.

    TODO: HAVE MAPPING DICT AS INPUT. in fact, do it with a config file that is read and
    also applies to the other veg_pars stuff.

    Parameters
    ----------
    bbarr : np.arr
        numpy array of TLM bodenbedeckung.

    Returns
    -------
    vegarr : np.arr
        vegetation classification for palm.
    pavarr : np.arr
        pavement classification for palm. returned empty so far.
    watarr : np.arr
        water classification for palm.
    soilarr : np.arr
        soil classification for palm.
    '''
    import numpy as np
    
    #vegetation array
    vegarr = np.ones(bbarr.shape)*fillvalues['vegetation_type']#-127
    vegarr[bbarr==0]   = 3  # unclassified > short grass
    vegarr[bbarr==1]   = 9  # fels > desert
    vegarr[bbarr==6]   = 16 # gebueschwald > deciduous shrubs
    vegarr[bbarr==7]   = 9  # lockergestein > desert
    vegarr[bbarr==9]   = 13 # Gletscher > ice caps and glaciers
    vegarr[bbarr==11]  = 14 # Feuchtgebiet > bogs and marshes
    vegarr[bbarr==12]  = 17 # Wald > mixed Forest/woodland
    vegarr[bbarr==13]  = 18 # Wald offen > interrupted forest

    #pavement array
    pavarr = np.ones(bbarr.shape)*fillvalues['pavement_type']

    #water array
    watarr = np.ones(bbarr.shape)*fillvalues['water_type']
    watarr[bbarr==5]   = 2 #fliessgewaesser > river
    watarr[bbarr==10]  = 1 #stehendes gewaesser > lake

    #soiltype array
    soilarr = np.ones(bbarr.shape)*fillvalues['soil_type']
    soilarr[bbarr==0] = 2 #medium
    soilarr[bbarr==1] = 1 #coarse
    soilarr[bbarr==5] = 2 #
    soilarr[bbarr==6] = 2 #
    soilarr[bbarr==7] = 1 #
    soilarr[bbarr==9] = 1 #
    soilarr[bbarr==11] = 1 #
    soilarr[bbarr==12] = 1 #
    soilarr[bbarr==13] = 1 #

       
    print('Unique veget. types:\t'+str(np.unique(vegarr)))
    print('Unique pavement types:\t'+ str(np.unique(pavarr)))
    print('Unique water types:\t'+str(np.unique(watarr)))
    print('Unique soil types:\t'+str(np.unique(soilarr)))
    
    #pavearr can be processed further in other functions with more tlm datasets.
    #if modified -> change function header info.
        
    return vegarr,pavarr,watarr,soilarr


def makesurffractarray(vegarr,pavarr,watarr):
    '''
    Takes vegetation, pavement and water classification arrays for palm, creates a
    surface fraction array out of it.

    Parameters
    ----------
    vegarr : np.array
        vegetation classification array.
    pavarr : np.array
        pavement classification array.
    watarr : np.array
        water classification array.

    Returns
    -------
    sfr : np.array
        surface fraction array

    '''
    import numpy as np
    sfr = np.ones((3,vegarr.shape[0], vegarr.shape[1]))*fillvalues['surface_fraction']
    sfrveg = np.ones(vegarr.shape)
    sfrveg[vegarr != -127] = 1
    sfrveg[vegarr == -127] = 0
    sfrpav = np.ones(pavarr.shape)
    sfrpav[pavarr != -127] = 1
    sfrpav[pavarr == -127] = 0
    sfrwat = np.ones(watarr.shape)
    sfrwat[watarr != -127] = 1
    sfrwat[watarr == -127] = 0
    sfr[0,:,:] = sfrveg
    sfr[1,:,:] = sfrpav
    sfr[2,:,:] = sfrwat
    return sfr


# def modifyvegpars(vegarr,bbarr):
#     '''
#     modify this one manually depending on what values should be set
#     for each bodenbedeckungskategorie or vegetation array category. 
    
    
#     0 - min. canopy resistance
#     1 - leaf area index
#     2 - vegetation coverage
#     3 - canopy resistance coefficient (1/hPa)
#     4 - roughness length for momentum
#     5 - roughness length for heat
#     6 - skin layer heat conductivity (stable cond, W/m2/K)
#     7 - skin layer heat conductivity (unstable cond., W/m2/K)
#     8 - fraction of incoming shortwave radiation transmitted to soil
#     9 - heat capacityof surface skin layer (J/m2/K)
#     10- albedo type (not albedo value! for albedo value -> type=0 and
#         provide albedo_pars)
#     11- emissivity
    
#     To set each category for desired category (either according to
#     palm category or TLM BB category, then uncomment the appropriate
#     section and filter for the appropriate category and set a value
#     according to the PIDS standard.)
    
#     example:
#         if wanting to set albedo type for certain TLM categories:
#         1) uncomment tenarr section. 
#         2) add filter statements and assign new values by adding a line
#             "tenarr[<bbarr or vegarr> == <classification>] = <newvalue>"
#             between the existing statements
    
#     Parameters
#     ----------
#     vegarr : np.array
#         vegetation classification array.
#     bbarr : np.array
#         array with TLM BB classifications.

#     Returns
#     -------
#     vegpars : np.array
#         vegetation parameters array.
    
#     '''
#     import numpy as np
#     vegpars = np.ones((12,vegarr.shape[0], vegarr.shape[1]))*-9999.0
    
#     # zeroarr = vegpars[0,:,:]
#     # 
#     # vegpars[0,:,:]  = zeroarr
    
#     # onearr = vegpars[1,:,:]
#     # 
#     # vegpars[1,:,:]  = onearr
    
#     # twoarr = vegpars[2,:,:]
#     # 
#     # vegpars[2,:,:]  = twoarr
    
#     # threearr = vegpars[3,:,:]
#     # 
#     # vegpars[3,:,:]  = threearr
    
#     # fourarr = vegpars[4,:,:]
#     # 
#     # vegpars[4,:,:]  = fourarr
    
#     # fivearr = vegpars[5,:,:]
#     # 
#     # vegpars[5,:,:]  = fivearr
    
#     # sixarr = vegpars[6,:,:]
#     # 
#     # vegpars[6,:,:]  = sixarr
    
#     # sevenarr = vegpars[7,:,:]
#     # 
#     # vegpars[7,:,:]  = sevenarr
    
#     # eightarr = vegpars[8,:,:]
#     # 
#     # vegpars[8,:,:]  = eightarr
    
#     # ninearr = vegpars[9,:,:]
#     # 
#     # vegpars[9,:,:]  = ninearr
    
#     tenarr = vegpars[10,:,:]
#     tenarr[bbarr == 7] = 0
#     vegpars[10,:,:] = tenarr
    
#     # elevenarr = vegpars[11,:,:]
#     # 
#     # vegpars[11,:,:] = elevenarr
        
#     return vegpars 



def createparsarrays(nx,ny):
    '''
    Creates XXX_pars arrays with correct fill values and "height". 
    If some are not needed, they can be skipped when calling the function, e.g.
    _,_,_,soil_pars,_,_ = createparsarrays(nx,ny) 
    if only the soil_pars array needs to be created.

    Parameters
    ----------
    nx : int
        number of cells in x direction.
    ny : int
        number of cells in y direction.

    Returns
    -------
    vegpars : np.array
        vegetation_pars array with fillvalue and correct number of nvegetation_pars.
    watpars : TYPE
        water_pars array with fillvalue and correct number of nwater_pars.
    pavpars : TYPE
        pavement_pars array with fillvalue and correct number of npavement_pars.
    soilpars : TYPE
        soil_pars array with fillvalue and correct number of nsoil_pars.
    bldpars : TYPE
        building_pars array with fillvalue and correct number of nbuilding_pars.
    albpars : TYPE
        albedo_pars array with fillvalue and correct number of nalbedo_pars.

    '''
    vegpars = np.ones((12,ny,nx))*fillvalues['vegetation_pars']
    watpars = np.ones((7,ny,nx))*fillvalues['water_pars']
    pavpars = np.ones((4,ny,nx))*fillvalues['pavement_pars']
    soilpars = np.ones((8,ny,nx))*fillvalues['soil_pars']
    bldpars = np.ones((136,ny,nx))*fillvalues['building_pars']
    albpars = np.ones((7,ny,nx))*fillvalues['albedo_pars']
    
    return vegpars,watpars,pavpars,soilpars,bldpars,albpars



def modifyparsarray(parsarr, npar, newvalue, filterarr, filtervalue):
    '''
    Modify individual parameters depending on a conditions of a 2D array (filterarr).
    
    Modifies the provided parsarr on the level npar for positions in 2D, where
    the value in the filterarr matches the filtervalue. If it does, it overwrites
    it with the newvalue.
    
    see http://palm.muk.uni-hannover.de/trac/wiki/doc/app/iofiles/pids/static/tables
    
    Example usage: set albedo_type in vegetation_pars where land surface is desert.
    
    vegetation_pars = modifyparsarray(vegetation_pars, 10, 12, vegetation_type, 9)
    
    as in: "modify array at parameter 10 to 12 where vegetation_type is 9."
    
    CAUTION: if ALBEDO-value needs to be set directly, use setalbedovalue() instead,
    which also calls this function to first set albedo_types to 0!

    Parameters
    ----------
    parsarr : np.array (3D)
        3D numpy array of desired parameters
    npar : int
        index of desired parameter to be changed.
    newvalue : float
        new value at filtered positions
    filterarr : np.array (2D)
        2D numpy array for position detection.
    filtervalue : int
        value for which filterarr is filtered.

    Returns
    -------
    parsarr : np.array (3D)
        modified parameter array.

    '''
    
    import numpy as np
    newparsarr = parsarr[npar,:,:]
    newparsarr[filterarr==filtervalue] = newvalue
    parsarr[npar,:,:] = newparsarr
    return parsarr

    
    
    
    


# def modifyXpars(levels,vegarr,bbarr):
#     '''
#     create a parameter array where different parameters can be changed 
#     based on the level (nXXX_pars as coordinate)
    
#     TODO: REWRITE AS GENERIC xxx-PARS FILE: PROVIDE AS INPUT HOW MANY LEVELS, 
#     PROVIDE AS PROMPT WHICH ARRAY VEGARR OR BBARR, PROVIDE AS INPUT WHICH 
#     CATEGORY NUMBER TO BE MODIFIED AND TO WHICH VALUE. RETURN IS AS
#     ARRAY.
#     MAKE IT SO IT ALREADY CREATES ITS OWN COORDINATES!
        
#     To set each category for desired category (either according to
#     palm category or TLM BB category, then uncomment the appropriate
#     section and filter for the appropriate category and set a value
#     according to the PIDS standard.)
    
#     example:
#         if wanting to set albedo type for certain TLM categories:
#         1) uncomment tenarr section. 
#         2) add filter statements and assign new values by adding a line
#             "tenarr[<bbarr or vegarr> == <classification>] = <newvalue>"
#             between the existing statements
    
#     Parameters
#     ----------
#     levels : int
#         how many parameterlevels shall be created.
#     vegarr : np.array
#         vegetation classification array.
#     bbarr : np.array
#         array with TLM BB classifications. Does not necessarily have to be provided, can also be None.

#     Returns
#     -------
#     vegpars : np.array
#         vegetation parameters array.
    
#     '''
#     import numpy as np
#     xpars = np.ones((levels,vegarr.shape[0], vegarr.shape[1]))*-9999.0
    
#     modarr = xpars[10,:,:]
#     modarr[bbarr == 7] = 0
#     xpars[10,:,:]  = modarr
    
#     return xpars
 
    

def setalbedovalue(albedopars, vegpars, filterarr, filtervalue, newvalue, npar):
    '''
    Set albedo-values directly in albedo_pars and in vegetation_pars the albedo
    type to 0 (user defined) in one go. 
        
       

    
    example, if wanting to set albedo for certain TLM categories:
        
        albpars = setalbedovalue(albpars, vegpars, vegarr, 9, 0.5)
        ...changes the albedo value at positions where
            a) vegetation type is 9
            b) vegpars[10] is 0
                                           ...to 0.5. 
            
    
    Parameters
    ----------
    albedopars : np.array 3D
        albedo_pars array.
    vegpars : np.array
        vegpars vegetation parameters.
    filterarr : np.array
        vegetation classification- or BB array.
    filtervalue : int
        value with which filterarr will be filtered.
    newvalue : float
        new value to be entered.
    npar : int
    which parameter. set -1 for all the same value, otherwise specify nalbedo_pars

    Returns
    -------
    vegpars : np.array
        vegetation_pars array with albedo_type set to 0 for filterarr==filtervalue
    albedopars : np.array
        albedo parameters that are user defined.

    '''
    
    vegpars = modifyparsarray(vegpars,10,0,filterarr,filtervalue)
  
    # zeroarr = albedopars[0,:,:]
    # zeroarr[(filterarr == filtervalue) & (vegpars[10,:,:] == 0)] = newvalue
    # albedopars[0,:,:]  = zeroarr
    
    # onearr = albedopars[1,:,:]
    # onearr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[1,:,:]  = onearr
    
    # twoarr = albedopars[2,:,:]
    # twoarr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[2,:,:]  = twoarr
    
    # threearr = albedopars[3,:,:]
    # threearr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[3,:,:]  = threearr
    
    # fourarr = albedopars[4,:,:]
    # fourarr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[4,:,:]  = fourarr
    
    # fivearr = albedopars[5,:,:]
    # fivearr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[5,:,:]  = fivearr
    
    # sixarr = albedopars[6,:,:]
    # sixarr[(filterarr == filtervalue) & (vegpars[10,:,:]==0)] = newvalue
    # albedopars[6,:,:]  = sixarr
    
    if npar == -1:
        for i in range(albedopars.shape[0]):
            zeroarr = albedopars[i,:,:]
            zeroarr[(filterarr == filtervalue) & (vegpars[10,:,:] == 0)] = newvalue
            albedopars[i,:,:]  = zeroarr
    
    else:
        zeroarr = albedopars[npar,:,:]
        zeroarr[(filterarr == filtervalue) & (vegpars[10,:,:] == 0)] = newvalue
        albedopars[npar,:,:]  = zeroarr
    
    return vegpars,albedopars


def createstaticcoords(xsize, ysize, pixelsize):
    '''
    Provide x and y size of the raster by specifying topo.shape[0] for x and topo.shape[1] for y (or bare values with
    the danger of it not matching.

    Parameters
    ----------
    xsize : int
        number of cells in rasters in x direction.
    ysize : int
        number of cells in rasters in y direction.
    pixelsize : int
        width of a pixel of the raster (resolution).

    Returns
    -------
    x : np.array
        x coordinates in correct spacing.
    y : np.array
        y coordinates in correct spacing.
    nsurface_fraction : np.array
        nsurface_fraction coordinates in correct spacing.
    nvegetation_pars : np.array
        nvegetation_pars coordinates in correct spacing.
    nalbedo_pars : np.array
        nalbedo_pars coordinates in correct spacing.
    '''
    import numpy as np
    
    xleft = 0; xright = xsize-1
    yfront = 0; yback = ysize-1
    
    x = np.arange(xleft,xright*pixelsize+pixelsize,pixelsize) + 0.5*pixelsize
    y = np.arange(yfront, yback*pixelsize+pixelsize, pixelsize) + 0.5*pixelsize
    nsurface_fraction = np.array([0,1,2])
    nvegetation_pars = np.array([0,1,2,3,4,5,6,7,8,9,10,11])
    nalbedo_pars = np.array([0,1,2,3,4,5,6])
    npavement_pars = np.arange(0,4)
    nsoil_pars = np.arange(0,8)
    nwater_pars = np.arange(0,7)
    npavement_subsurface_pars = np.arange(0,2)
    nbuilding_pars = np.arange(0,136)
    nbuilding_surface_pars = np.arange(0,28)
    
    return x, y, nsurface_fraction, nvegetation_pars, nalbedo_pars, npavement_pars, nsoil_pars, nwater_pars, nbuilding_pars



def createDataArrays(array, dims, coords):
    '''
    Creates DataArrays. Provide the numpy array, its dimensions as a list of strings in correct order
    ([<3rd>,y,x]) and provide the coordinates as list of variables in same order as dimensions.
    Flips the numpy arrays (due to requirement that row 0 is at south corner and not 
    as in numpy at north (most upwards) side) and returns a xr.Dataarray, 
    name it with variable name as defined in the PIDS.

    example usage: vegetation_type = createDataArrays(vegarr,['y','x'],[y,x])

    Parameters
    ----------
    array : np.array
        DESCRIPTION.
    dims : list of strings
        in correct order ([<3rd dimension>,y,x]). 3rd dimension could be z, nvegetation_pars or else.
    coords : list of variables
        same order as dims but not as strings, but variables.

    Returns
    -------
    dataarray : xr.DataArray
        xr Dataarray, name it appropriately like the variable name defined in the PIDS for the specific data array.

    '''
    import xarray as xr
    if len(dims) == 2:
        arrflip = np.flip(array, axis=0)
        dataarray = xr.DataArray(arrflip, dims=dims, coords={dims[1]:coords[1], dims[0]:coords[0]})
    if len(dims) == 3:
        arrflip = np.flip(array, axis=1)
        dataarray = xr.DataArray(arrflip, dims=dims, coords={dims[2]:coords[2], dims[1]:coords[1], dims[0]:coords[0]})
    return dataarray


def setNeededAttributes(dataarray, staticvariable):    
    '''
    Sets attributes.

    Parameters
    ----------
    dataarray : TYPE
        DESCRIPTION.
    staticvariable : string
        static file variable name as it is defined in PIDS.

    Returns
    -------
    None.

    '''
    if staticvariable == 'zt':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'terrain_height';
        
    if staticvariable == 'vegetation_type':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'vegetation type classification'
    
    if staticvariable == 'water_type':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'water type classification'

    if staticvariable == 'pavement_type':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'pavement type classification'
    
    if staticvariable == 'soil_type':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'soil type classification'    
        
    if staticvariable == 'surface_fraction':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'surface_tile_fraction'    
        
    if staticvariable == 'buildings_2d':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'vegetation parameters'         
     
    if staticvariable == 'building_id':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'building id numbers'      
     
    if staticvariable == 'building_type':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'building type classification'     
     
    if staticvariable == 'vegetation_pars':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'vegetation_parameters'    
     
    if staticvariable == 'albedo_pars':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'albedo parameters'
        
    if staticvariable == 'pavement_pars':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'pavement parameters'      
        
    if staticvariable == 'water_pars':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'water parameters'      
    
    if staticvariable == 'lad':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'leaf area density'          

    return


# def assembleDataset(zt=None,vegetation_type=None,water_type=None,
#                     pavement_type=None,soil_type=None,
#                     surface_fraction=None,vegetation_pars=None):
#     '''
#     Creates a static file from provided dataarrays. The Function asks if you
#     want to add each variable it has been designed for so far to the static file. 
#     confirm with "y" for each variable. DataArrays need to be present beforehand with correct name 
#     (like variable name defined in PIDS.)
    
#     Returns
#     -------
#     static: xr.Dataset
#         static dataset.   
        
#     '''
#     import xarray as xr
#     static = xr.Dataset()
#     if zt != None:
#         static['zt'] = zt
#     if vegetation_type != None:
#         static['vegetation_type'] = vegetation_type
#     if water_type != None:
#         static['water_type'] = water_type
#     if soil_type != None:
#         static['soil_type'] = soil_type
#     if pavement_type != None:
#         static['pavement_type'] = pavement_type
#     if surface_fraction != None:
#         static['surface_fraction'] = surface_fraction
#     if vegetation_pars != None:
#         static['vegetation_pars'] = vegetation_pars
    
    
    # return static
    


infodict = {'version':           1,
           'palm_version':      6.0,
           'origin_z':          0.0,
           'origin_y':          0.0,
           'origin_x':          0.0,
           'origin_lat':        0.0,
           'origin_lon':        00,
           'origin_time':       '2000-01-01 00:00:00 +0',
           'rotation_angle':    0.0,
           }

def setGlobalAttributes(static, infodict):
    '''
    sets global Attributes to the static dataset accordint to the infordir.
    infodict example: 
        
        infodict = {'version':           1,
                    'palm_version':      6.0,
                    'origin_z':          0.0,
                    'origin_y':          189000.0,
                    'origin_x':          730000.0,
                    'origin_lat':        46.8392,
                    'origin_lon':        9.143,
                    'origin_time':       '2018-08-04 12:00:00 +01',
                    'rotation_angle':    0.0,
                    }

    Parameters
    ----------
    static : xr.Dataset
        DESCRIPTION.
    infodir : dict
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    static.attrs['version'] = infodict['version']
    static.attrs['origin_z'] = infodict['origin_z']
    static.attrs['origin_y'] = float(infodict['origin_y'])
    static.attrs['origin_x'] = float(infodict['origin_x'])
    static.attrs['origin_lat'] = infodict['origin_lat']
    static.attrs['origin_lon'] = infodict['origin_lon']
    static.attrs['rotation_angle'] = infodict['rotation_angle']
    static.attrs['palm_version'] = infodict['palm_version']
    static.attrs['origin_time'] = infodict['origin_time']

    static.coords['x'].attrs['_FillValue'] = fillvalues['E_UTM']
    static.coords['x'].attrs['units'] = 'm'
    static.coords['y'].attrs['_FillValue'] = fillvalues['N_UTM']
    static.coords['y'].attrs['units'] = 'm'






    
encodingdict = {'x':                {'dtype': 'float32'}, 
                'y':                {'dtype': 'float32'},
                'zt':               {'dtype': 'float32'},
                'vegetation_type':  {'dtype': 'int8'},
                'water_type':       {'dtype': 'int8'},
                'soil_type':        {'dtype': 'int8'},
                'pavement_type':    {'dtype': 'int8'},
                'surface_fraction': {'dtype': 'float32'},
                'vegetation_pars':  {'dtype': 'float32'}
                }

def outputstaticfile(static, fileout, encodingdict):
    '''
    Output the static file. Requires a encoding dict.

    Parameters
    ----------
    static : TYPE
        DESCRIPTION.
    fileout : TYPE
        DESCRIPTION.
    encodingdict : dict
        dict with specified datatypes for each variable and coordinate variable.
        known datatypes that work: NC_FLOAT = int32 or float32, NC_BYTE = int8
        
        example: encodingdict = {'x':                {'dtype': 'float32'}, 
                                 'y':                {'dtype': 'float32'},
                                 'zt':               {'dtype': 'float32'},
                                 'vegetation_type':  {'dtype': 'int8'}}
    
    Returns
    -------
    None.

    '''
    import xarray as xr
    static.to_netcdf(fileout, mode='w', format="NETCDF3_CLASSIC",
                     encoding = encodingdict)

    























