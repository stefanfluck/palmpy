"""
Static File generation script.
written by Stefan Fluck, fluf@zhaw.ch in FS2020.

"""
import xarray as xr
import sys
import os
from configparser import ConfigParser
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

#%% Read config file and set flags and values appropriately.

cfp = ConfigParser(allow_no_value=True) #

try:
    cfp.read(sys.argv[1]) #check if commandline argument is given for config file.
except:
    print('No command line argument given. Using hardcoded config_file path in script.')
    cfp.read("C:\\Users\\Stefan Fluck\\Documents\\Python Scripts\\ZAV-PALM-Scripts\\example_scripts\\make_static\\make_static.ini")
    # cfp.read("C:\\Users\\Stefan Fluck\\Desktop\\ladtest.ini")

modulepath = cfp.get('paths', 'modulepath') #read modulepath from config file

# modulepath = str(Path.home() / 'Documents' / 'Python Scripts' / 'ZAV-PALM-Scripts') #uncomment this line to have module path hardcoded.

if modulepath not in sys.path:
    sys.path.append(modulepath) #add modulepath to system path if not already there.
    
import palmpy.staticcreation.geodatatools as gdt         #import modules for static generation
import palmpy.staticcreation.makestatictools as mst



#parse settings and paths
filenames = cfp.get('settings','casename', fallback='default')+'_static'
origin_time = cfp.get('settings', 'origin_time', fallback='2020-08-01 12:00:00 +02')
totaldomains = cfp.getint('settings', 'totaldomains', fallback=1)
cutorthoimg = cfp.getboolean('settings', 'cutorthoimg', fallback=False)
orthores = cfp.getfloat('settings', 'orthores', fallback=5.0)
rotationangle = cfp.getfloat('settings', 'rotationangle', fallback=0.0)
setvmag = cfp.getfloat('settings', 'set_vmag', fallback=1.0)
simtime = cfp.getfloat('settings', 'simtime', fallback = 14400.0)

inputfilepath = cfp.get('paths', 'inputfilepath')
ortho = inputfilepath+cfp.get('paths', 'orthoimage')
dhm = inputfilepath+cfp.get('paths', 'dhm')
bb = inputfilepath+cfp.get('paths', 'bb')

if cfp.get('paths', 'resolvedforest') != '':
    resolvedforestshp = inputfilepath+cfp.get('paths', 'resolvedforest')
else:
    resolvedforestshp = None
if cfp.get('paths', 'treerows') != '':
    treerowsshp = inputfilepath+cfp.get('paths', 'treerows')
else:
    treerowsshp = None
if cfp.get('paths', 'singletrees') != '':
    singletreesshp = inputfilepath+cfp.get('paths', 'singletrees')
else:
    singletreesshp = None

pavementareas = inputfilepath+cfp.get('paths', 'pavementareas')
gebaeudefoots = inputfilepath+cfp.get('paths', 'gebaeudefoots')
crops = inputfilepath+cfp.get('paths', 'crops')
streetsonly = inputfilepath+cfp.get('paths', 'streetsonly')
subdir_rasteredshp = cfp.get('paths', 'tmp')
outpath = cfp.get('paths', 'outpath')

#try to generate output folders, don't if they exist (throws error when creating a folder)
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

