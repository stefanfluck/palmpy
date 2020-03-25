"""
create static files just using dhm and tlm bb

TODO: make it so an infinite number of nests can be used. use lists for every parameter instead of 
      laufnummer-variable names and provide indexes. 


"""
import xarray as xr
from pathlib import Path
import sys
import os
from configparser import ConfigParser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

#%% Read config file
cfp = ConfigParser(allow_no_value=True) #

try:
    cfp.read(sys.argv[1])
except:
    print('no command line argument given. Using hardcoded config_file path in script.')
    cfp.read("C:\\Users\\Stefan Fluck\\Documents\\Python Scripts\\ZAV-PALM-Scripts\\example_scripts\\make_static\\make_static.ini")

modulepath = cfp.get('paths', 'modulepath')

# modulepath = str(Path.home() / 'Documents' / 'Python Scripts' / 'ZAV-PALM-Scripts')

if modulepath not in sys.path:
    sys.path.append(modulepath)
    
import palmpy.staticcreation.geodatatools as gdt
import palmpy.staticcreation.makestatictools as mst



#parse settings and paths
filenames = cfp.get('settings','casename', fallback='default')+'_static'
origin_time = cfp.get('settings', 'origin_time', fallback='2020-08-01 12:00:00 +02')
totaldomains = cfp.getint('settings', 'totaldomains', fallback=1)
cutorthoimg = cfp.getboolean('settings', 'cutorthoimg', fallback=False)
orthores = cfp.getfloat('settings', 'orthores', fallback=5.0)
rotationangle = cfp.getfloat('settings', 'rotationangle', fallback=0.0)
setvmag = cfp.getfloat('settings', 'set_vmag', fallback=1.0)

inputfilepath = cfp.get('paths', 'inputfilepath')
ortho = inputfilepath+cfp.get('paths', 'orthoimage')
dhm = inputfilepath+cfp.get('paths', 'dhm')
bb = inputfilepath+cfp.get('paths', 'bb')
resolvedforestshp = inputfilepath+cfp.get('paths', 'resolvedforest')
treerowsshp = inputfilepath+cfp.get('paths', 'treerows')
singletreesshp = inputfilepath+cfp.get('paths', 'singletrees')
pavementareas = inputfilepath+cfp.get('paths', 'pavementareas')
gebaeudefoots = inputfilepath+cfp.get('paths', 'gebaeudefoots')
crops = inputfilepath+cfp.get('paths', 'crops')
streetsonly = inputfilepath+cfp.get('paths', 'streetsonly')
subdir_rasteredshp = cfp.get('paths', 'subdir_rasterdata')
outpath = cfp.get('paths', 'outpath')

try:
    os.mkdir(outpath)
    print('create outpath')
except:
    pass
try:
    os.mkdir(subdir_rasteredshp)
    print('create subdir for rastered data:')
except:
    pass    

#initialize all variable lists
ischild = totaldomains*[None];          xmin = totaldomains*[None]
ymin = totaldomains*[None];             zmax = totaldomains*[None] 
xres = totaldomains*[None];             yres = totaldomains*[None]
zres = totaldomains*[None];             xlen = totaldomains*[None]
xmax = totaldomains*[None];             ymax = totaldomains*[None]
nx = totaldomains*[None];               ny = totaldomains*[None]
ylen = totaldomains*[None];             nz = totaldomains*[None]
doterrain = totaldomains*[None];        bulkvegclass = totaldomains*[None]
dotlmbb = totaldomains*[None];          dostreetsbb = totaldomains*[None]
docropfields = totaldomains*[None];     dolad = totaldomains*[None]
dobuildings_2d = totaldomains*[None];   dobuildings_3d = totaldomains*[None]
dovegpars = totaldomains*[None];        doalbedopars = totaldomains*[None]
dostreettypes = totaldomains*[None];    lai_forest = totaldomains*[None]
lai_breihe = totaldomains*[None];       lai_ebgebu = totaldomains*[None]
a_forest = totaldomains*[None];         b_forest = totaldomains*[None]
a_breihe = totaldomains*[None];         b_breihe = totaldomains*[None]
a_ebgebu = totaldomains*[None];         b_ebgebu = totaldomains*[None]
llx = totaldomains*[0.0];               lly = totaldomains*[0.0]
flags = totaldomains*[{}]

