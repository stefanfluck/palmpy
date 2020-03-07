"""
create static files just using dhm and tlm bb

TODO: make it so an infinite number of nests can be used. use lists for every parameter instead of 
      laufnummer-variable names and provide indexes. 


"""
import xarray as xr
from pathlib import Path
import sys
import os
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

origin_time = '2019-06-07 12:00:00 +02'
cutorthoimg = True  # provide orthoimages for parent and child domains

#GEODATA FILES (if not available, write None)
ortho = "C:\\Users\\stefa\\Desktop\\preprocessed_shp\\swissimage2.5cutlarger.tif"
dhm = "C:\\Users\\stefa\\Desktop\\preprocessed_shp\\swissALTI3Dcut.tif"
bb = "C:\\Users\\stefa\\Desktop\\preprocessed_shp\\yverdoncut_bb.shp"
resolvedforestshp = 'C:\\Users\\stefa\\Desktop\\preprocessed_shp\\yverdoncut_bb_waldonly.shp'
treerowsshp =       'C:\\Users\\stefa\\Desktop\\preprocessed_shp\\yverdoncut_breihe_mod_puff.shp'
singletreesshp =    'C:\\Users\\stefa\\Desktop\\preprocessed_shp\\yverdoncut_ebgeb_mod_puff.shp'
pavementareas =     'C:\\Users\\stefa\\Desktop\\preprocessed_shp\\yverdoncut_strasse_vkareal_eisenbahn_versflaechen.shp'


#OUTPUT
subdir_rasteredshp = str(Path.home() / 'Desktop' / 'preprocessed_shp' / 'rasteredshp')+'\\' #where rastered shp shall be saved
outpath = str(Path.home() / 'Desktop' / 'yverdon_out')+'\\' #where the staticfile shall be saved

#Point of Interest
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

flags0 = {'doterrain':       True,
          'dotlmbb':         True,
          'dostreetsbb':     True,
          'dolad':           False, #for now: resolved tree file, treerows file and singletree file needed
          'dobuildings2d':   False,
          'dobuildings3d':   False,
          'dovegpars':       False,
          'doalbedopars':    False,
          'dostreettypes':   False
          }

##################### child 1 ###########################
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

#LAD PARAMETERS CHILD 1
lai_forest1 = 8; lai_breihe1 = 10; lai_ebgebu1 = 8;
a_forest1 = 2;   b_forest1 = 1.2
a_breihe1 = 1.3; b_breihe1 = 1.1
a_ebgebu1 = 4;   b_ebgebu1 = 2

flags1 = {'doterrain':       True,
          'dotlmbb':         True,
          'dostreetsbb':     True,
          'dolad':           True, #for now: resolved tree file, treerows file and singletree file needed
          'dobuildings2d':   False,
          'dobuildings3d':   False,
          'dovegpars':       False,
          'doalbedopars':    False,
          'dostreettypes':   False
          }

##################### child 2 ###########################
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

#LAD PARAMETERS CHILD 2
lai_forest2 = 8; lai_breihe2 = 10; lai_ebgebu2 = 8;
a_forest2 = 2;   b_forest2 = 1.2
a_breihe2 = 1.3; b_breihe2 = 1.1
a_ebgebu2 = 4;   b_ebgebu2 = 2

flags2 = {'doterrain':       True,
          'dotlmbb':         True,
          'dostreetsbb':     True,
          'dolad':           True, #for now: resolved tree file, treerows file and singletree file needed
          'dobuildings2d':   False,
          'dobuildings3d':   False,
          'dovegpars':       False,
          'doalbedopars':    False,
          'dostreettypes':   False
          }

#%%#######################################################
## This section creates the parent static file.

#assign variables:
filename = filenames
ischild = ischild0 #Child id. this here is not a child, i.e. parent. 
flags = flags0

xmin = xmin0 #in LV03 Koordinaten, lower left corner
xmax = xmax0
ymin = ymin0 #in LV03 Koordinaten, lower left corner
ymax = ymax0
xres = xres0
yres = yres0
zres = zres0

if flags['dolad'] == True:
    lai_forest = lai_forest0; lai_breihe = lai_breihe0; lai_ebgebu = lai_ebgebu0
    a_forest = a_forest0; b_forest = b_forest0
    a_breihe = a_breihe0; b_breihe = b_breihe0
    a_ebgebu = a_ebgebu0; b_ebgebu = b_ebgebu0


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

