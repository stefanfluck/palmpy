"""
create static files just using dhm and tlm bb

TODO: make it so an infinite number of nests can be used. use lists for every parameter instead of 
      laufnummer-variable names and provide indexes. 


"""
import xarray as xr
from pathlib import Path
import sys
import configparser as cfp
import numpy as np

modulepath = str(Path.home() / 'Documents' / 'Python Scripts' / 'ZAV-PALM-Scripts')
if modulepath not in sys.path:
    sys.path.append(modulepath)
    
import palmpy.staticcreation.geodatatools as gdt
import palmpy.staticcreation.makestatictools as mst
    
# from palmpy.staticcreation.geodatatools import *
# from palmpy.staticcreation.makestatictools import *

#%% setup
filenames =   'yverdon_static'
totalnumberofdomains = 3
flags = (1,1,0,0,0)  # ( zt, TLMBBtypes, vegetation_pars, albedo_pars, treeraster)
origin_time = '2019-06-07 12:00:00 +02'
cutorthoimg = True  # provide orthoimages for parent and child domains

#GEODATA FILES
ortho = "E:\\Dokumente\\Bibliothek\\Meteorology\\Geodaten\\zrh_lszh_winti\\swissimage2.5m_latest.tif"
dhm = "E:\\Dokumente\\Bibliothek\\Meteorology\\Geodaten\\zrh_lszh_winti\\swissALTI3D2018.tif"
bb = "E:\\Dokumente\\Bibliothek\\Meteorology\\Geodaten\\zrh_lszh_winti\\tlm\\swissTLM3D_2019_tlm_bodenbedeckung\\bb.shp"

#OUTPUT
outpath = str(Path.home() / 'Desktop' / 'yverdon_out')+'\\'

poix,poiy      =  536953.0, 179395.0                # Point of interest ARP
poi2x,poi2y    =  536524.0, 178530.0                # Point of Interest, Messstation

#parent
ischild0       =   0
xaus0,yaus0    =   8192.0, 8192.0                   # dimensions of domain in meter
xmin0,ymin0    =   poi2x-xaus0/2, poi2y-yaus0/2       # lower left corner (origin) coordinates
xmax0, ymax0   =   xmin0+xaus0, ymin0+yaus0         # calculation of upper right corner coords
zmax0          =   4096.0                           # vertical extent
xres0,yres0,zres0    =  32.0, 32.0, 32.0            # resolutions

nx0      =  (xmax0-xmin0)/xres0                     # number of gridpoints in x
ny0      =  (ymax0-ymin0)/yres0                     # number of gridpoints in y
nz0      =  zmax0/zres0                             # number of gridpoints in z
mst.checknxyzvalid(nx0,ny0,nz0)                     # parentchecks

#child 1
ischild1       =   1
xaus1,yaus1    =   3072.0, 3072.0                   # dimensions of domain in meter
xmin1,ymin1    =   poi2x-xaus1/2, poi2y+512-yaus1/2       # lower left corner (origin) coordinates
xmax1, ymax1   =   xmin1+xaus1, ymin1+yaus1         # calculation of upper right corner coords
zmax1          =   3072.0                            # vertical extent
xres1,yres1,zres1    =  16.0, 16.0, 16.0            # resolutions

nx1      =  (xmax1-xmin1)/xres1                     # number of gridpoints in x
ny1      =  (ymax1-ymin1)/yres1                     # number of gridpoints in y
nz1      =  zmax1/zres1                             # number of gridpoints in z
llx1     =   xmin1-xmin0                            # ll-corner x coords in parent coord system
lly1     =   ymin1-ymin0                            # ll-corner y coords in parent coord system

mst.checknxyzvalid(nx1,ny1,nz1)                     # childchecks
mst.checknestcoordsvalid(xres0,xres1,llx1,lly1)     # childchecks

#child 2
ischild2       =   2
xaus2,yaus2    =   1024.0, 1024.0                   # dimensions of domain in meter
xmin2,ymin2    =   poi2x-xaus2/2, poi2y+256-(yaus2/2)       # lower left corner (origin) coordinates
xmax2, ymax2   =   xmin2+xaus2, ymin2+yaus2      # calculation of upper right corner coords
zmax2          =   256.0                            # vertical extent
xres2,yres2,zres2    =  2.0, 2.0, 2.0            # resolutions

nx2      =  (xmax2-xmin2)/xres2                     # number of gridpoints in x
ny2      =  (ymax2-ymin2)/yres2                     # number of gridpoints in y
nz2      =  zmax2/zres2                             # number of gridpoints in z
llx2     =   xmin2-xmin1                            # ll-corner x coords in parent coord system
lly2     =   ymin2-ymin1                            # ll-corner y coords in parent coord system

mst.checknxyzvalid(nx2,ny2,nz2)                     # childchecks
mst.checknestcoordsvalid(xres1,xres2,llx2,lly2)     # childchecks



#%%#######################################################
## This section creates the parent static file.

#assign values
filename = filenames
ischild = ischild0 #Child id. this here is not a child, i.e. parent.