#iterate over every section name, if it begins with "domain" then there are domain parameters in it. 0-indexed! 0 is parent.
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
        xmax[index] = xmin[index]+xlen[index] #compute xmax from xmin and xlen
        ymax[index] = ymin[index]+ylen[index]
        nx[index] = xlen[index]/xres[index]   #compute number of cells from len and res
        ny[index] = ylen[index]/yres[index]
        nz[index] = zmax[index]/zres[index]
        if index > 0:
            llx[index] = xmin[index]-xmin[0]  #compute domain origin distance to parent origin, only for domains that are not parent
            lly[index] = ymin[index]-ymin[0]
        doterrain[index] = cfp.getboolean(section,'doterrain', fallback=False)  #read flags from config file
        dotlmbb[index] = cfp.getboolean(section,'dotlmbb', fallback=False)
        dostreetsbb[index] = cfp.getboolean(section,'dostreetsbb', fallback=False)
        docropfields[index] = cfp.getboolean(section,'docropfields', fallback=False)
        dolad[index] = cfp.getboolean(section,'dolad', fallback=False)
        dobuildings_2d[index] = cfp.getboolean(section,'dobuildings_2d', fallback=False)
        dobuildings_3d[index] = cfp.getboolean(section,'dobuildings_3d', fallback=False)
        dovegpars[index] = cfp.getboolean(section,'dovegpars', fallback=False)
        doalbedopars[index] = cfp.getboolean(section,'doalbedopars', fallback=False)
        dostreettypes[index] = cfp.getboolean(section,'dostreettypes', fallback=False)
        
        #method = XXX -> TODO: implement a method selector for lad constant or lad with beta distribution
        bulkvegclass[index] = cfp.getint(section,'bulkvegclass', fallback=None)   #read canopy variables from config file
        lai_forest[index] = cfp.getfloat(section,'lai_forest', fallback=None)
        lai_breihe[index] = cfp.getfloat(section,'lai_breihe', fallback=None)
        lai_ebgebu[index] = cfp.getfloat(section,'lai_ebgebu', fallback=None)
        a_forest[index] = cfp.getfloat(section,'a_forest', fallback=None)
        b_forest[index] = cfp.getfloat(section,'b_forest', fallback=None)
        a_breihe[index] = cfp.getfloat(section,'a_breihe', fallback=None)
        b_breihe[index] = cfp.getfloat(section,'b_breihe', fallback=None)
        a_ebgebu[index] = cfp.getfloat(section,'a_ebgebu', fallback=None)
        b_ebgebu[index] = cfp.getfloat(section,'b_ebgebu', fallback=None)
        
        mst.checknxyzvalid(nx[index],ny[index],nz[index])   #check if nxyz choice is valids
        if index > 0:
            mst.checknestcoordsvalid(xres[index-1],xres[index],llx[index],lly[index])  #for childs check nest coordinates validity
        
        flags[index] = {'doterrain':       doterrain[index], #create flags dictionary 
                        'dotlmbb':         dotlmbb[index],
                        'dostreetsbb':     dostreetsbb[index], #requires dotlmbb = True
                        'docropfields':    docropfields[index], #requires dotlmbb = true
                        'dolad':           dolad[index], #for now: resolved tree file, treerows file and singletree file needed, requires dotlmbb=true
                        'dobuildings2d':   dobuildings_2d[index],
                        'dobuildings3d':   dobuildings_3d[index],
                        'dovegpars':       dovegpars[index],
                        'doalbedopars':    doalbedopars[index],
                        'dostreettypes':   dostreettypes[index]}
        
        #a = '1,2,3,4' #hint for implementation of vegpars/albedopars
        #b = a.split(',')
        #c = list(map(int,b))
        
#further checks:
print('\nFinalizing Checks:\n')

