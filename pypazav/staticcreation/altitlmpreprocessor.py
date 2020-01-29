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
        dhm info as numpy array.

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
    array : TYPE
        DESCRIPTION.

    '''
    from osgeo import ogr, gdal
    import os
    srcds = ogr.Open(filein)
    srclayer = srcds.GetLayer()
    x_res = int((xmax - xmin) / xres)
    y_res = int((ymax - ymin) / yres)
    trgds = gdal.GetDriverByName('GTiff').Create('tmp.tif', x_res,y_res,1,gdal.GDT_Byte)
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



    
    

#%%
# par = cutalti('swissALTI3D2018.tif', 'parentdhm.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
# chi = cutalti('swissALTI3D2018.tif', 'childdhm.asc', xmin=735000, xmax=738000, ymin=194720, ymax=197720, xres=20, yres=20)

# tlmbb = rasterandcuttlm('bb.shp', 'tlm.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
# tlmgeb = rasterandcuttlm('gebaeudefootprint.shp', 'gebaeude.asc', xmin=730000, xmax=742000, ymin=190000, ymax=202000, xres=40, yres=40)