for i in range(0,len(cfp.sections())):
    section = cfp.sections()[i]
    if section.split('_')[0] == 'domain':
        index = int(section.split('_')[1])
        print('\n'+section)
        ischild[index] = cfp.getint(section, 'ischild', fallback=0)
        xlen[index] = cfp.getfloat(section, 'xlen', fallback=0.0)
        ylen[index] = cfp.getfloat(section, 'ylen', fallback=0.0)
        xmin[index] = cfp.getfloat(section, 'xmin', fallback=0.0)
        ymin[index] = cfp.getfloat(section, 'ymin', fallback=0.0)
        zmax[index] = cfp.getfloat(section, 'zmax', fallback=0.0)
        xres[index] = cfp.getfloat(section, 'xres', fallback=0.0)
        yres[index] = cfp.getfloat(section, 'yres', fallback=0.0)
        zres[index] = cfp.getfloat(section, 'zres', fallback=0.0)
        xmax[index] = xmin[index]+xlen[index]
        ymax[index] = ymin[index]+ylen[index]
        nx[index] = xlen[index]/xres[index]
        ny[index] = ylen[index]/yres[index]
        nz[index] = zmax[index]/zres[index]
        if index > 0:
            llx[index] = xmin[index]-xmin[0]
            lly[index] = ymin[index]-ymin[0]
        doterrain[index] = cfp.getboolean(section,'doterrain', fallback=False)
        dotlmbb[index] = cfp.getboolean(section,'dotlmbb', fallback=False)
        dostreetsbb[index] = cfp.getboolean(section,'dostreetsbb', fallback=False)
        docropfields[index] = cfp.getboolean(section,'docropfields', fallback=False)
        dolad[index] = cfp.getboolean(section,'dolad', fallback=False)
        dobuildings_2d[index] = cfp.getboolean(section,'dobuildings_2d', fallback=False)
        dobuildings_3d[index] = cfp.getboolean(section,'dobuildings_3d', fallback=False)
        dovegpars[index] = cfp.getboolean(section,'dovegpars', fallback=False)
        doalbedopars[index] = cfp.getboolean(section,'doalbedopars', fallback=False)
        dostreettypes[index] = cfp.getboolean(section,'dostreettypes', fallback=False)
        
        bulkvegclass[index] = cfp.getint(section,'bulkvegclass', fallback=None)
        lai_forest[index] = cfp.getfloat(section,'lai_forest', fallback=None)
        lai_breihe[index] = cfp.getfloat(section,'lai_breihe', fallback=None)
        lai_ebgebu[index] = cfp.getfloat(section,'lai_ebgebu', fallback=None)
        a_forest[index] = cfp.getfloat(section,'a_forest', fallback=None)
        b_forest[index] = cfp.getfloat(section,'b_forest', fallback=None)
        a_breihe[index] = cfp.getfloat(section,'a_breihe', fallback=None)
        b_breihe[index] = cfp.getfloat(section,'b_breihe', fallback=None)
        a_ebgebu[index] = cfp.getfloat(section,'a_ebgebu', fallback=None)
        b_ebgebu[index] = cfp.getfloat(section,'b_ebgebu', fallback=None)
        
        mst.checknxyzvalid(nx[index],ny[index],nz[index])                     
        if index > 0:
            mst.checknestcoordsvalid(xres[index-1],xres[index],llx[index],lly[index])    
        
        flags[index] = {'doterrain':       doterrain[index],
                        'dotlmbb':         dotlmbb[index],
                        'dostreetsbb':     dostreetsbb[index], #requires dotlmbb = True
                        'docropfields':    docropfields[index], #requires dotlmbb = true
                        'dolad':           dolad[index], #for now: resolved tree file, treerows file and singletree file needed, requires dotlmbb=true
                        'dobuildings2d':   dobuildings_2d[index],
                        'dobuildings3d':   dobuildings_3d[index],
                        'dovegpars':       dovegpars[index],
                        'doalbedopars':    doalbedopars[index],
                        'dostreettypes':   dostreettypes[index]}
        
        