#### cut orthoimage if specified above.
if cutorthoimg == True:
    gdt.cutortho(ortho, outpath+filename+'_ortho.tif', xmin,xmax,ymin,ymax,xres,yres)

##### treat terrain
if flags['doterrain'] == True:
    ztdat = gdt.cutalti(dhm, outpath+'dhm'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres)
    ztdat, origin_z = mst.shifttopodown(ztdat,ischild) #shift the domain downwards
    infodict['origin_z'] = origin_z

##### treat tlm-bb bulk parametrization
if flags['dotlmbb'] == True:
    bbdat = gdt.rasterandcuttlm(bb, outpath+'bb'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
    vegarr, pavarr, watarr, soilarr = mst.mapbbclasses(bbdat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
    
    if flags['dostreetsbb'] == True:
        paved = gdt.rasterandcuttlm(pavementareas, outpath+'pavement'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
        vegarr = np.where( paved[:,:] != 0 , mst.fillvalues['vegetation_type'], vegarr[:,:])
        watarr = np.where( paved[:,:] != 0 , mst.fillvalues['water_type'], watarr[:,:])
        pavarr = paved
        pavarr = np.where ( pavarr[:,:] != 0, 1, mst.fillvalues['pavement_type']) #TODO: mit einem map dict auch pavements richtig klassifizieren.
    #create surface fraction array
    sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)

##### treat LAD
if flags['dolad'] == True:
    try:
        os.mkdir(subdir_rasteredshp)
    except:
        pass    
    
    resforesttop = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforesttop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resforestbot = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resforestid = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resbreihetop = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihentop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resbreihebot = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resbreiheid = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resebgebtop = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebtop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resebgebbot = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resebgebid = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    
    canopyheight = np.maximum.reduce([resforesttop, resbreihetop, resebgebtop])
    canopybottom = np.maximum.reduce([resforestbot, resbreihebot, resebgebbot])
    canopyid = np.maximum.reduce([resforestid, resbreiheid, resebgebid])
    
    #create arrays for alpha and beta and reduce to one layer.
    resforesta = np.where(resforesttop[:,:] != 0, a_forest, resforesttop[:,:])     # alpha für forest
    resforestb = np.where(resforesttop[:,:] != 0, b_forest, resforesttop[:,:])     # beta für forest
    resbreihea = np.where(resbreihetop[:,:] != 0, a_breihe, resbreihetop[:,:])     # alpha für baumreihe
    resbreiheb = np.where(resbreihetop[:,:] != 0, b_breihe, resbreihetop[:,:])     # beta für baumreihe
    resebgeba = np.where(resebgebtop[:,:] != 0, a_ebgebu, resebgebtop[:,:])        # alpha für ebgeb
    resebgebb = np.where(resebgebtop[:,:] != 0, b_ebgebu, resebgebtop[:,:])        # beta für ebgeb
    canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
    canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
    
    #create an LAI array
    laiforest = np.where(resforesttop[:,:] != 0, lai_forest, resforesttop[:,:])
    laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe, resbreihetop[:,:])
    laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu, resebgebtop[:,:])        
    lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
    
    maxtreeheight = np.max(canopyheight) #evaluate maximum tree height for zlad array generation
    
    zlad= mst.createzlad(maxtreeheight, zres) #create zlad array
    ladarr = np.ones((len(zlad), canopyheight.shape[0], canopyheight.shape[1]))*mst.fillvalues['tree_data'] #create empty lad array
    
    chdztop = np.round(canopyheight/zres,0).astype(int)
    chidxtop = np.where( (chdztop[:,:]==0), -9999, chdztop[:,:]) #index of zlad height that needs to be filled
    chdzbot = np.round(canopybottom/zres,0).astype(int)
    chidxbot = np.where( (chdzbot[:,:]==0), 0, chdzbot[:,:]) #index of zlad height that needs to be filled
    
    #create actual lad array
    from scipy.stats import beta
    for i in range(ladarr.shape[1]):
        for j in range(ladarr.shape[2]):
            # if not np.isnan(chidxtop[i,j]):
            if not chidxtop[i,j] == -9999:
                botindex = int(chidxbot[i,j])
                topindex = int(chidxtop[i,j])+1
                pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[i,j],b=canbeta[i,j])
                ladarr[botindex:topindex,i,j] = pdf/pdf.max()*lai[i,j]/canopyheight[i,j]

    vegarr = np.where(canopyid[:,:] != 0, 3, vegarr[:,:])
    canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:])