xmin = xmin0 #in LV03 Koordinaten, lower left corner
xmax = xmax0
ymin = ymin0 #in LV03 Koordinaten, lower left corner
ymax = ymax0
xres = xres0
yres = xres0

infodict = {'version':           1,
            'palm_version':      6.0,
            'origin_z':          0.0, #is changed further below
            'origin_y':          ymin,
            'origin_x':          xmin,
            'origin_lat':        gdt.lv95towgs84(xmin+2000000,ymin+1000000)[1],
            'origin_lon':        gdt.lv95towgs84(xmin+2000000,ymin+1000000)[0],
            'origin_time':       origin_time,
            'rotation_angle':    0.0,
           }


#childify filename (add _NXX if necessary)
filename = mst.childifyfilename(filename, ischild)

#cut and output input data as np arrays.
ztdat = gdt.cutalti(dhm, outpath+'parentdhm.asc',xmin,xmax,ymin,ymax,xres,yres)
bbdat = gdt.rasterandcuttlm(bb, outpath+'parentbb.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')

#shift the domain downwards
ztdat, origin_z = mst.shifttopodown(ztdat,ischild)
infodict['origin_z'] = origin_z

#map tlm bodenbedeckungs-kategorien to the palm definitions.
vegarr, pavarr, watarr, soilarr = mst.mapbbclasses(bbdat)

#create surface fraction array
sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)

#create static coordinates
x,y,nsurface_fraction,_,_,_,_,_,_ = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)
if flags[2] == 1:
    _,_,_,nvegetation_pars,_,_,_,_,_ =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)
if flags[3] == 1:
    _,_,_,_,nalbedo_pars,_,_,_,_ = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)

#create dataarrays
zt = mst.createDataArrays(ztdat,['y','x'],[y,x])
vegetation_type = mst.createDataArrays(vegarr,['y','x'],[y,x])
pavement_type = mst.createDataArrays(pavarr,['y','x'],[y,x])
water_type = mst.createDataArrays(watarr,['y','x'],[y,x])
soil_type = mst.createDataArrays(soilarr,['y','x'],[y,x])
surface_fraction = mst.createDataArrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
if flags[2] == 1:
    vegetation_pars =  mst.createDataArrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
if flags[3] == 1:
    albedo_pars =  mst.createDataArrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])


#set needed attributes to the data arrays
mst.setNeededAttributes(zt, 'zt')
mst.setNeededAttributes(vegetation_type,'vegetation_type')
mst.setNeededAttributes(pavement_type,'pavement_type')
mst.setNeededAttributes(water_type,'water_type')
mst.setNeededAttributes(soil_type,'soil_type')
mst.setNeededAttributes(surface_fraction,'surface_fraction')

#assemble Dataset
static = xr.Dataset()
static['zt'] = zt
static['vegetation_type'] = vegetation_type
static['water_type'] = water_type
static['soil_type'] = soil_type
static['pavement_type'] = pavement_type
static['surface_fraction'] = surface_fraction

#set global attributes
mst.setGlobalAttributes(static,infodict)

#output the static file
encodingdict = {'x':                {'dtype': 'float32'}, 
                'y':                {'dtype': 'float32'},
                'zt':               {'dtype': 'float32'},
                'vegetation_type':  {'dtype': 'int8'},
                'water_type':       {'dtype': 'int8'},
                'soil_type':        {'dtype': 'int8'},
                'pavement_type':    {'dtype': 'int8'},
                'surface_fraction': {'dtype': 'float32'},
                'nsurface_fraction':{'dtype': 'float32'}}
if flags[2] == 1:
    encodingdict['vegetation_pars'] = {'dtype':'float32'}
if flags[3] == 1:
    encodingdict['albedo_pars'] = {'dtype':'float32'}

mst.outputstaticfile(static,outpath+filename, encodingdict)

if cutorthoimg == True:
    gdt.cutortho(ortho, outpath+filename+'_ortho.tif', xmin,xmax,ymin,ymax,xres,yres)



#%%#######################################################
## This section creates the parent static file.

#assign variables:
ischild = ischild1 #Child id. this here is not a child, i.e. parent. 
xmin = xmin1 #in LV03 Koordinaten, lower left corner
xmax = xmax1
ymin = ymin1 #in LV03 Koordinaten, lower left corner
ymax = ymax1
xres = xres1
yres = xres1

infodict = {'version':           1,
            'palm_version':      6.0,
            'origin_z':          0.0, #is changed further below
            'origin_y':          ymin,
            'origin_x':          xmin,
            'origin_lat':        gdt.lv95towgs84(xmin+2000000,ymin+1000000)[1],
            'origin_lon':        gdt.lv95towgs84(xmin+2000000,ymin+1000000)[0],
            'origin_time':       origin_time,
            'rotation_angle':    0.0,
           }


#childify filename (add _NXX if necessary)
filename = mst.childifyfilename(filename, ischild)