mst.checknxyzisint(nx,ny,nz) #checks if nx ny nz values dont have a float part
nx = list(map(int,nx))
ny = list(map(int,ny))
nz = list(map(int,nz))
#visualize domain boundaries, cut the image new for that with higher res than parent resolution.
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
    print('\nSTART CREATING DOMAIN '+str(i))
    infodict = {'version':           1, #assemble the infodict, will be added as global attributes to static file.
                'palm_version':      6.0,
                'origin_z':          0.0, #is changed further below
                'origin_y':          ymin[i],
                'origin_x':          xmin[i],
                'origin_lat':        gdt.lv95towgs84(xmin[i]+2000000,ymin[i]+1000000)[1],
                'origin_lon':        gdt.lv95towgs84(xmin[i]+2000000,ymin[i]+1000000)[0],
                'origin_time':       origin_time,
                'rotation_angle':    rotationangle}
    
    #childify filename (add _NXX if necessary)
    filename = mst.childifyfilename(filenames, ischild[i]) #adds _N0X to the filename if needed
    
    #### cut orthoimage if specified.
    if cutorthoimg == True:
        gdt.cutortho(ortho, subdir_rasteredshp+filename+'_ortho.tif', xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
    
    ##### treat terrain
    if flags[i]['doterrain'] == True:
        ztdat = gdt.cutalti(dhm, subdir_rasteredshp+'dhm'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
        if ischild[i]==0:
            ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i]) #shift the domain downwards to min value if it's the parent domain
        else:
            ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i],shift=origin_z) #shift the domain downwards with origin_z value of parent if its a child.
        infodict['origin_z'] = origin_z    #modify the origin_z attribute according to the shift
    
    ##### treat tlm-bb bulk parametrization
    if flags[i]['dotlmbb'] == True:
        bbdat = gdt.rasterandcuttlm(bb, subdir_rasteredshp+'bb'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt='OBJEKTART')
        vegarr, pavarr, watarr = mst.mapbbclasses(bbdat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
        
        
    ##### BLOCK FOR MODIFICATIONS TO VEGPARS AND ALBEDOPARS
    
        # vegpars = mst.createparsarrays(nx[i], ny[i])[0]
        # albedopars = mst.createparsarrays(nx[i], ny[i])[5]
    
        # vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, bbdat, 9, 1, -1)
        # vegpars = mst.modifyparsarray(vegpars,9,2093,bbdat,9)
        # vegpars = mst.modifyparsarray(vegpars,11,0,bbdat,9)
    
    ##### treat LAD
        if flags[i]['dolad'] == True:
            
            #import canopyfiles
            if resolvedforestshp != None:
                resforesttop = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforesttop'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
                resforestbot = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestbot'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
                resforestid = gdt.rasterandcuttlm(resolvedforestshp, subdir_rasteredshp+'resolvedforestid'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            else:
                resforesttop = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resforestbot = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resforestid = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                
            if treerowsshp != None:
                resbreihetop = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihentop'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
                resbreihebot = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenbot'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
                resbreiheid = gdt.rasterandcuttlm(treerowsshp, subdir_rasteredshp+'resolvedbreihenid'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            else:
                resbreihetop = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resbreihebot = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resbreiheid = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                
            if singletreesshp != None:
                resebgebtop = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebtop'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
                resebgebbot = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebbot'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
                resebgebid = gdt.rasterandcuttlm(singletreesshp, subdir_rasteredshp+'resolvedebgebid'+str(ischild[i])+'.asc', 
                                                xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
            else:
                resebgebtop = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resebgebbot = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                resebgebid = np.ones((ny[i], nx[i]))*mst.fillvalues['vegetation_height']
                
            
            canopyheight = np.maximum.reduce([resforesttop, resbreihetop, resebgebtop]) #analyze all arrays in each pixel and return max value per pixel
            canopybottom = np.maximum.reduce([resforestbot, resbreihebot, resebgebbot])
            canopyid = np.maximum.reduce([resforestid, resbreiheid, resebgebid])
            
            #create arrays for alpha and beta and reduce to one layer in the end
            resforesta = np.where(resforesttop[:,:] != 0, a_forest[i], resforesttop[:,:])     # alpha für forest
            resforestb = np.where(resforesttop[:,:] != 0, b_forest[i], resforesttop[:,:])     # beta für forest
            resbreihea = np.where(resbreihetop[:,:] != 0, a_breihe[i], resbreihetop[:,:])     # alpha für baumreihe
            resbreiheb = np.where(resbreihetop[:,:] != 0, b_breihe[i], resbreihetop[:,:])     # beta für baumreihe
            resebgeba = np.where(resebgebtop[:,:] != 0, a_ebgebu[i], resebgebtop[:,:])        # alpha für ebgeb
            resebgebb = np.where(resebgebtop[:,:] != 0, b_ebgebu[i], resebgebtop[:,:])        # beta für ebgeb
            canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
            canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
            
            #create an LAI array, only at pixels where canopy has a height. get maximum lai where forest/reihe/ebgebu overlap
            laiforest = np.where(resforesttop[:,:] != 0, lai_forest[i], resforesttop[:,:])
            laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe[i], resbreihetop[:,:])
            laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu[i], resebgebtop[:,:])        
            lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
            
            maxtreeheight = np.max(canopyheight) #evaluate maximum tree height for zlad coordinate generation
            
            zlad= mst.createzlad(maxtreeheight, zres[i]) #create zlad array
            ladarr = np.ones((len(zlad), ny[i], nx[i]))*mst.fillvalues['tree_data'] #create empty lad array
            
            chdztop = np.where(canopyheight[:,:]==-9999., canopyheight[:,:], np.round(canopyheight[:,:]/zres[i],0).astype(int)) # cell indexes that need to be filled with lad.
            chidxtop = np.where( (chdztop[:,:]==0), -9999, chdztop[:,:]) #index of zlad height that needs to be filled (same as above, leiche)
            chdzbot = np.where(canopybottom[:,:]==-9999., canopybottom[:,:], np.round(canopybottom[:,:]/zres[i],0).astype(int)) #same for bottom.
            chidxbot = np.where( (chdzbot[:,:]==0), 0, chdzbot[:,:]) #index of zlad height that needs to be filled
            
            #create actual lad array
            from scipy.stats import beta
            for k in range(ny[i]): #iterate over y and x dimensions
                for j in range(nx[i]):
                    if not chidxtop[k,j] == -9999:
                        botindex = int(chidxbot[k,j])
                        topindex = int(chidxtop[k,j])+1
                        pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[k,j],b=canbeta[k,j]) #get a beta distribution (pdf) for given a and b values
                        ladarr[botindex:topindex,k,j] = pdf/pdf.max()*lai[k,j]/canopyheight[k,j] #scale a by the max pdf value, multiply by lai/treeheight (definition of lad)
                        
            vegarr = np.where((canopyid[:,:] != -9999) & (watarr[:,:] == -127), 3, vegarr[:,:]) #where there is a tree id assigned/where a tree is and no water, set land surface to grass
            vegarr = np.where( (ladarr[0] == mst.fillvalues['lad']) &
                               (watarr[:,:] == mst.fillvalues['water_type']) &
                               (canopyid[:,:] != mst.fillvalues['tree_id']), 18, vegarr[:,:]) #where no water and where tree too small to be resolved and where tree_id is present -> set vegtype to deciduous shrubs (18)
            canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:]) #where ther is no tree to be found, set canopyid to its fill value
            canopyid = np.where( ladarr[0] == mst.fillvalues['lad'], mst.fillvalues['tree_id'], canopyid[:,:]) #where no lad is defined, maybe bc its subgridscale, set tree-id to fillvalue too
            
        vegarr = np.where( (vegarr[:,:]==-127) & (watarr[:,:]==-127) & (pavarr[:,:]==-127), bulkvegclass[i], vegarr[:,:]) #fill unassigned vegetation types to defined bulk vegetation class.
        
        if flags[i]['docropfields'] == True:
            cropheight = gdt.rasterandcuttlm(crops, subdir_rasteredshp+'felder'+str(ischild[i])+'.asc', 
                                           xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
            vegarr = np.where( (vegarr[:,:]==bulkvegclass[i]) & (cropheight[:,:] != -9999), 2, vegarr[:,:]) #where vegarr is set to bulk class and crops are found, set class to 2 (crops)
        
        
        if flags[i]['dostreetsbb'] == True:
            paved = gdt.rasterandcuttlm(pavementareas, subdir_rasteredshp+'pavement'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt='OBJEKTART')
            vegarr = np.where( paved[:,:] != -9999 , mst.fillvalues['vegetation_type'], vegarr[:,:]) #overwrite vegarr where pavement areas are found with fillvalue
            watarr = np.where( paved[:,:] != -9999 , mst.fillvalues['water_type'], watarr[:,:]) #overwrite watarr where pavement areas are found with fillvalue
            pavarr = paved
            pavarr = np.where ( pavarr[:,:] != -9999, 1, mst.fillvalues['pavement_type']) #pavement_type set where shp is non-fillvalue. TODO: mit einem map dict auch pavements richtig klassifizieren.
       
        #create surface fraction array
        soilarr = mst.makesoilarray(vegarr,pavarr) #finally do soilarray depending on vegarr and pavarr, mapping see makestaticotools in palmpy
        sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr) #create surfacefraction in end, as now only 0 and 1 fractions are allowed (ca r4400)
        
    if flags[i]['dobuildings2d'] == True:  
        gebhoehe = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudehoehe'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
        gebid = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeid'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
        gebtyp = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetyp'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='BLDGTYP')
        gebtyp = np.where((gebtyp[:,:]==-9999.), mst.fillvalues['building_type'], gebtyp[:,:]) #change fillvalue to byte, import function defaults to -9999.0
    
    if flags[i]['dobuildings3d'] == True:
        gebtop = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetop'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_TOP')
        gebbot = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudebot'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='HEIGHT_BOT')
        maxbldgheight = np.max(gebtop)+zres[i]
        z = mst.createzcoord(maxbldgheight,zres[i])              #create z coordinate
        bldarr = np.ones((len(z), ny[i], nx[i]))*np.byte(0) #create empty buliding3d array
        
        bhdztop = np.where(gebtop[:,:]==-9999., gebtop[:,:], np.round(gebtop[:,:]/zres[i],0).astype(int))
        bhidxtop = np.where( (bhdztop[:,:]==0), -9999, bhdztop[:,:]) #index of zlad height that needs to be filled
        bhdzbot = np.where(gebbot[:,:]==-9999., gebbot[:,:], np.round(gebbot[:,:]/zres[i],0).astype(int))
        bhidxbot = np.where( (bhdzbot[:,:]==0), 0, bhdzbot[:,:]) #index of zlad height that needs to be filled
        
        for k in range(ny[i]):
               for j in range(nx[i]):
                   # if not np.isnan(chidxtop[k,j]):
                   if not bhidxtop[k,j] == -9999:
                       botindex = int(bhidxbot[k,j])
                       topindex = int(bhidxtop[k,j])+1
                       bldarr[botindex:topindex,k,j] = np.byte(1)
        
        gebid = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeid'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='ID')
        gebid = np.where( bldarr[0] == np.byte(0) , mst.fillvalues['building_id'], gebid[:,:] ) #set id to fillvalue where 3d bldg is not resolved/subgrid scale
        gebtyp = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetyp'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='BLDGTYP')
        gebtyp = np.where((gebtyp[:,:]==-9999.), mst.fillvalues['building_type'], gebtyp[:,:]) #change fillvalue to right one, import fcn defatults to -9999.0
        gebtyp = np.where( bldarr[0] == np.byte(0) , mst.fillvalues['building_type'], gebtyp[:,:] ) #set type to fillvalue where 3d bldg is too small to be resolved.
            
    if flags[i]['dostreettypes'] == True:
        roadarr = gdt.rasterandcuttlm(streetsonly, subdir_rasteredshp+'gebaeudehoehe'+str(ischild[i])+'.asc', 
                                        xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='OBJEKTART')
        roadarr = mst.mapstreettypes(roadarr)
        

    ######### create static netcdf file
    static = xr.Dataset()
    x,y = mst.createstaticcoords(nx[i],ny[i],xres[i])[0:2] #create x and y cordinates. 
    
    #create coordinates, create data Array and then assign to static dataset and append the encodingdict.
    if flags[i]['doterrain'] == True:
        zt = mst.createdataarrays(ztdat,['y','x'],[y,x]) #create xr.DataArray object
        mst.setneededattributes(zt, 'zt') #set attributes to dataarray object
        static['zt'] = zt    #add dataarray object to dataset object
    if flags[i]['dotlmbb'] == True:
        nsurface_fraction = mst.createstaticcoords(ny[i],nx[i],xres[i])[2] #create coordinates of the item
        vegetation_type = mst.createdataarrays(vegarr,['y','x'],[y,x])    #create dataarray object
        pavement_type = mst.createdataarrays(pavarr,['y','x'],[y,x])
        water_type = mst.createdataarrays(watarr,['y','x'],[y,x])
        soil_type = mst.createdataarrays(soilarr,['y','x'],[y,x])
        surface_fraction = mst.createdataarrays(sfrarr,['nsurface_fraction','y','x'],[nsurface_fraction,y,x])
        mst.setneededattributes(vegetation_type,'vegetation_type')  #set attributes
        mst.setneededattributes(pavement_type,'pavement_type')
        mst.setneededattributes(water_type,'water_type')
        mst.setneededattributes(soil_type,'soil_type')
        mst.setneededattributes(surface_fraction,'surface_fraction')
        static['vegetation_type'] = vegetation_type #merge into dataset object
        static['water_type'] = water_type
        static['soil_type'] = soil_type
        static['pavement_type'] = pavement_type
        static['surface_fraction'] = surface_fraction
    if flags[i]['dovegpars'] == True:
        nvegetation_pars =  mst.createstaticcoords(ny[i],nx[i],xres[i])[3]
        vegetation_pars =  mst.createdataarrays(vegpars, ['nvegetation_pars','y','x'],[nvegetation_pars,y,x])
        mst.setneededattributes(vegetation_pars,'vegetation_pars')
        static['vegetation_pars']=vegetation_pars
    if flags[i]['doalbedopars'] == True:
        nalbedo_pars = mst.createstaticcoords(ny[i],nx[i],xres[i])[4]
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
    
    mst.setneededattributes(static.x,'x') #set attributes of basic coordinates x and y
    mst.setneededattributes(static.y,'y')
    
    if flags[i]['dobuildings3d'] == True:
        mst.setneededattributes(static.z,'z') #set attributes of coordinate z if buildings are set (only data to require z so far)
    
    encodingdict = mst.setupencodingdict(flags[i]) #create encoding dictionary for saving the netcdf file (maybe not needed if really all fillvalues and dtypes are set correct!)
    mst.setglobalattributes(static,infodict) #set global attributes
    
    mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file as netcdf file.