######### create static netcdf file
static = xr.Dataset()
x,y = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[0:2]


#create coordinates, create data Array and then assign to static dataset and append the encodingdict.
if flags['doterrain'] == True:
    zt = mst.createDataArrays(ztdat,['y','x'],[y,x])
    mst.setNeededAttributes(zt, 'zt')
    static['zt'] = zt
if flags['dotlmbb'] == True:
    nsurface_fraction = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[2]
    vegetation_type = mst.createDataArrays(vegarr,['y','x'],[y,x])
    pavement_type = mst.createDataArrays(pavarr,['y','x'],[y,x])
    water_type = mst.createDataArrays(watarr,['y','x'],[y,x])
    soil_type = mst.createDataArrays(soilarr,['y','x'],[y,x])
    surface_fraction = mst.createDataArrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
    mst.setNeededAttributes(vegetation_type,'vegetation_type')
    mst.setNeededAttributes(pavement_type,'pavement_type')
    mst.setNeededAttributes(water_type,'water_type')
    mst.setNeededAttributes(soil_type,'soil_type')
    mst.setNeededAttributes(surface_fraction,'surface_fraction')
    static['vegetation_type'] = vegetation_type
    static['water_type'] = water_type
    static['soil_type'] = soil_type
    static['pavement_type'] = pavement_type
    static['surface_fraction'] = surface_fraction
if flags['dovegpars'] == True:
    nvegetation_pars =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[3]
    vegetation_pars =  mst.createDataArrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
if flags['doalbedopars'] == True:
    nalbedo_pars = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[4]
    albedo_pars =  mst.createDataArrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])
if flags['dolad'] == True:
    lad = mst.createDataArrays(ladarr,['zlad', 'y', 'x'], [zlad,y,x])
    mst.setNeededAttributes(lad, 'lad')
    static['lad'] = lad
    tree_id = mst.createDataArrays(canopyid, ['y','x'], [y,x])
    mst.setNeededAttributes(tree_id,'tree_id')
    static['tree_id'] = tree_id
# if flags['dobuildings2d'] == True:
#     continue



encodingdict = mst.setupencodingdict(flags)
mst.setGlobalAttributes(static,infodict) #set global attributes

mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file



#%%#######################################################
## This section creates the child 1 static file.

#assign variables:
filename = filenames
ischild = ischild1 #Child id. this here is not a child, i.e. parent. 
flags = flags1

xmin = xmin1 #in LV03 Koordinaten, lower left corner
xmax = xmax1
ymin = ymin1 #in LV03 Koordinaten, lower left corner
ymax = ymax1
xres = xres1
yres = yres1
zres = zres1

if flags['dolad'] == True:
    lai_forest = lai_forest1; lai_breihe = lai_breihe1; lai_ebgebu = lai_ebgebu1
    a_forest = a_forest1; b_forest = b_forest1
    a_breihe = a_breihe1; b_breihe = b_breihe1
    a_ebgebu = a_ebgebu1; b_ebgebu = b_ebgebu1


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

#### cut orthoimage if specified above.
if cutorthoimg == True:
    gdt.cutortho(ortho, outpath+filename+'_ortho.tif', xmin,xmax,ymin,ymax,xres,yres)

##### treat terrain
if flags['doterrain'] == True:
    ztdat = gdt.cutalti(dhm, outpath+'dhm'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres)
    ztdat, origin_z = mst.shifttopodown(ztdat,ischild,shift=origin_z) #shift the domain downwards
    infodict['origin_z'] = origin_z