#cut and output input data as np arrays.
ztdat = gdt.cutalti(dhm, outpath+'child1dhm.asc',xmin,xmax,ymin,ymax,xres,yres)
bbdat = gdt.rasterandcuttlm(bb, outpath+'child1bb.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')

#shift the domain downwards
ztdat, origin_z = mst.shifttopodown(ztdat,ischild,shift=origin_z)
infodict['origin_z'] = origin_z

#map tlm bodenbedeckungs-kategorien to the palm definitions.
vegarr, pavarr, watarr, soilarr = mst.mapbbclasses(bbdat)

#create surface fraction array
sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)

#create static coordinates
x,y,nsurface_fraction,_,_,_,_,_,_ = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)
if flags[2] == 1:
    _,_,_,nvegetation_pars,_,_,_,_,_ =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)
if flags[3] == 1:
    _,_,_,_,nalbedo_pars,_,_,_,_ = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)

#create dataarrays
zt = mst.createDataArrays(ztdat,['y','x'],[y,x])
vegetation_type = mst.createDataArrays(vegarr,['y','x'],[y,x])
pavement_type = mst.createDataArrays(pavarr,['y','x'],[y,x])
water_type = mst.createDataArrays(watarr,['y','x'],[y,x])
soil_type = mst.createDataArrays(soilarr,['y','x'],[y,x])
surface_fraction = mst.createDataArrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
if flags[2] == 1:
    vegetation_pars =  mst.createDataArrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
if flags[3] == 1:
    albedo_pars =  mst.createDataArrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])


#set needed attributes to the data arrays
mst.setNeededAttributes(zt, 'zt')
mst.setNeededAttributes(vegetation_type,'vegetation_type')
mst.setNeededAttributes(pavement_type,'pavement_type')
mst.setNeededAttributes(water_type,'water_type')
mst.setNeededAttributes(soil_type,'soil_type')
mst.setNeededAttributes(surface_fraction,'surface_fraction')

#assemble Dataset
static = xr.Dataset()
static['zt'] = zt
static['vegetation_type'] = vegetation_type
static['water_type'] = water_type
static['soil_type'] = soil_type
static['pavement_type'] = pavement_type
static['surface_fraction'] = surface_fraction

#set global attributes
mst.setGlobalAttributes(static,infodict)

#output the static file
encodingdict = {'x':                {'dtype': 'float32'}, 
                'y':                {'dtype': 'float32'},
                'zt':               {'dtype': 'float32'},
                'vegetation_type':  {'dtype': 'int8'},
                'water_type':       {'dtype': 'int8'},
                'soil_type':        {'dtype': 'int8'},
                'pavement_type':    {'dtype': 'int8'},
                'surface_fraction': {'dtype': 'float32'},
                'nsurface_fraction':{'dtype': 'float32'}}
if flags[2] == 1:
    encodingdict['vegetation_pars'] = {'dtype':'float32'}
if flags[3] == 1:
    encodingdict['albedo_pars'] = {'dtype':'float32'}

mst.outputstaticfile(static,outpath+filename, encodingdict)

if cutorthoimg == True:
    gdt.cutortho(ortho, outpath+filename+'_ortho.tif', xmin,xmax,ymin,ymax,xres,yres)



#%% finishing actions



print('Setup the following parameters in the namelists:\n'+
      'Parent Domain'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx0-1))+'/'+str(int(ny0-1))+'/'+str(int(nz0))+
      '\t'+str(xres0)+'/'+str(yres0)+'/'+str(zres0)+'\n')
      
print('Child Domain 1'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx1-1))+'/'+str(int(ny1-1))+'/'+str(int(nz1))+
      '\t'+str(xres1)+'/'+str(yres1)+'/'+str(zres1) +
      '\nNest 1 llx-Position Coordinates for &nesting_parameters (x,y): '+str(llx1)+', '+str(lly1)+'\n')

if totalnumberofdomains>=2:
    print('Child Domain 2'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx2-1))+'/'+str(int(ny2-1))+'/'+str(int(nz2))+
          '\t'+str(xres2)+'/'+str(yres2)+'/'+str(zres2) +
          '\nNest 2 llx-Position Coordinates for &nesting_parameters (x,y): '+str(llx2)+', '+str(lly2)+'\n\n')


cellcount0=nx0*ny0*nz0
totcells=cellcount0
if totalnumberofdomains>=2:
    cellcount1=nx1*ny1*nz1
    totcells+=cellcount1
if totalnumberofdomains>=3:
    cellcount2=nx2*ny2*nz2
    totcells+=cellcount2
print('Total cells: '+str(totcells))
print('Cells Parent: '+str(cellcount0)+'\t\t'+str(np.round(cellcount0/totcells*100,2))+'%')
if totalnumberofdomains>=2:
    print('Cells Child1: '+str(cellcount1)+'\t\t'+str(np.round(cellcount1/totcells*100,2))+'%')
if totalnumberofdomains>=3:
    print('Cells Child2: '+str(cellcount2)+'\t'+str(np.round(cellcount2/totcells*100,2))+'%')