#visualize domain boundaries
gdt.cutortho(ortho, subdir_rasteredshp+filenames+'_baseortho.tif', 
             xmin[0],xmax[0],ymin[0],ymax[0],orthores,orthores)

fig = plt.figure(figsize=(12,12))
ax = fig.gca()
img = plt.imread(subdir_rasteredshp+filenames+'_baseortho.tif')
ax.imshow(img)

for a in range(1,totaldomains):
    rect = patches.Rectangle((llx[a]/orthores,(ylen[0]-lly[a]-ylen[a])/orthores), 
                          xlen[a]/orthores,ylen[a]/orthores, 
                          linewidth=3, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
plt.savefig(outpath+'domainoverview.png')






#%%generation with for loop
for i in range(totaldomains):
    
    infodict = {'version':           1,
                'palm_version':      6.0,
                'origin_z':          0.0, #is changed further below
                'origin_y':          ymin[i],
                'origin_x':          xmin[i],
                'origin_lat':        gdt.lv95towgs84(xmin[i]+2000000,ymin[i]+1000000)[1],
                'origin_lon':        gdt.lv95towgs84(xmin[i]+2000000,ymin[i]+1000000)[0],
                'origin_time':       origin_time,
                'rotation_angle':    rotationangle}
    
    #childify filename (add _NXX if necessary)
    filename = mst.childifyfilename(filenames, ischild[i])
    
    #### cut orthoimage if specified above.
    if cutorthoimg == True:
        gdt.cutortho(ortho, subdir_rasteredshp+filename+'_ortho.tif', xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
    
    ##### treat terrain
    if flags[i]['doterrain'] == True:
        ztdat = gdt.cutalti(dhm, subdir_rasteredshp+'dhm'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
        if ischild[i]==0:
            ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i]) #shift the domain downwards
        else:
            ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i],shift=origin_z) #shift the domain downwards
        infodict['origin_z'] = origin_z
    
    ##### treat tlm-bb bulk parametrization
    if flags[i]['dotlmbb'] == True:
        bbdat = gdt.rasterandcuttlm(bb, subdir_rasteredshp+'bb'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt='OBJEKTART')
        vegarr, pavarr, watarr = mst.mapbbclasses(bbdat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
        
    ##### BLOCK FOR MODIFICATIONS TO VEGPARS AND ALBEDOPARS
    
        # vegpars = mst.createparsarrays(bbdat.shape[1], bbdat.shape[0])[0]
        # albedopars = mst.createparsarrays(bbdat.shape[1], bbdat.shape[0])[5]
    
        # vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, bbdat, 9, 1, -1)
        # vegpars = mst.modifyparsarray(vegpars,9,2093,bbdat,9)
        # vegpars = mst.modifyparsarray(vegpars,11,0,bbdat,9)
    
    ##### treat LAD
        if flags[i]['dolad'] == True:
            
            resforesttop = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforesttop'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
            resforestbot = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestbot'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
            resforestid = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestid'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            resbreihetop = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihentop'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
            resbreihebot = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenbot'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
            resbreiheid = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenid'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            resebgebtop = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebtop'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
            resebgebbot = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebbot'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
            resebgebid = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebid'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            
            canopyheight = np.maximum.reduce([resforesttop, resbreihetop, resebgebtop])
            canopybottom = np.maximum.reduce([resforestbot, resbreihebot, resebgebbot])
            canopyid = np.maximum.reduce([resforestid, resbreiheid, resebgebid])
            
            #create arrays for alpha and beta and reduce to one layer.
            resforesta = np.where(resforesttop[:,:] != 0, a_forest[i], resforesttop[:,:])     # alpha für forest
            resforestb = np.where(resforesttop[:,:] != 0, b_forest[i], resforesttop[:,:])     # beta für forest
            resbreihea = np.where(resbreihetop[:,:] != 0, a_breihe[i], resbreihetop[:,:])     # alpha für baumreihe
            resbreiheb = np.where(resbreihetop[:,:] != 0, b_breihe[i], resbreihetop[:,:])     # beta für baumreihe
            resebgeba = np.where(resebgebtop[:,:] != 0, a_ebgebu[i], resebgebtop[:,:])        # alpha für ebgeb
            resebgebb = np.where(resebgebtop[:,:] != 0, b_ebgebu[i], resebgebtop[:,:])        # beta für ebgeb
            canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
            canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
            
            #create an LAI array
            laiforest = np.where(resforesttop[:,:] != 0, lai_forest[i], resforesttop[:,:])
            laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe[i], resbreihetop[:,:])
            laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu[i], resebgebtop[:,:])        
            lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
            
            maxtreeheight = np.max(canopyheight) #evaluate maximum tree height for zlad array generation
            
            zlad= mst.createzlad(maxtreeheight, zres[i]) #create zlad array
            ladarr = np.ones((len(zlad), canopyheight.shape[0], canopyheight.shape[1]))*mst.fillvalues['tree_data'] #create empty lad array
            
            chdztop = np.where(canopyheight[:,:]==-9999., canopyheight[:,:], np.round(canopyheight/zres[i],0).astype(int)) #TODO check if needs canopyheight[:,:] in else statement
            chidxtop = np.where( (chdztop[:,:]==0), -9999, chdztop[:,:]) #index of zlad height that needs to be filled
            chdzbot = np.where(canopybottom[:,:]==-9999., canopybottom[:,:], np.round(canopybottom/zres[i],0).astype(int))
            chidxbot = np.where( (chdzbot[:,:]==0), 0, chdzbot[:,:]) #index of zlad height that needs to be filled
            
            #create actual lad array
            from scipy.stats import beta
            for k in range(ladarr.shape[1]):
                for j in range(ladarr.shape[2]):
                    # if not np.isnan(chidxtop[k,j]):
                    if not chidxtop[k,j] == -9999:
                        botindex = int(chidxbot[k,j])
                        topindex = int(chidxtop[k,j])+1
                        pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[k,j],b=canbeta[k,j])
                        ladarr[botindex:topindex,k,j] = pdf/pdf.max()*lai[k,j]/canopyheight[k,j]
        
            vegarr = np.where((canopyid[:,:] != -9999) & (watarr[:,:] == -127), 3, vegarr[:,:])
            canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:])
        
        vegarr = np.where( (vegarr[:,:]==-127) & (watarr[:,:]==-127) & (pavarr[:,:]==-127), bulkvegclass[i], vegarr[:,:]) #fill unassigned vegetation types to bare soil.
        
        if flags[i]['docropfields'] == True:
            cropheight = gdt.rasterandcuttlm(crops, subdir_rasteredshp+'felder'+str(ischild[i])+'.asc', 
                                           xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
            vegarr = np.where( (vegarr[:,:]==bulkvegclass[i]) & (cropheight[:,:] != -9999), 2, vegarr[:,:])
        
        
        if flags[i]['dostreetsbb'] == True:
            paved = gdt.rasterandcuttlm(pavementareas, subdir_rasteredshp+'pavement'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt='OBJEKTART')
            vegarr = np.where( paved[:,:] != -9999 , mst.fillvalues['vegetation_type'], vegarr[:,:])
            watarr = np.where( paved[:,:] != -9999 , mst.fillvalues['water_type'], watarr[:,:])
            pavarr = paved
            pavarr = np.where ( pavarr[:,:] != -9999, 1, mst.fillvalues['pavement_type']) #TODO: mit einem map dict auch pavements richtig klassifizieren.
        #create surface fraction array
        soilarr = mst.makesoilarray(vegarr,pavarr)
        sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr)
        
    if flags[i]['dobuildings2d'] == True:  
        gebhoehe = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudehoehe'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
        gebid = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeid'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
        gebtyp = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetyp'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='BLDGTYP')
        gebtyp = np.where((gebtyp[:,:]==-9999.), mst.fillvalues['building_type'], gebtyp[:,:])
    
    if flags[i]['dobuildings3d'] == True:
        gebtop = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetop'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
        gebbot = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudebot'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
        z = mst.createzcoord(zmax[i],zres[i])
        bldarr = np.ones((len(z), gebtop.shape[0], gebtop.shape[1]))*np.byte(0)
        
        bhdztop = np.where(gebtop[:,:]==-9999., gebtop[:,:], np.round(gebtop[:,:]/zres[i],0).astype(int))
        bhidxtop = np.where( (bhdztop[:,:]==0), -9999, bhdztop[:,:]) #index of zlad height that needs to be filled
        bhdzbot = np.where(gebbot[:,:]==-9999., gebbot[:,:], np.round(gebbot[:,:]/zres[i],0).astype(int))
        bhidxbot = np.where( (bhdzbot[:,:]==0), 0, bhdzbot[:,:]) #index of zlad height that needs to be filled
        
        for k in range(bldarr.shape[1]):
               for j in range(bldarr.shape[2]):
                   # if not np.isnan(chidxtop[k,j]):
                   if not bhidxtop[k,j] == -9999:
                       botindex = int(bhidxbot[k,j])
                       topindex = int(bhidxtop[k,j])+1
                       bldarr[botindex:topindex,k,j] = np.byte(1)
        
        gebid = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeid'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
        gebtyp = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetyp'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='BLDGTYP')
        gebtyp = np.where((gebtyp[:,:]==-9999.), mst.fillvalues['building_type'], gebtyp[:,:])
            
    
    if flags[i]['dostreettypes'] == True:
        roadarr = gdt.rasterandcuttlm(streetsonly, subdir_rasteredshp+'gebaeudehoehe'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='OBJEKTART')
        roadarr = mst.mapstreettypes(roadarr)
        

    ######### create static netcdf file
    static = xr.Dataset()
    x,y = mst.createstaticcoords(vegarr.shape[1],vegarr.shape[0],xres[i])[0:2]
    
    
    #create coordinates, create data Array and then assign to static dataset and append the encodingdict.
    if flags[i]['doterrain'] == True:
        zt = mst.createdataarrays(ztdat,['y','x'],[y,x])
        mst.setneededattributes(zt, 'zt')
        static['zt'] = zt
    if flags[i]['dotlmbb'] == True:
        nsurface_fraction = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres[i])[2]
        vegetation_type = mst.createdataarrays(vegarr,['y','x'],[y,x])
        pavement_type = mst.createdataarrays(pavarr,['y','x'],[y,x])
        water_type = mst.createdataarrays(watarr,['y','x'],[y,x])
        soil_type = mst.createdataarrays(soilarr,['y','x'],[y,x])
        surface_fraction = mst.createdataarrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
        mst.setneededattributes(vegetation_type,'vegetation_type')
        mst.setneededattributes(pavement_type,'pavement_type')
        mst.setneededattributes(water_type,'water_type')
        mst.setneededattributes(soil_type,'soil_type')
        mst.setneededattributes(surface_fraction,'surface_fraction')
        static['vegetation_type'] = vegetation_type
        static['water_type'] = water_type
        static['soil_type'] = soil_type
        static['pavement_type'] = pavement_type
        static['surface_fraction'] = surface_fraction
    if flags[i]['dovegpars'] == True:
        nvegetation_pars =  mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres[i])[3]
        vegetation_pars =  mst.createdataarrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
        mst.setneededattributes(vegetation_pars,'vegetation_pars')
        static['vegetation_pars']=vegetation_pars
    if flags[i]['doalbedopars'] == True:
        nalbedo_pars = mst.createstaticcoords(vegarr.shape[0],vegarr.shape[1],xres[i])[4]
        albedo_pars =  mst.createdataarrays(albedopars, ['nalbedo_pars','y','x'],[nalbedo_pars,y,x])
        mst.setneededattributes(albedo_pars,'albedo_pars')
        static['albedo_pars'] = albedo_pars
    if flags[i]['dolad'] == True:
        lad = mst.createdataarrays(ladarr,['zlad', 'y', 'x'], [zlad,y,x])
        mst.setneededattributes(lad, 'lad')
        static['lad'] = lad
        tree_id = mst.createdataarrays(canopyid, ['y','x'], [y,x])
        mst.setneededattributes(tree_id,'tree_id')
        static['tree_id'] = tree_id
    if flags[i]['dobuildings2d'] == True:
        buildings_2d = mst.createdataarrays(gebhoehe, ['y','x'], [y,x])
        mst.setneededattributes(buildings_2d, 'buildings_2d')
        static['buildings_2d'] = buildings_2d
        building_id = mst.createdataarrays(gebid, ['y','x'], [y,x])
        mst.setneededattributes(building_id, 'building_id')
        static['building_id'] = building_id
        building_type = mst.createdataarrays(gebtyp, ['y','x'], [y,x])
        mst.setneededattributes(building_type, 'building_type')
        static['building_type'] = building_type
    if flags[i]['dobuildings3d'] == True:
        buildings_3d = mst.createdataarrays(bldarr, ['z','y','x'], [z,y,x])
        mst.setneededattributes(buildings_3d, 'buildings_3d')
        static['buildings_3d'] = buildings_3d
        building_id = mst.createdataarrays(gebid, ['y','x'], [y,x])
        mst.setneededattributes(building_id, 'building_id')
        static['building_id'] = building_id
        building_type = mst.createdataarrays(gebtyp, ['y','x'], [y,x])
        mst.setneededattributes(building_type, 'building_type')
        static['building_type'] = building_type
    if flags[i]['dostreettypes'] == True:
        street_type = mst.createdataarrays(roadarr, ['y','x'], [y,x])
        mst.setneededattributes(street_type,'street_type')
        static['street_type'] = street_type
    
    
    encodingdict = mst.setupencodingdict(flags[i])
    mst.setglobalattributes(static,infodict) #set global attributes
    
    mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file