##### treat tlm-bb bulk parametrization
if flags['dotlmbb'] == True:
    bbdat = gdt.rasterandcuttlm(bb, outpath+'bb'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
    vegarr, pavarr, watarr, soilarr = mst.mapbbclasses(bbdat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
    
    if flags['dostreetsbb'] == True:
        paved = gdt.rasterandcuttlm(pavementareas, outpath+'pavement'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
        vegarr = np.where( paved[:,:] != 0 , mst.fillvalues['vegetation_type'], vegarr[:,:])
        watarr = np.where( paved[:,:] != 0 , mst.fillvalues['water_type'], watarr[:,:])
        pavarr = paved
        pavarr = np.where ( pavarr[:,:] != 0, 1, mst.fillvalues['pavement_type']) #TODO: mit einem map dict auch pavements richtig klassifizieren.
    #create surface fraction array
    sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)

##### treat LAD
if flags['dolad'] == True:
    try:
        os.mkdir(subdir_rasteredshp)
    except:
        pass    
    
    resforesttop = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforesttop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resforestbot = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resforestid = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resbreihetop = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihentop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resbreihebot = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resbreiheid = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resebgebtop = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebtop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resebgebbot = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resebgebid = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    
    canopyheight = np.maximum.reduce([resforesttop, resbreihetop, resebgebtop])
    canopybottom = np.maximum.reduce([resforestbot, resbreihebot, resebgebbot])
    canopyid = np.maximum.reduce([resforestid, resbreiheid, resebgebid])
    
    #create arrays for alpha and beta and reduce to one layer.
    resforesta = np.where(resforesttop[:,:] != 0, a_forest, resforesttop[:,:])     # alpha für forest
    resforestb = np.where(resforesttop[:,:] != 0, b_forest, resforesttop[:,:])     # beta für forest
    resbreihea = np.where(resbreihetop[:,:] != 0, a_breihe, resbreihetop[:,:])     # alpha für baumreihe
    resbreiheb = np.where(resbreihetop[:,:] != 0, b_breihe, resbreihetop[:,:])     # beta für baumreihe
    resebgeba = np.where(resebgebtop[:,:] != 0, a_ebgebu, resebgebtop[:,:])        # alpha für ebgeb
    resebgebb = np.where(resebgebtop[:,:] != 0, b_ebgebu, resebgebtop[:,:])        # beta für ebgeb
    canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
    canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
    
    #create an LAI array
    laiforest = np.where(resforesttop[:,:] != 0, lai_forest, resforesttop[:,:])
    laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe, resbreihetop[:,:])
    laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu, resebgebtop[:,:])        
    lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
    
    maxtreeheight = np.max(canopyheight) #evaluate maximum tree height for zlad array generation
    
    zlad= mst.createzlad(maxtreeheight, zres) #create zlad array
    ladarr = np.ones((len(zlad), canopyheight.shape[0], canopyheight.shape[1]))*mst.fillvalues['tree_data'] #create empty lad array
    
    chdztop = np.round(canopyheight/zres,0).astype(int)
    chidxtop = np.where( (chdztop[:,:]==0), -9999, chdztop[:,:]) #index of zlad height that needs to be filled
    chdzbot = np.round(canopybottom/zres,0).astype(int)
    chidxbot = np.where( (chdzbot[:,:]==0), 0, chdzbot[:,:]) #index of zlad height that needs to be filled
    
    #create actual lad array
    from scipy.stats import beta
    for i in range(ladarr.shape[1]):
        for j in range(ladarr.shape[2]):
            # if not np.isnan(chidxtop[i,j]):
            if not chidxtop[i,j] == -9999:
                botindex = int(chidxbot[i,j])
                topindex = int(chidxtop[i,j])+1
                pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[i,j],b=canbeta[i,j])
                ladarr[botindex:topindex,i,j] = pdf/pdf.max()*lai[i,j]/canopyheight[i,j]

    vegarr = np.where(canopyid[:,:] != 0, 3, vegarr[:,:])
    canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:])



######### create static netcdf file
static = xr.Dataset()
x,y = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[0:2]


#create coordinates, create data Array and then assign to static dataset and append the encodingdict.
if flags['doterrain'] == True:
    zt = mst.createDataArrays(ztdat,['y','x'],[y,x])
    mst.setNeededAttributes(zt, 'zt')
    static['zt'] = zt
if flags['dotlmbb'] == True:
    nsurface_fraction = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[2]
    vegetation_type = mst.createDataArrays(vegarr,['y','x'],[y,x])
    pavement_type = mst.createDataArrays(pavarr,['y','x'],[y,x])
    water_type = mst.createDataArrays(watarr,['y','x'],[y,x])
    soil_type = mst.createDataArrays(soilarr,['y','x'],[y,x])
    surface_fraction = mst.createDataArrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
    mst.setNeededAttributes(vegetation_type,'vegetation_type')
    mst.setNeededAttributes(pavement_type,'pavement_type')
    mst.setNeededAttributes(water_type,'water_type')
    mst.setNeededAttributes(soil_type,'soil_type')
    mst.setNeededAttributes(surface_fraction,'surface_fraction')
    static['vegetation_type'] = vegetation_type
    static['water_type'] = water_type
    static['soil_type'] = soil_type
    static['pavement_type'] = pavement_type
    static['surface_fraction'] = surface_fraction
