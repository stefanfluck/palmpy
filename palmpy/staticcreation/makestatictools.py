"""
Created on Thu Jan 30 10:13:51 2020
STATIC CREATION FILE TURNED INTO FUNCTIONS

TODO: 
    
    -   dicts to be added and implemented in the mapbbclasses

    -   when implementing streets, implement a function that sets pavement_type, street_type,
        etc to fillvalue where it intersects with building_2d (np.where, check palm_csd)


"""
import numpy as np


def checknestcoordsvalid(dxyp,dxyn,nllx,nlly):
    '''
    Checks if grid spacing of parent and child match, also if lower left position of nest is aligned 
    with parent grid.

    Parameters
    ----------
    dxyp : float
        grid spacing of parent/root.
    dxyn : float
        grid spacing of nest.
    nllx : float
        lower left corner x of nest.
    nlly : float
        lower left corner y of nest.

    Returns
    -------
    result : Boolean
        True if checks are passed.

    '''
    dxyp = float(dxyp)
    dxyn = float(dxyn)
    nllx = float(nllx)
    nlly = float(nlly)
    result = False
    
    if (dxyp%dxyn==0) & (nllx%dxyp==0) & (nlly%dxyp==0):
        print('\nSUCCESS - Chosen parameters for dxy of child and parent and llxy of child match')
        result = True
    if (nllx%dxyp!=0):
        print('\nError: llx of nest not integer divisible by dxyp, hence not aligned with parent grid')
    if (nlly%dxyp!=0):
        print('\nError: lly of nest not integer divisible by dxyp, hence not aligned with parent grid')
    if (dxyp%dxyn!=0):
        print('\nError: dxyn not an integer divisor of dxyp, does not align')
    return result

def checknxyzvalid(nx,ny,nz):
    '''
    Checks if nx,ny and nz will pass the palm checks.

    Parameters
    ----------
    nx : int
        number of cells in x.
    ny : int
        number of cells in y.
    nz : int
        number of cells in z.

    Returns
    -------
    result : Boolean
        True if checks are passed.

    '''
    result = False
    if (nx%nz==0) & (ny%nz==0):
        print('\nSUCCESS - Chosen parameters and resulting nx, ny and nz match')
        result=True
    if (nx%nz!=0):
        print('\nnx is not integer divisible by nz')
    if (ny%nz!=0):
        print('\nny is not integer divisible by nz')
    return result


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
   "tree_id": int(-9999),
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
   "tree_type": np.byte(-127),
   "lad": float(-9999.0)
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

'''
DICTIONARY MAPPING BODENBEDECKUNG AND OTHER CATEGORIES TO PALM CLASSES. BEST GUESS. IMPORT ARRAY IN 
STATIC GENERATION SCRIPTS FOR INDIVIDUAL CHANGES.
'''
tlmbb2veg = {
    #vegetation classes
    int(0):int(3),    # unclassified > short grass
    int(1):int(9),    # fels > desert
    int(6):int(16),   # gebueschwald > deciduous shrubs
    int(7):int(9),    # lockergestein > desert
    int(9):int(13),   # Gletscher > ice caps and glaciers
    int(11):int(14),  # Feuchtgebiet > bogs and marshes
    int(12):int(17),  # Wald > mixed Forest/woodland
    int(13):int(18),  # Wald offen > interrupted forest
   }

tlmbb2wat = {
    int(5):int(2),    #fliessgewaesser > river
    int(10):int(1),   #stehendes gewaesser > lake
    }

tlmstr2str = {
    
    }

ownclass2palm = {
    int(1001) : 'etwas für maisfeld'
    }




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
    
    #vegetation array, was done before knowing np.vectorization(dict.get)(inarr)
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

       
    # print('Unique veget. types:\t'+str(np.unique(vegarr)))
    # print('Unique pavement types:\t'+ str(np.unique(pavarr)))
    # print('Unique water types:\t'+str(np.unique(watarr)))
           
    return vegarr,pavarr,watarr #,soilarr




def makesoilarray(vegarr,pavarr):
    '''
    Creates Soilarray from vegarr and pavement array. Everywhere where vegetation_type and pavement_type are nonzero values
    a soiltype class needs to be specified.

    Parameters
    ----------
    vegarr : np.array
        vegetation type array in palm classification.
    pavarr : np.array
        pavement type array in palm classification.

    Returns
    -------
    soilarr : np.array
        soil array classificaton.

    '''
    soilarr = np.ones(vegarr.shape)*fillvalues['soil_type']
    soilarr = np.where( (vegarr[:,:] != fillvalues['vegetation_type'] ), 2, soilarr[:,:])
    
    soilarr = np.where( (vegarr[:,:] == 1), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 2), 6, soilarr[:,:]) 
    soilarr = np.where( (vegarr[:,:] == 16), 2, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 9), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 3), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 13), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 14), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 17), 1, soilarr[:,:])
    soilarr = np.where( (vegarr[:,:] == 18), 1, soilarr[:,:])
    
    soilarr = np.where( (pavarr[:,:] != fillvalues['pavement_type']), 3, soilarr[:,:])
    #TODO: Add more exact pavement classifications fpr soils
    return soilarr


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
    
    newparsarr = parsarr[npar,:,:]
    newparsarr[filterarr==filtervalue] = newvalue
    parsarr[npar,:,:] = newparsarr
    
    return parsarr

 
    

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



