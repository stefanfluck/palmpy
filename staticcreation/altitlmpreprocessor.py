#%%
'''
stefan fluc, 22.01.2020
functions to cut swissalti3d dtm datafile and swisstlm shapefiles.
'''

from osgeo import gdal

def cutalti(filein, fileout, xmin, xmax, ymin, ymax, xres, yres):
    ds = gdal.Open(filein)
    ds = gdal.Translate(fileout, ds, projWin=[xmin, ymax, xmax, ymin], xRes=xres, yRes = yres)
    ds = None
    
def cuttlm(filein, fileout, xmin, xmax, ymin, ymax, xres, yres, burnatt='OBJEKTART'):
    ds = gdal.Open(filein)
    ds = gdal.Rasterize