if flags['dovegpars'] == True:
    nvegetation_pars =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[3]
    vegetation_pars =  mst.createDataArrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
if flags['doalbedopars'] == True:
    nalbedo_pars = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[4]
    albedo_pars =  mst.createDataArrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])
if flags['dolad'] == True:
    lad = mst.createDataArrays(ladarr,['zlad', 'y', 'x'], [zlad,y,x])
    mst.setNeededAttributes(lad, 'lad')
    static['lad'] = lad
    tree_id = mst.createDataArrays(canopyid, ['y','x'], [y,x])
    mst.setNeededAttributes(tree_id,'tree_id')
    static['tree_id'] = tree_id
# if flags['dobuildings2d'] == True:
#     continue


encodingdict = mst.setupencodingdict(flags)
mst.setGlobalAttributes(static,infodict) #set global attributes

mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file



#%%#######################################################
## This section creates the child 2 static file.

#assign variables:
filename = filenames
ischild = ischild2 #Child id. this here is not a child, i.e. parent. 
flags = flags2

xmin = xmin2 #in LV03 Koordinaten, lower left corner
xmax = xmax2
ymin = ymin2 #in LV03 Koordinaten, lower left corner
ymax = ymax2
xres = xres2
yres = yres2
zres = zres2

if flags['dolad'] == True:
    lai_forest = lai_forest2; lai_breihe = lai_breihe2; lai_ebgebu = lai_ebgebu2
    a_forest = a_forest2; b_forest = b_forest2
    a_breihe = a_breihe2; b_breihe = b_breihe2
    a_ebgebu = a_ebgebu2; b_ebgebu = b_ebgebu2


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

#### cut orthoimage if specified above.
if cutorthoimg == True:
    gdt.cutortho(ortho, outpath+filename+'_ortho.tif', xmin,xmax,ymin,ymax,xres,yres)

##### treat terrain
if flags['doterrain'] == True:
    ztdat = gdt.cutalti(dhm, outpath+'dhm'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres)
    ztdat, origin_z = mst.shifttopodown(ztdat,ischild,shift=origin_z) #shift the domain downwards
    infodict['origin_z'] = origin_z