#%% finishing actions and write parameters to a file
parfile = open(outpath+'parameters.txt', 'w') 

print('-----------------------------------------\nSIMULATION SETUP SUMMARY', file = parfile)
print('-----------------------------------------', file = parfile)
domaincells = totaldomains*[0]
rti = totaldomains*[0]

for n in range(totaldomains):
    print('\nDomain '+str(n)+':', file=parfile)
    print('\tnx/ny/nz\t\t'+str(int(nx[n]-1))+'/'+str(int(ny[n]-1))+'/'+str(int(nz[n])), file=parfile)
    print('\tdx/dy/dz\t\t'+str(xres[n])+'/'+str(yres[n])+'/'+str(zres[n]), file=parfile)
    domaincells[n] = nx[n]*ny[n]*nz[n]
    # rti[n] = domaincells[n]*setvmag/xres[n]
    if n > 0:
        print('  ll-Position for &nesting_parameters\n\tx,y:\t\t\t'+str(llx[n])+', '+str(lly[n]), file=parfile)

print('\nTotal Number of Cells:\t\t'+"%4.2e" % (sum(domaincells)), file=parfile)
for m in range(len(domaincells)):
    print('  Domain '+str(m)+':\t\t\t%4.3e\t= %3.2d %%' % (domaincells[m], round(domaincells[m]/sum(domaincells),4)*100), file=parfile)
