"""
Created on Thu Jan 30 10:13:51 2020
STATIC CREATION FILE TURNED INTO FUNCTIONS

"""

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


def shifttopodown(arr):
    '''
    shifts topography array down so lowest value is 0. Subtracts the minimum value from the specified input array.

    example usage: topo = shifttopodown(topo)
    
    Parameters
    ----------
    arr : np.array
        Topography as numpy array.

    Returns
    -------
    normed : np.array
        Array shifted down by amount.
        
    '''
    import numpy as np
    amount = arr.min()
    normed = arr - amount
    print('Shifted the input array downwards by '+str(np.round(amount,3))+' meters.')
    return normed


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


#%%
#params for createstaticfile

ischild = 0



def createstaticfile():
    import xarray as xr
    


