##### treat tlm-bb bulk parametrization
if flags['dotlmbb'] == True:
    bbdat = gdt.rasterandcuttlm(bb, outpath+'bb'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
    vegarr, pavarr, watarr, soilarr = mst.mapbbclasses(bbdat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
    
    if flags['dostreetsbb'] == True:
        paved = gdt.rasterandcuttlm(pavementareas, outpath+'pavement'+str(ischild)+'.asc',xmin,xmax,ymin,ymax,xres,yres, burnatt='OBJEKTART')
        vegarr = np.where( paved[:,:] != 0 , mst.fillvalues['vegetation_type'], vegarr[:,:])
        watarr = np.where( paved[:,:] != 0 , mst.fillvalues['water_type'], watarr[:,:])
        pavarr = paved
        pavarr = np.where ( pavarr[:,:] != 0, 1, mst.fillvalues['pavement_type']) #TODO: mit einem map dict auch pavements richtig klassifizieren.
    #create surface fraction array
    sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)

##### treat LAD
if flags['dolad'] == True:
    try:
        os.mkdir(subdir_rasteredshp)
    except:
        pass    
    
    resforesttop = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforesttop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resforestbot = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resforestid = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resbreihetop = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihentop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resbreihebot = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resbreiheid = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    resebgebtop = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebtop'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_TOP')
    resebgebbot = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebbot'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='HEIGHT_BOT')
    resebgebid = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebid'+str(ischild)+'.asc', 
                                    xmin, xmax, ymin, ymax, xres, yres, burnatt='ID')
    
    canopyheight = np.maximum.reduce([resforesttop, resbreihetop, resebgebtop])
    canopybottom = np.maximum.reduce([resforestbot, resbreihebot, resebgebbot])
    canopyid = np.maximum.reduce([resforestid, resbreiheid, resebgebid])
    
    #create arrays for alpha and beta and reduce to one layer.
    resforesta = np.where(resforesttop[:,:] != 0, a_forest, resforesttop[:,:])     # alpha für forest
    resforestb = np.where(resforesttop[:,:] != 0, b_forest, resforesttop[:,:])     # beta für forest
    resbreihea = np.where(resbreihetop[:,:] != 0, a_breihe, resbreihetop[:,:])     # alpha für baumreihe
    resbreiheb = np.where(resbreihetop[:,:] != 0, b_breihe, resbreihetop[:,:])     # beta für baumreihe
    resebgeba = np.where(resebgebtop[:,:] != 0, a_ebgebu, resebgebtop[:,:])        # alpha für ebgeb
    resebgebb = np.where(resebgebtop[:,:] != 0, b_ebgebu, resebgebtop[:,:])        # beta für ebgeb
    canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
    canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
    
    #create an LAI array
    laiforest = np.where(resforesttop[:,:] != 0, lai_forest, resforesttop[:,:])
    laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe, resbreihetop[:,:])
    laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu, resebgebtop[:,:])        
    lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
    
    maxtreeheight = np.max(canopyheight) #evaluate maximum tree height for zlad array generation
    
    zlad= mst.createzlad(maxtreeheight, zres) #create zlad array
    ladarr = np.ones((len(zlad), canopyheight.shape[0], canopyheight.shape[1]))*mst.fillvalues['tree_data'] #create empty lad array
    
    chdztop = np.round(canopyheight/zres,0).astype(int)
    chidxtop = np.where( (chdztop[:,:]==0), -9999, chdztop[:,:]) #index of zlad height that needs to be filled
    chdzbot = np.round(canopybottom/zres,0).astype(int)
    chidxbot = np.where( (chdzbot[:,:]==0), 0, chdzbot[:,:]) #index of zlad height that needs to be filled
    
    #create actual lad array
    from scipy.stats import beta
    for i in range(ladarr.shape[1]):
        for j in range(ladarr.shape[2]):
            # if not np.isnan(chidxtop[i,j]):
            if not chidxtop[i,j] == -9999:
                botindex = int(chidxbot[i,j])
                topindex = int(chidxtop[i,j])+1
                pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[i,j],b=canbeta[i,j])
                ladarr[botindex:topindex,i,j] = pdf/pdf.max()*lai[i,j]/canopyheight[i,j]

    vegarr = np.where(canopyid[:,:] != 0, 3, vegarr[:,:])
    canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:])


######### create static netcdf file
static = xr.Dataset()
x,y = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[0:2]


#create coordinates, create data Array and then assign to static dataset and append the encodingdict.
if flags['doterrain'] == True:
    zt = mst.createDataArrays(ztdat,['y','x'],[y,x])
    mst.setNeededAttributes(zt, 'zt')
    static['zt'] = zt
if flags['dotlmbb'] == True:
    nsurface_fraction = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[2]
    vegetation_type = mst.createDataArrays(vegarr,['y','x'],[y,x])
    pavement_type = mst.createDataArrays(pavarr,['y','x'],[y,x])
    water_type = mst.createDataArrays(watarr,['y','x'],[y,x])
    soil_type = mst.createDataArrays(soilarr,['y','x'],[y,x])
    surface_fraction = mst.createDataArrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
    mst.setNeededAttributes(vegetation_type,'vegetation_type')
    mst.setNeededAttributes(pavement_type,'pavement_type')
    mst.setNeededAttributes(water_type,'water_type')
    mst.setNeededAttributes(soil_type,'soil_type')
    mst.setNeededAttributes(surface_fraction,'surface_fraction')
    static['vegetation_type'] = vegetation_type
    static['water_type'] = water_type
    static['soil_type'] = soil_type
    static['pavement_type'] = pavement_type
    static['surface_fraction'] = surface_fraction
if flags['dovegpars'] == True:
    nvegetation_pars =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[3]
    vegetation_pars =  mst.createDataArrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
if flags['doalbedopars'] == True:
    nalbedo_pars = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres)[4]
    albedo_pars =  mst.createDataArrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])
if flags['dolad'] == True:
    lad = mst.createDataArrays(ladarr,['zlad', 'y', 'x'], [zlad,y,x])
    mst.setNeededAttributes(lad, 'lad')
    static['lad'] = lad
    tree_id = mst.createDataArrays(canopyid, ['y','x'], [y,x])
    mst.setNeededAttributes(tree_id,'tree_id')
    static['tree_id'] = tree_id
# if flags['dobuildings2d'] == True:
#     continue


encodingdict = mst.setupencodingdict(flags)
mst.setGlobalAttributes(static,infodict) #set global attributes

mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file




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