#%% finishing actions and write parameters to a file
parfile = open(outpath+'parameters.txt', 'w') 

print('-----------------------------------------\nSIMULATION SETUP SUMMARY', file = parfile)
print('-----------------------------------------', file = parfile)
domaincells = totaldomains*[0]
rti = totaldomains*[0]

for n in range(totaldomains):
    print('\nDomain '+str(n)+':\nParent Domain'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx[n]-1))+'/'+str(int(ny[n]-1))+'/'+str(int(nz[n]))+
      '\t'+str(xres[n])+'/'+str(yres[n])+'/'+str(zres[n]), file = parfile)
    domaincells[n] = nx[n]*ny[n]*nz[n]
    # rti[n] = domaincells[n]*setvmag/xres[n]
    if n > 0:
        print('ll-Position Coordinates for &nesting_parameters (x,y):\t'+str(llx[n])+', '+str(lly[n]), file = parfile)

print('\nTotal Number of Cells:\t'+"%10.2E" % (sum(domaincells)), file = parfile)
for m in range(len(domaincells)):
    print('Domain '+str(m)+':\t\t'+str(domaincells[m])+'\t'+str( round(domaincells[m]/sum(domaincells),4)*100 )+' %', file = parfile)

print('Runtime length score: '+str(round((sum(domaincells)*setvmag/min(xres))/1e6,2)), file = parfile)

