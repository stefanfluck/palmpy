#%%
'''
stefan fluck, 22.01.2020
functions to cut swissalti3d dtm datafile and swisstlm shapefiles.

Last updated: 29.01.2020
'''


def cutalti(filein, fileout, xmin, xmax, ymin, ymax, xres, yres):
    '''
    cuts geotiff input file into fileout with bounds xmin/max ymin/max with resultion xres,yres. 
    fileout should be designated with format in mind: ".asc" for ascii.
    
    example usage:
        par = cutalti('swissALTI3D2018.tif', 'parentdhm.asc', xmin=730000, 
                      xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)

    - also cuts orthoimages, but output needs to be tif.
    - if error message says "NoneType" object has no attribute 'GetGeoTransform', relative Path
      is incorrect.
      
    Parameters
    ----------
    filein : str
        filename of input file. Provide a Geotiff raster file.
    fileout : str
        output filename. set output type by chosing an appropriate file ending (.asc for ASCII).
    xmin : int
        lower left corner x coordinate.
    xmax : int
        upper right corner x coordinate.
    ymin : int
        lower left corner y coordinate.
    ymax : int
        upper right corner y coordinate.
    xres : int
        target resolution in x direction.
    yres : int
        target resolution in y direction. choose symmetrically to xres.

    Returns
    -------
    array : np.array
        dhm info as numpy array. array index 0 is northern most line (already flipped).
    SAVES CUT TIF FILE UNDER fileout VARIABLE AS WELL. SEE fileout FOR TYPES.

    '''
    from osgeo import gdal
    ds = gdal.Open(filein)
    gtrf = ds.GetGeoTransform()
    print('Origin before cutting: '+str(gtrf[0])+'/'+str(gtrf[3])+'. Resolution: '+str(gtrf[1])+' m.')
    ds = gdal.Translate(fileout, ds, projWin=[xmin, ymax, xmax, ymin], xRes=xres, yRes = yres)
    gtrf = ds.GetGeoTransform()
    print('Origin after cutting: '+str(gtrf[0])+'/'+str(gtrf[3])+'. Resolution: '+str(gtrf[1])+' m.')
    print('Raster Size: X: '+str(ds.RasterXSize)+' Y: '+str(ds.RasterYSize))
    array = ds.ReadAsArray()
    return array
    
def rasterandcuttlm(filein, fileout, xmin, xmax, ymin, ymax, xres, yres, burnatt='OBJEKTART'):
    '''
    Takes a swissTLM3D .shp input file (mainly BB), creates a tif file with resolution xres/yres of
    the shp vector data and saves it as tmp.tif. This is loaded again and is transformed to ascii. Direct
    ascii creation is not available with gdal. The tmp.tif is removed in the end.

    example usage:
        tlmbb = rasterandcuttlm('bb.shp', 'tlm.asc', xmin=730000, xmax=742000, 
                                ymin=190000, ymax=202000, xres=40, yres=40)


    Parameters
    ----------
    filein : str
        filename of input shapefile to be converted to raster.
    fileout : str
        output filename. set output type by chosing an appropriate file ending (.asc for ASCII).
    xmin : int
        lower left corner x coordinate.
    xmax : int
        upper right corner x coordinate.
    ymin : int
        lower left corner y coordinate.
    ymax : int
        upper right corner y coordinate.
    xres : int
        target resolution in x direction.
    yres : int
        target resolution in y direction. choose symmetrically to xres.
    burnatt : TYPE, optional
        Which attribute of the TLM dataset to be burned into the array. For most, OBJEKTART is the best choice
        The default is 'OBJEKTART'.

    Returns
    -------
    array : np.array
        tlm burnatt as np array. array index 0 is northern most line (already flipped).
    SAVES CUT TIF FILE UNDER fileout VARIABLE AS WELL. SEE fileout FOR TYPES.

    '''
    from osgeo import ogr, gdal
    import os
    srcds = ogr.Open(filein)
    srclayer = srcds.GetLayer()
    x_res = int((xmax - xmin) / xres)
    y_res = int((ymax - ymin) / yres)
    trgds = gdal.GetDriverByName('GTiff').Create('tmp.tif', x_res,y_res,1,gdal.GDT_Float32)
    trgds.SetGeoTransform((xmin,xres,0,ymax,0,-xres))
    band = trgds.GetRasterBand(1)
    band.SetNoDataValue(-9999)
    gdal.RasterizeLayer(trgds, [1], srclayer, options=['ATTRIBUTE='+burnatt])
    trgds=None
    ds = gdal.Open('tmp.tif')
    ds = gdal.Translate(fileout, ds)
    array = ds.ReadAsArray()
    ds = None
    os.remove('tmp.tif')
    return array


def lv95towgs84(E,N):
    '''
    converts lv95 (or lv03, in which case it adds 2000000 or 1000000 to the coordinates)
    swiss coordinates to wgs84 coordinates according to 
    "Formeln und Konstanten für die Berechnung der Schweizerischen schiefachsigen 
    Zylinderprojektion und der Transformation zwischen Koordinatensystemen" by swisstopo, P.14.
    
    Parameters
    ----------
    E : float
        east component (with leading 2!).
    N : float
        north component (with leading 1!).

    Returns
    -------
    lon : float
        longitude in wgs84.
    lat : TYPE
        latitude in wgs84.

    '''
    import numpy as np
    if E < 1500000:
        E += 2000000
    if N < 900000:
        N += 1000000
    ys = (E-2600000)/1000000
    xs = (N-1200000)/1000000
    ls = 2.6779094 + 4.728982*ys + 0.791484 * ys * xs + 0.1306 * ys * xs**2 - 0.0436 * ys**3
    ps = 16.9023892 + 3.238272 * xs - 0.270978 * ys**2  - 0.002528 * xs**2  - 0.0447 * ys**2 * xs - 0.0140 * xs**3 
    lon = np.round(ls*100/36,4)
    lat = np.round(ps*100/36,4)
    return lon,lat



def cutortho(filein, fileout, xmin, xmax, ymin, ymax, xres, yres):
    '''
    Cuts an orthoimage in geotif format to the provided boundaries and resolution, 
    does not change crs. Only tested for outputting again a .tif geotif file. 
    

    Parameters
    ----------
    filein : str
        filename of input file. Provide a Geotiff orthoimage file.
    fileout : str
        output filename with ending .tif.
    xmin : int
        lower left corner x coordinate.
    xmax : int
        upper right corner x coordinate.
    ymin : int
        lower left corner y coordinate.
    ymax : int
        upper right corner y coordinate.
    xres : int
        target resolution in x direction.
    yres : int
        target resolution in y direction. choose symmetrically to xres.

    Returns
    -------
    Saves cut orthoimage to provided path. No return in python.
    
    '''
    from osgeo import gdal
    ds = gdal.Open(filein)
    ds = gdal.Translate(fileout, ds, projWin=[xmin, ymax, xmax, ymin], xRes=xres, yRes = yres)


#%%
# par = cutalti('swissALTI3D2018.tif', 'parentdhm.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
# chi = cutalti('swissALTI3D2018.tif', 'childdhm.asc', xmin=735000, xmax=738000, ymin=194720, ymax=197720, xres=20, yres=20)

# tlmbb = rasterandcuttlm('bb.shp', 'tlm.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
# tlmgeb = rasterandcuttlm('gebaeudefootprint.shp', 'gebaeude.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
