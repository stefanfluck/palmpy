"""
create static files just using dhm and tlm bb
"""
import xarray as xr
from pathlib import Path
import sys
import configparser as cfp

modulepath = str(Path.home() / 'Documents' / 'Python Scripts' / 'ZAV-PALM-Scripts')
if modulepath not in sys.path:
    sys.path.append(modulepath)
    
import palmpy.staticcreation.geodatatools as gdt
import palmpy.staticcreation.makestatictools as mst
    
# from palmpy.staticcreation.geodatatools import *
# from palmpy.staticcreation.makestatictools import *

#%% setup
filenames =   'wepf_static'
totalnumberofdomains = 2
flags = (1,1,0,0,0)  # ( zt, TLMBBtypes, vegetation_pars, albedo_pars, treeraster)
origin_time = '2019-08-01 12:00:00 +02'

#GEODATA FILES
dhm = "E:\\Dokumente\\Bibliothek\\Meteorology\\Geodaten\\zrh_lszh_winti\\swissALTI3D2018.tif"
bb = "E:\\Dokumente\\Bibliothek\\Meteorology\\Geodaten\\zrh_lszh_winti\\tlm\\swissTLM3D_2019_tlm_bodenbedeckung\\bb.shp"


#parent
ischild0 =          0
xmin0    =   684221.0
xmax0    =   690621.0
ymin0    =   255833.0
ymax0    =   262233.0     
zmax0    =     3200.0
xres0    =       50.0
yres0    =       50.0
zres0    =       50.0
nx0      =  (xmax0-xmin0)/xres0
ny0      =  (ymax0-ymin0)/yres0
nz0      =  zmax0/zres0
#parentchecks
mst.checknxyzvalid(nx0,ny0,nz0)

#child 1
ischild1 =          1
xmin1 =      686221.0
xmax1 =      688621.0
ymin1 =      257833.0 
ymax1 =      260233.0
zmax1    =      600.0
xres1 =          10.0
yres1 =          10.0
zres1 =          10.0
nx1      =  (xmax1-xmin1)/xres1
ny1      =  (ymax1-ymin1)/yres1
nz1      =  zmax1/zres1
llx1  =   xmin1-xmin0
lly1  =   ymin1-ymin0
#childchecks
mst.checknxyzvalid(nx1,ny1,nz1)
mst.checknestcoordsvalid(xres0,xres1,llx1,lly1)


print('Setup the following parameters in the namelists:\n'+
      'Parent Domain'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx0-1))+'/'+str(int(ny0-1))+'/'+str(int(nz0))+
      '\t'+str(int(xres0))+'/'+str(int(yres0))+'/'+str(int(zres0))+'\n'+
      'Child Domain 1'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx1-1))+'/'+str(int(ny1-1))+'/'+str(int(nz1))+
      '\t'+str(int(xres1))+'/'+str(int(yres1))+'/'+str(int(zres1))      )



#%%#######################################################
## This section creates the parent static file.

#settings:
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




#------------


#childify filename (add _NXX if necessary)
filename = mst.childifyfilename(filename, ischild)

#cut and output input data as np arrays.
ztdat = gdt.cutalti(dhm, 'parentdhm.asc',xmin,xmax,ymin,ymax,xres,yres)
bbdat = gdt.rasterandcuttlm(bb, 'parentbb.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')

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

mst.outputstaticfile(static,filename, encodingdict)





#%%#######################################################
## This section creates the parent static file.

#settings:
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


#------------------------


#childify filename (add _NXX if necessary)
filename = mst.childifyfilename(filename, ischild)

#cut and output input data as np arrays.
ztdat = gdt.cutalti(dhm, 'childdhm.asc',xmin,xmax,ymin,ymax,xres,yres)
bbdat = gdt.rasterandcuttlm(bb, 'childbb.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')

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

mst.outputstaticfile(static,filename, encodingdict)













