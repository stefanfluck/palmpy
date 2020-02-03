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
    print('\nLoaded Geodata contained in File:\t'+str(filename)+'\nCoordinates of LL corner:\t '+str(xll)+
          ' / '+str(yll)+'\nGrid Resolution:\t\t'+str(res))
    return arr,xll,yll,res