print('\nTopo shifted down by:\t\t{:.2f} Meter'.format(origin_z), file=parfile)
print('\nRuntime length score:\t\t'+str(round((sum(domaincells)*setvmag/min(xres))/1e6,2)), file = parfile)

# print('\nNormalized by dxzy')
# for m in range(len(rti)):
#     print('Domain '+str(m)+':\t\t'+str(rti[m])+'\t'+str( round(rti[m]/sum(rti),4)*100 )+' %')

parfile.close() 

print('\n\n-----------------------------------------\nSIMULATION SETUP SUMMARY')
print('-----------------------------------------')
domaincells = totaldomains*[0]
rti = totaldomains*[0]

for n in range(totaldomains):
    print('\nDomain '+str(n)+':')
    print('\tnx/ny/nz\t\t'+str(int(nx[n]-1))+'/'+str(int(ny[n]-1))+'/'+str(int(nz[n])))
    print('\tdx/dy/dz\t\t'+str(xres[n])+'/'+str(yres[n])+'/'+str(zres[n]))
    domaincells[n] = nx[n]*ny[n]*nz[n]
    # rti[n] = domaincells[n]*setvmag/xres[n]
    if n > 0:
        print('  ll-Position for &nesting_parameters\n\tx,y:\t\t\t'+str(llx[n])+', '+str(lly[n]))

print('\nTotal Number of Cells:\t\t'+"%4.2e" % (sum(domaincells)))
for m in range(len(domaincells)):
    print('  Domain '+str(m)+':\t\t\t%4.3e\t= %3.2d %%' % (domaincells[m], round(domaincells[m]/sum(domaincells),4)*100))

print('\nTopo shifted down by:\t\t{:.2f} Meter'.format(origin_z))
print('\nRuntime length score:\t\t'+str(round((sum(domaincells)*setvmag/min(xres))/1e6,2)))


#%% create inifor namelist and save to file

namelist = open(outpath+'inifornamelist', 'w')
print('&inipar nx = {:d}, ny = {:d}, nz = {:d},\n' \
      '        dx = {:.1f}, dy = {:.1f}, dz = {:.1f},\n    /'.format(int(nx[0])-1, 
                                                             int(ny[0]-1), 
                                                             int(nz[0]),
                                                             xres[0], yres[0], 
                                                             zres[0]),
      file=namelist)
print('&d3par    end_time = {:.1f}\n    /'.format(simtime), file = namelist)

namelist.close() 

print('\nCreated inifor namelist.')