# print('\nNormalized by dxzy')
# for m in range(len(rti)):
#     print('Domain '+str(m)+':\t\t'+str(rti[m])+'\t'+str( round(rti[m]/sum(rti),4)*100 )+' %')

parfile.close() 

print('\n\n-----------------------------------------\nSIMULATION SETUP SUMMARY')
print('-----------------------------------------')
domaincells = totaldomains*[0]
rti = totaldomains*[0]

for n in range(totaldomains):
    print('\nDomain '+str(n)+':\nParent Domain'+':\tnx/ny/nz dx/dy/dz  =  '+str(int(nx[n]-1))+'/'+str(int(ny[n]-1))+'/'+str(int(nz[n]))+
      '\t'+str(xres[n])+'/'+str(yres[n])+'/'+str(zres[n]))
    domaincells[n] = nx[n]*ny[n]*nz[n]
    # rti[n] = domaincells[n]*setvmag/xres[n]
    if n > 0:
        print('ll-Position Coordinates for &nesting_parameters (x,y):\t'+str(llx[n])+', '+str(lly[n]))

print('\nTotal Number of Cells:\t'+"%10.2E" % (sum(domaincells)))
for m in range(len(domaincells)):
    print('Domain '+str(m)+':\t\t'+str(domaincells[m])+'\t'+str( round(domaincells[m]/sum(domaincells),4)*100 )+' %')

print('Runtime length score: '+str(round((sum(domaincells)*setvmag/min(xres))/1e6,2)))

# print('\nNormalized by dxzy')
# for m in range(len(rti)):
#     print('Domain '+str(m)+':\t\t'+str(rti[m])+'\t'+str( round(rti[m]/sum(rti),4)*100 )+' %')