def mapstreettypes(roadarr):
    '''
    map street classes from swisstlm (0-22) to approximately the ones from palm
    categorization. resembles openstreetmap classes. Best guess applied in 
    mapping dictionary.
    required for chem emission parametrization
                
    Parameters
    ----------
    roadarr : np.array
        tlm objektarten für roads. fillvalue shall be -9999.
    
    Returns
    -------
    street_type : np.array
        street_types array with palm classification for road types.   
    
    '''
    
    import numpy as np
    mapdict = {-9999 : fillvalues['street_type'],
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
               14   : fillvalues['street_type'],
               15   : 4,
               16   : 3,
               17   : 3,
               18   : 3,
               19   : 3,
               20   : 13,
               21   : 15,
               22   : 3}
    street_type = np.vectorize(mapdict.get)(roadarr)
    return street_type







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
#    npavement_subsurface_pars = np.arange(0,2)
    nbuilding_pars = np.arange(0,136)
#    nbuilding_surface_pars = np.arange(0,28)
    
    return x, y, nsurface_fraction, nvegetation_pars, nalbedo_pars, npavement_pars, nsoil_pars, nwater_pars, nbuilding_pars



def createdataarrays(array, dims, coords):
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


def setneededattributes(dataarray, staticvariable):    
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
        dataarray.attrs['lod'] = int(1)      
     
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
  
    if staticvariable == 'tree_id':
        dataarray.attrs['_FillValue'] = fillvalues[staticvariable]
        dataarray.attrs['long_name'] = 'tree id'          

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

def setglobalattributes(static, infodict):
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




# encodingdict = {'x':                {'dtype': 'float32'}, 
#                 'y':                {'dtype': 'float32'},
#                 'zt':               {'dtype': 'float32'},
#                 'vegetation_type':  {'dtype': 'int8'},
#                 'water_type':       {'dtype': 'int8'},
#                 'soil_type':        {'dtype': 'int8'},
#                 'pavement_type':    {'dtype': 'int8'},
#                 'surface_fraction': {'dtype': 'float32'},
#                 'vegetation_pars':  {'dtype': 'float32'}
#                 }

def setupencodingdict(flags):
    '''
    creates a encodingdict dictionary for saving static files 
    in xarray

    Parameters
    ----------
    flags : dict
        dict from the static generation script.

    Returns
    -------
    encodingdict : dict
        encoding dict with needed conversions.

    '''
    encodingdict = {'x':  {'dtype': 'float64'}, 
                    'y':  {'dtype': 'float64'}}
    if flags['doterrain'] == True:
        encodingdict['zt'] = {'dtype': 'float32'}
    if flags['dotlmbb'] == True:
        encodingdict['vegetation_type'] = {'dtype': 'int8'}
        encodingdict['water_type'] = {'dtype': 'int8'}
        encodingdict['soil_type'] = {'dtype': 'int8'}
        encodingdict['pavement_type'] = {'dtype': 'int8'}
        encodingdict['surface_fraction'] = {'dtype': 'float32'}
        encodingdict['nsurface_fraction'] = {'dtype': 'float32'}
    if flags['dovegpars'] == True:
        encodingdict['vegetation_pars'] = {'dtype':'float32'}
    if flags['doalbedopars'] == True:
        encodingdict['albedo_pars'] = {'dtype':'float32'}
    if flags['dolad'] == True:
        encodingdict['lad'] = {'dtype':'float32'}
        encodingdict['tree_id'] = {'dtype':'int32'}
    if flags['dobuildings2d'] == True:
        encodingdict['buildings_2d'] = {'dtype':'float32'}
        encodingdict['building_id'] = {'dtype':'int32'}
    if flags['dobuildings3d'] == True:
        encodingdict['buildings_3d'] = {'dtype':'uint8'}
        encodingdict['building_id'] = {'dtype':'int8'}
    if flags['dostreettypes'] == True:
        encodingdict['street_type'] =  {'dtype':'int8'}
    return encodingdict





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

    


#CANOPY IMPLEMENTATION
def createzlad(maxtreeheight, dz):
    '''
    Creates zlad from a maximum tree height and a dz.

    Parameters
    ----------
    maxtreeheight : float
        max tree height.
    dz : float
        vertical grid spacing.

    Returns
    -------
    zlad : np.array
        array of zlad levels.

    '''
    zlad = np.arange(0,np.floor(maxtreeheight/dz)*dz+2*dz, dz)
    zlad[1:] = zlad[1:]-0.5*dz
    return zlad


def showbetadistribution():
    '''
    plots various distributions for different alpha and beta values

    Returns
    -------
    shows plot.

    '''
    from scipy.stats import beta
    import matplotlib.pyplot as plt
    fig=plt.figure()
    ax=fig.gca()
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=2, b=2), label='a=2,b=2')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=1.3, b=1.1), label='a=1.3,b=1.1')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=4, b=2), label='a=4,b=2')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=5, b=2), label='a=5,b=2')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=2, b=3), label='a=2,b=3')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=2, b=1.2), label='a=2,b=1.2')
    ax.plot(np.arange(0,1,0.01),beta.pdf(x=np.arange(0,1,0.01), a=3, b=1.2), label='a=3,b=1.2')
    ax.legend(); ax.grid()































