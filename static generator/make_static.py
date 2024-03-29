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
from datetime import datetime

#%% Read config file and set flags and values appropriately.

cfp = ConfigParser(allow_no_value=True) #

try:
    cfp.read(sys.argv[1]) #check if commandline argument is given for config file.
except:
    print('No command line argument given. Choose your config file.')
    from tkinter import Tk
    from tkinter.filedialog import askopenfilename
    Tk().withdraw()
    inipath = askopenfilename()
    if inipath=='':
        raise ImportError('No file chosen in the Wizard. Abort.')
    cfp.read(inipath)

#%% set paths
modulepath = cfp.get('paths', 'modulepath', fallback = '') #read modulepath from config file
mapdialect = cfp.get('settings', 'mapdialect', fallback = 'mapdicts')

if modulepath not in sys.path:
    sys.path.append(modulepath) #add modulepath to system path if not already there.

#%% import palmpy functions
import palmpy.staticcreation.geodatatools as gdt         #import modules for static generation
import palmpy.staticcreation.makestatictools as mst

#make mapping dialect selection
if mapdialect == 'tlm':
    import palmpy.staticcreation.dictfolder.tlm as mpd
    print('\nINFO: Imported the tlm mapdict.')
elif mapdialect == 'tutorial':
    import palmpy.staticcreation.dictfolder.tutorial as mpd
    print('\nINFO: Imported the tutorial mapdict.')
elif mapdialect == 'DM01AVZH24':
    import palmpy.staticcreation.dictfolder.DM01AVZH24 as mpd
    print('\nINFO: Imported the DM01AVZH24 mapdict.')
elif mapdialect == 'LULC_down_unige_2018':
    import palmpy.staticcreation.dictfolder.LULC_down_unige_2018 as mpd
    print('\nINFO: Imported the LULC downsampled by UNIGE 2018 mapdict.')
elif mapdialect == 'custom':
    import palmpy.staticcreation.dictfolder.custom as mpd
    print('\nINFO: Imported the custom mapdict.')
elif mapdialect == 'mapdicts':
    import palmpy.staticcreation.mapdicts as mpd
    print('\nINFO: Imported the generic mapdicts mapdict.')
# elif mapdialect == 'NEWDIALECT':
#     import palmpy.staticcreation.dictfolder.NEWDIALECT as mpd
#     print('\nINFO: Imported the NEWDIALECT mapdict.')

#%% parse settings and paths
filenames = cfp.get('settings','casename', fallback='default')+'_static'
origin_time = cfp.get('settings', 'origin_time', fallback='2020-08-01 12:00:00 +02')
# totaldomains = cfp.getint('settings', 'totaldomains', fallback=1)
cutorthoimg = cfp.getboolean('settings', 'cutorthoimg', fallback=False)
extentsonly = cfp.getboolean('settings', 'extentsonly', fallback=False)
discrete_zt = cfp.getboolean('settings','discrete_zt', fallback=False)
surf_data_mode = cfp.get('settings','surf_data_mode',fallback='separate') #are land use and pavement separate or together
src_luse_type = cfp.get('settings','src_luse_type',fallback='OBJEKTART') #attribute name of land use type in source shapefile
src_pav_type = cfp.get('settings','src_pav_type',fallback='BELAGSART') #attribute name of pavement type in source shapefile
orthores = cfp.getfloat('settings', 'orthores', fallback=5.0)
rotationangle = cfp.getfloat('settings', 'rotationangle', fallback=0.0)
setvmag = cfp.getfloat('settings', 'set_vmag', fallback=1.0)
simtime = cfp.getfloat('settings', 'simtime', fallback = 14400.0)


#parse paths
inputfilepath = cfp.get('paths', 'inputfilepath')
inputfilepath = os.path.join(inputfilepath, '')
input_crs_epsg =cfp.getint('paths','input_crs_epsg')
ortho = inputfilepath+cfp.get('paths', 'orthoimage')
dhm = inputfilepath+cfp.get('paths', 'dhm')
bb = inputfilepath+cfp.get('paths', 'bb')

#get vegetation input type
veg_input_type = cfp.get('settings','veg_format', fallback='shp')
if not veg_input_type in 'shptiff':
    raise ValueError('Vegetation input type is not "shp" or "tif(f)"')    

if veg_input_type == 'shp':
    #read in vegetation input shapefiles
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

if veg_input_type in 'tiff':
    veg_raster_path = inputfilepath+cfp.get('paths','veg_raster')
    veg_height_bot = cfp.getfloat('settings', 'veg_height_bot',fallback=3.0)

pavementareas = inputfilepath+cfp.get('paths', 'pavementareas')
gebaeudefoots = inputfilepath+cfp.get('paths', 'gebaeudefoots')
crops = inputfilepath+cfp.get('paths', 'crops')
streetsonly = inputfilepath+cfp.get('paths', 'streetsonly')
outpath = cfp.get('paths', 'outpath')
outpath = os.path.join(outpath, '')
subdir_rasteredshp = os.path.join(outpath, 'tmp','')

#try to generate output folders, don't if they exist (throws error when creating a folder)
try:
    os.makedirs(outpath)
    print('Created the output path as given in the namelist.')
except:
    print('Could not creat the output path as given in the namelist (e.g. exists already).')
    pass
try:
    os.makedirs(subdir_rasteredshp)
    print('Create tmp folder for rastered data:')
except:
    pass    


#%% parse domain information
totaldomains = sum(1 for s in cfp.sections() if 'domain' in s)

#initialize all variable lists
ischild = totaldomains*[None];          xmin = totaldomains*[None]
ymin = totaldomains*[None];             zmax = totaldomains*[None] 
xres = totaldomains*[None];             yres = totaldomains*[None]
zres = totaldomains*[None];             xlen = totaldomains*[None]
xmax = totaldomains*[None];             ymax = totaldomains*[None]
nx = totaldomains*[None];               ny = totaldomains*[None]
ylen = totaldomains*[None];             nz = totaldomains*[None]
doterrain = totaldomains*[None];        bulkvegclass = totaldomains*[None]
dolandcover = totaldomains*[None];      dopavedbb = totaldomains*[None]
docropfields = totaldomains*[None];     dolad = totaldomains*[None]
dobuildings_2d = totaldomains*[None];   dobuildings_3d = totaldomains*[None]
dovegpars = totaldomains*[None];        doalbedopars = totaldomains*[None]
dobldgpars = totaldomains*[None];       dopavpars = totaldomains*[None]
dostreettypes = totaldomains*[None];    lai_forest = totaldomains*[None]
lai_breihe = totaldomains*[None];       lai_ebgebu = totaldomains*[None]
a_forest = totaldomains*[None];         b_forest = totaldomains*[None]
a_breihe = totaldomains*[None];         b_breihe = totaldomains*[None]
a_ebgebu = totaldomains*[None];         b_ebgebu = totaldomains*[None]
llx = totaldomains*[0.0];               lly = totaldomains*[0.0]
flags = totaldomains*[{}];              pavealltouched = totaldomains*[None]
bulkpavclass = totaldomains*[None]

#iterate over every section name, if it begins with "domain" then there are domain parameters in it. 0-indexed! 0 is parent.
for i in range(0,len(cfp.sections())):
    section = cfp.sections()[i]
    if section.split('_')[0] == 'domain':
        index = int(section.split('_')[1])
        print('\n'+section)
        try:
            # ischild[index] = cfp.getint(section, 'ischild', fallback=0) #does the same as the next line, but removes to need to define ischild in namelist.
            ischild[index] = index 
        except IndexError:
            print(f'\n\n{15*"@"+" "}ERROR! totaldomains parameter is wrong.{" "+15*"@"}')
            raise
            
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
        dolandcover[index] = cfp.getboolean(section,'dolandcover', fallback=False)
        dopavedbb[index] = cfp.getboolean(section,'dopavedbb', fallback=False)
        docropfields[index] = cfp.getboolean(section,'docropfields', fallback=False)
        dolad[index] = cfp.getboolean(section,'dolad', fallback=False)
        dobuildings_2d[index] = cfp.getboolean(section,'dobuildings_2d', fallback=False)
        dobuildings_3d[index] = cfp.getboolean(section,'dobuildings_3d', fallback=False)
        dovegpars[index] = cfp.getboolean(section,'dovegpars', fallback=False)
        dopavpars[index] = cfp.getboolean(section,'dopavpars', fallback=False)
        doalbedopars[index] = cfp.getboolean(section,'doalbedopars', fallback=False)
        dobldgpars[index] = cfp.getboolean(section,'dobldgpars', fallback=False)
        dostreettypes[index] = cfp.getboolean(section,'dostreettypes', fallback=False)
        
        #method = XXX -> TODO: implement a method selector for lad constant or lad with beta distribution
        bulkvegclass[index] = cfp.getint(section,'bulkvegclass', fallback=3)   #read canopy variables from config file
        bulkpavclass[index] = cfp.getint(section,'bulkpavclass', fallback=1)   
        pavealltouched[index] = cfp.getboolean(section, 'pave_alltouched', fallback = False)
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
            checknestcoord_result = mst.checknestcoordsvalid(xres[index-1],xres[index],llx[index],lly[index])  #for childs check nest coordinates validity

        
        flags[index] = {'doterrain':       doterrain[index], #create flags dictionary 
                        'dolandcover':     dolandcover[index],
                        'dopavedbb':       dopavedbb[index], #requires dolandcover = True
                        'docropfields':    docropfields[index], #requires dolandcover = true
                        'dolad':           dolad[index], #for now: resolved tree file, treerows file and singletree file needed, requires dolandcover=true
                        'dobuildings2d':   dobuildings_2d[index],
                        'dobuildings3d':   dobuildings_3d[index],
                        'dovegpars':       dovegpars[index],
                        'dopavpars':       dopavpars[index],
                        'doalbedopars':    doalbedopars[index],
                        'dobldgpars':      dobldgpars[index],
                        'dostreettypes':   dostreettypes[index]}
        
        #a = '1,2,3,4' #hint for implementation of vegpars/albedopars
        #b = a.split(',')
        #c = list(map(int,b))

#%% correct nest coordinates if they are not on parent grid
if sum('domain' in s for s in cfp.sections())>1:
    if checknestcoord_result == False: #shift coordinates so they match grid of their parents.
        xmin,xmax,ymin,ymax = mst.shift_domain_llxy_to_parent_grid(xmin,ymin,xres,yres,xmax,ymax)

#%% read in probe locations
probes_E = cfp.get('probes', 'probes_E', fallback=str(xmin[0]))
if probes_E != '':
    probes_E = list(map(float,probes_E.replace(' ','').rstrip(',').split(',')))
    probes_E = list(map(round,probes_E))
probes_N = cfp.get('probes', 'probes_N', fallback=str(ymin[0]))
if probes_N != '':
    probes_N = list(map(float,probes_N.replace(' ','').rstrip(',').split(',')))
    probes_N = list(map(round,probes_N))
probes_name = cfp.get('probes', 'probes_name', fallback='default')
if probes_name != '':
    probes_name = list(probes_name.replace(' ','').rstrip(',').split(','))

#%% read in vegpars changes
vegparchanges = cfp.get('change_npars', 'vegparchanges').replace(' ','').rstrip(',').split(',')
if vegparchanges != ['']:
    for it in range(len(vegparchanges)):
        vegparchanges[it] = vegparchanges[it].split(':')
        vegparchanges[it] = list(map(float,vegparchanges[it]))
    
watparchanges = cfp.get('change_npars', 'watparchanges').replace(' ','').rstrip(',').split(',')
if watparchanges != ['']:
    for it in range(len(watparchanges)):
        watparchanges[it] = watparchanges[it].split(':')
        watparchanges[it] = list(map(float,watparchanges[it]))

pavparchanges = cfp.get('change_npars', 'pavparchanges').replace(' ','').rstrip(',').split(',')
if pavparchanges != ['']:
    for it in range(len(pavparchanges)):
        pavparchanges[it] = pavparchanges[it].split(':')
        pavparchanges[it] = list(map(float,pavparchanges[it]))
    
soilparchanges = cfp.get('change_npars', 'soilparchanges').replace(' ','').rstrip(',').split(',')
if soilparchanges != ['']:  
    for it in range(len(soilparchanges)):
        soilparchanges[it] = soilparchanges[it].split(':')
        soilparchanges[it] = list(map(float,soilparchanges[it]))

albedoparchanges = cfp.get('change_npars', 'albedoparchanges').replace(' ','').rstrip(',').split(',')
if albedoparchanges != ['']:
    for it in range(len(albedoparchanges)):
        albedoparchanges[it] = albedoparchanges[it].split(':')
        albedoparchanges[it] = list(map(float,albedoparchanges[it]))

bldgparchanges = cfp.get('change_npars', 'bldgparchanges').replace(' ','').rstrip(',').split(',')
if bldgparchanges != ['']:
    for it in range(len(bldgparchanges)):
        bldgparchanges[it] = bldgparchanges[it].split(':')
        bldgparchanges[it] = list(map(float,bldgparchanges[it]))

    
    
#%% final checks for initialization phase
print('\nFinalizing Checks:\n')

mst.checknxyzisint(nx,ny,nz) #checks if nx ny nz values dont have a float part
nx = list(map(int,nx))
ny = list(map(int,ny))
nz = list(map(int,nz))

#%% create satellite image with domain extents on it.
if cutorthoimg == True:
    #visualize domain boundaries, cut the image new for that with higher res than parent resolution.
    gdt.cutortho(ortho, subdir_rasteredshp+filenames+'_baseortho.tif', 
                 xmin[0],xmax[0],ymin[0],ymax[0],orthores,orthores)
    
    fig = plt.figure(figsize=(16/2.54,16/2.54))
    ax = fig.gca()
    img = plt.imread(subdir_rasteredshp+filenames+'_baseortho.tif')
    ax.imshow(img)
    
    for a in range(0,totaldomains):
        rect = patches.Rectangle((llx[a]/orthores,(ylen[0]-lly[a]-ylen[a])/orthores), 
                              xlen[a]/orthores,ylen[a]/orthores, 
                              linewidth=3, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        
    for b in range(len(probes_E)):
        ax.plot( (probes_E[b]-xmin[0]-(xlen[0]/orthores/10))/orthores, 
                 (ylen[0]-(probes_N[b]-ymin[0]))/orthores, 
                 marker='$'+str(b+1)+'$', color='red',
                 markersize=6)
        ax.plot( (probes_E[b]-xmin[0])/orthores, 
                  (ylen[0]-(probes_N[b]-ymin[0]))/orthores, 
                  marker='.', markersize=8, color='red')
 
    
#%% debugging phase: show plot if exentsonly=True.
    if extentsonly == True:
        plt.show()
        print('\n\nINFORMATION: Plot is only shown, not saved.')
        print('\n\n-----------------------------------------\nDOMAIN INFO')
        print('-----------------------------------------')
        domaincells = totaldomains*[0]
        
        for n in range(totaldomains):
            print('\nDomain '+str(n)+':')
            print('\tnx/ny/nz\t\t'+str(int(nx[n]-1))+'/'+str(int(ny[n]-1))+'/'+str(int(nz[n])))
            print('\tdx/dy/dz\t\t'+str(xres[n])+'/'+str(yres[n])+'/'+str(zres[n]))
            domaincells[n] = nx[n]*ny[n]*nz[n]
            print(f"\tOrigin E/N:\t\t{xmin[n]}/{ymin[n]}")
        print('\nTotal Number of Cells:\t\t'+"%4.2e" % (sum(domaincells)))
        for m in range(len(domaincells)):
            # print('  Domain '+str(m)+':\t\t\t%4.3e\t= %3.2d %%' % (domaincells[m], round(domaincells[m]/sum(domaincells),4)*100))
            print(f'   Domain {m}:\t\t\t{domaincells[m]:4.3e}\t{domaincells[m]/sum(domaincells)*100:.2f}%')
        
        print('\nRuntime length score:\t\t'+str(round((sum(domaincells)*setvmag/min(xres))/1e06,2)))
    
    
    else:
        plt.savefig(outpath+'domainoverview.png')
        print('Saved domainoverview.png')




#%%generation with for loop
#%%
if extentsonly == False:
    for i in range(totaldomains):
        print('\n\n---------------------------\nSTART CREATING DOMAIN '+str(i))
        infodict = {'version':           1, #assemble the infodict, will be added as global attributes to static file.
                    'palm_version':      6.0,
                    'origin_z':          0.0, #is changed further below
                    'origin_y':          ymin[i],
                    'origin_x':          xmin[i],
                    'origin_lat':        gdt.epsgtoWGS84(input_crs_epsg, xmin[i], ymin[i])[0],
                    'origin_lon':        gdt.epsgtoWGS84(input_crs_epsg, xmin[i], ymin[i])[1],
                    'origin_time':       origin_time,
                    'rotation_angle':    rotationangle}
        
        #%%childify filename (add _NXX if necessary)
        filename = mst.childifyfilename(filenames, ischild[i]) #adds _N0X to the filename if needed
        
        #%% cut orthoimage if specified.
        if cutorthoimg == True:
            gdt.cutortho(ortho, subdir_rasteredshp+filename+'_ortho.tif', xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
        
        #%% treat terrain
        if flags[i]['doterrain'] == True:
            ztdat = gdt.cutalti(dhm, subdir_rasteredshp+'dhm'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
            if ischild[i]==0:
                ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i]) #shift the domain downwards to min value if it's the parent domain
                if discrete_zt == True:
                    ztdat = zres[i]*np.round(ztdat/zres[i])
            else:
                ztdat, origin_z = mst.shifttopodown(ztdat,ischild[i],shift=origin_z) #shift the domain downwards with origin_z value of parent if its a child.
                if discrete_zt == True: 
                    ztdat = zres[i]*np.round(ztdat/zres[i])
            infodict['origin_z'] = origin_z    #modify the origin_z attribute according to the shift
        
        #%% treat tlm-bb bulk parametrization
        if flags[i]['dolandcover'] == True:
            if bb.split('.')[-1] in 'shp':
                bbdat = gdt.rasterandcuttlm(bb, subdir_rasteredshp+'bb'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt=src_luse_type)
                vegarr, pavarr, watarr = mst.mapbbclasses2(bbdat, mpd.bb2palmveg, mpd.bb2palmwat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.
                #or: function content in three lines.
                # vegarr = mst.mapdicttoarray(bbdat, mpd.tlmbb2palmveg, mst.fillvalues['vegetation_type'])
                # watarr = mst.mapdicttoarray(bbdat, mpd.tlmbb2palmwat, mst.fillvalues['water_type'])
                # pavarr = np.ones((ny[i],nx[i]))*mst.fillvalues['pavement_type'] #empty array
    
            if bb.split('.')[-1] in 'tiff':
                bbdat = gdt.cutalti(bb, subdir_rasteredshp+'bb'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
                vegarr, pavarr, watarr = mst.mapbbclasses2(bbdat, mpd.bb2palmveg, mpd.bb2palmwat)  #map tlm bodenbedeckungs-kategorien to the palm definitions.

        #%% BLOCK FOR MODIFICATIONS TO VEGPARS AND ALBEDOPARS
            if flags[i]['dovegpars'] == True:
                vegpars = mst.createparsarrays(nx[i], ny[i])[0] # create vegpars arrays and albedopars arrays
                # vegpars = mst.modifyparsarray(vegpars,9,2093,bbdat,9)
                # vegpars = mst.modifyparsarray(vegpars,11,0,bbdat,9)
                for it in range(len(vegparchanges)):
                    if vegparchanges[it][3] < 1000:
                        if vegparchanges[it][2] == 0:
                            vegpars = mst.modifyparsarray(vegpars,int(vegparchanges[it][0]),vegparchanges[it][1],bbdat,vegparchanges[it][3])
                        if vegparchanges[it][2] == 1:
                            vegpars = mst.modifyparsarray(vegpars,int(vegparchanges[it][0]),vegparchanges[it][1],vegarr,vegparchanges[it][3])
                 #TODO: add here also same structure for wat pav soilpars!

            if flags[i]['doalbedopars'] == True:
                albedopars = mst.createparsarrays(nx[i], ny[i])[5]
                # vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, bbdat, 9, 1, -1)
                for it in range(len(albedoparchanges)):
                    if albedoparchanges[it][3] < 1000:
                        if albedoparchanges[it][2] == 0:
                            vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, bbdat, albedoparchanges[it][3], 
                                                                    albedoparchanges[it][1], int(albedoparchanges[it][0]))
                        if albedoparchanges[it][2] == 1:
                            vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, vegarr, albedoparchanges[it][3], 
                                                                    albedoparchanges[it][1], int(albedoparchanges[it][0]))
            
        
        #%% treat LAD
            if flags[i]['dolad'] == True:
                
                if veg_input_type == 'shp':
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
                        
                    #finally
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
                    #finally
                    canalpha = np.maximum.reduce([resforesta,resbreihea,resebgeba])
                    canbeta = np.maximum.reduce([resforestb,resbreiheb,resebgebb])
                    
                    #create an LAI array, only at pixels where canopy has a height. get maximum lai where forest/reihe/ebgebu overlap
                    laiforest = np.where(resforesttop[:,:] != 0, lai_forest[i], resforesttop[:,:])
                    laibreihe = np.where(resbreihetop[:,:] != 0, lai_breihe[i], resbreihetop[:,:])
                    laiebgeb = np.where(resebgebtop[:,:] != 0, lai_ebgebu[i], resebgebtop[:,:])       
                    #finally
                    lai = np.maximum.reduce([laiforest, laibreihe, laiebgeb])
                    
                    canopyheight_maxperid = canopyheight.copy()
                    
                if veg_input_type in 'tiff':
                    print('\nVegetation supplied by tiff file. Read, cut and resample it now:')
                    veg_raster = gdt.cutalti(veg_raster_path, subdir_rasteredshp+'vegraster'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
                    canopyheight = np.where(veg_raster[:,:]<= veg_height_bot+zres[i], -9999., veg_raster[:,:])
                    canopybottom = np.where(canopyheight[:,:]!=-9999., veg_height_bot, canopyheight[:,:])
                    
                    from scipy.ndimage import label
                    canopyid = label( np.where(canopyheight[:,:]==-9999., 0, canopyheight[:,:] ) )[0]
                    canopyid = np.where( canopyid[:,:] == 0, -9999., canopyid[:,:])

                    #use lai, a and b from forest type to create lai, canalpha, canbeta arrays
                    canalpha = np.where(canopyheight[:,:] != -9999., a_forest[i], canopyheight[:,:]) 
                    canbeta = np.where(canopyheight[:,:] != -9999., b_forest[i], canopyheight[:,:]) 
                    lai = np.where(canopyheight[:,:] != -9999., lai_forest[i], canopyheight[:,:])                     
                    
                    canopyheight_maxperid = canopyheight.copy()
                    for idvalue in np.arange(1,canopyid.max()+1): #needed for lad calculation later on: needs max tree height per ID, otherwise "thin" borders of trees too high LAD values.
                        mask = np.where( canopyid[:,:]==idvalue, 0, 1  )
                        max_in_id = np.ma.array(canopyheight, mask=mask).max()
                        canopyheight_maxperid[np.where(mask==0)] = max_in_id
                        
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
                            #what happens if top and bot index equal? -> division by 0
                            pdf = beta.pdf(x=np.arange(0,1,(1/(topindex-botindex))),a=canalpha[k,j],b=canbeta[k,j]) #get a beta distribution (pdf) for given a and b values
                            
                            if pdf.max() == 0.0: #if topindex and botindex equal, pdf returns an array with only 0. this throws an error with pdf/pdf.max(). add 1/further factors in order to have one cell of valid LAD value.
                                pdf = pdf+(1/(lai[k,j]/canopyheight_maxperid[k,j])) 
                                ladarr[botindex:topindex,k,j] = pdf*lai[k,j]/canopyheight_maxperid[k,j]
                            else:
                                ladarr[botindex:topindex,k,j] = pdf/pdf.max()*lai[k,j]/canopyheight_maxperid[k,j] #scale a by the max pdf value, multiply by lai/treeheight (definition of lad)

                ladarr = np.where(ladarr[:,:,:] == 0, -9999., ladarr[:,:,:]) #where lad is 0, make it to nan

                vegarr = np.where((canopyid[:,:] != -9999) & (watarr[:,:] == -127), 3, vegarr[:,:]) #where there is a tree id assigned/where a tree is and no water, set land surface to grass
                vegarr = np.where( (np.maximum.reduce(ladarr) == mst.fillvalues['lad']) & 
                                   (watarr[:,:] == mst.fillvalues['water_type']) &
                                   (canopyid[:,:] != mst.fillvalues['tree_id']), 18, vegarr[:,:]) #where no water and where tree too small to be resolved and where tree_id is present -> set vegtype to deciduous shrubs (18)
                canopyid = np.where(canopyid[:,:] == 0, mst.fillvalues['tree_id'], canopyid[:,:]) #where ther is no tree to be found, set canopyid to its fill value
                canopyid = np.where( np.maximum.reduce(ladarr) == mst.fillvalues['lad'], mst.fillvalues['tree_id'], canopyid[:,:]) #where no lad is defined, maybe bc its subgridscale, set tree-id to fillvalue too
                
                vegarr = np.where( (vegarr[:,:]==-127) & (watarr[:,:]==-127) & (pavarr[:,:]==-127), bulkvegclass[i], vegarr[:,:]) #fill unassigned vegetation types to defined bulk vegetation class.
            
            #%% crop fields will be deprecated
            if flags[i]['docropfields'] == True:
                print('you selected crop fields. this will be deprecated in the future as this functionality has been kind of a workaround since the beginning.')
                croptype = gdt.rasterandcuttlm(crops, subdir_rasteredshp+'croptype'+str(ischild[i])+'.asc', 
                                               xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt=src_luse_type)
                vegarr = np.where( (vegarr[:,:]==bulkvegclass[i]) & (croptype[:,:] != -9999), 2, vegarr[:,:]) #where vegarr is set to bulk class and crops are found, set class to 2 (crops)
            
                
                if flags[i]['dovegpars'] == True:
                    for it in range(len(vegparchanges)):
                        if vegparchanges[it][3] >= 1000:
                            vegpars = mst.modifyparsarray(vegpars,int(vegparchanges[it][0]),vegparchanges[it][1],croptype,vegparchanges[it][3])
                
                if flags[i]['doalbedopars'] == True:      
                    for it in range(len(albedoparchanges)):
                        if albedoparchanges[it][3] >= 1000:
                            vegpars,albedopars = mst.setalbedovalue(albedopars, vegpars, croptype, albedoparchanges[it][3], 
                                                                    albedoparchanges[it][1], int(albedoparchanges[it][0]))

            #%% do paved surfaces
            if flags[i]['dopavedbb'] == True:
                #account for mode separate and ending in tiff -> cutalti. first the tiff ending. when "together", then use path from bb file
                
                if surf_data_mode == 'separate':
                    if pavementareas.split('.')[-1] in 'shp':
                        paved = gdt.rasterandcuttlm(pavementareas, subdir_rasteredshp+'paved'+str(ischild[i])+'.asc',
                                                    xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt=src_pav_type, alltouched=pavealltouched[i])
                    if pavementareas.split('.')[-1] in 'tiff':
                        paved = gdt.cutalti(pavementareas, subdir_rasteredshp+'paved'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])

                if surf_data_mode == 'together':
                    if bb.split('.')[-1] in 'shp':
                        print('not implemented and tested yet.')
                        paved = gdt.rasterandcuttlm(bb, subdir_rasteredshp+'paved'+str(ischild[i])+'.asc',
                                                    xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i], burnatt=src_luse_type, alltouched=pavealltouched[i])
                        paved[:,:] = np.where( np.isin(paved[:,:],np.fromiter(mpd.pav2palmpav.keys(), dtype='int')), paved[:,:], -9999. )                
                        
                    if bb.split('.')[-1] in 'tiff':
                        paved = gdt.cutalti(bb, subdir_rasteredshp+'pavementareas'+str(ischild[i])+'.asc',xmin[i],xmax[i],ymin[i],ymax[i],xres[i],yres[i])
                        paved[:,:] = np.where( np.isin(paved[:,:],np.fromiter(mpd.pav2palmpav.keys(), dtype='int')), paved[:,:], -9999. )                
                
                vegarr = np.where( paved[:,:] != -9999 , mst.fillvalues['vegetation_type'], vegarr[:,:]) #overwrite vegarr where pavement areas are found with fillvalue
                # if flags[i]['dovegpars'] == True:
                #     vegpars[:,:,:] = np.where( paved[:,:] != -9999, mst.fillvalues['vegetation_pars'], vegpars[:,:,:]) #delete vegpars where there is pavement
                watarr = np.where( paved[:,:] != -9999 , mst.fillvalues['water_type'], watarr[:,:]) #overwrite watarr where pavement areas are found with fillvalue
                # pavarr = paved
                # pavarr = np.where ( pavarr[:,:] != -9999, 1, mst.fillvalues['pavement_type']) #pavement_type set where shp is non-fillvalue. TODO: mit einem map dict auch pavements richtig klassifizieren.
                pavarr = mst.mapdicttoarray(paved, mpd.pav2palmpav, fillvalue = np.byte(bulkpavclass[i])) #classify pavement array acc. to dict.
    
        #%% do buildings
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
            maxbldgheight = np.max(gebtop) #+zres[i]
            if maxbldgheight > zmax[i]:         #if maxbldgheight is larger than domain height, set maxbldgheight to domain height.
                maxbldgheight = zmax[i]
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
#            gebid = np.where( bldarr[0] == np.byte(0) , mst.fillvalues['building_id'], gebid[:,:] ) #set id to fillvalue where 3d bldg is not resolved/subgrid scale (especially vertical dimension)
            gebid = np.where( np.maximum.reduce(bldarr) == np.byte(0) , mst.fillvalues['building_id'], gebid[:,:] ) #set id to fillvalue where 3d bldg is not resolved/subgrid scale (especially vertical dimension)
            gebtyp = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudetyp'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='BLDGTYP')
            gebtyp = np.where((gebtyp[:,:]==-9999.), mst.fillvalues['building_type'], gebtyp[:,:]) #change fillvalue to right one, import fcn defatults to -9999.0
#            gebtyp = np.where( bldarr[0] == np.byte(0) , mst.fillvalues['building_type'], gebtyp[:,:] ) #set type to fillvalue where 3d bldg is too small to be resolved.
            gebtyp = np.where( np.maximum.reduce(bldarr) == np.byte(0) , mst.fillvalues['building_type'], gebtyp[:,:] ) #set type to fillvalue where 3d bldg is too small to be resolved.
            
        #%% change buliding pars if buildings are created and dobuildingpars flag is set.
        if (flags[i]['dobuildings2d'] == True or flags[i]['dobuildings3d'] == True) and flags[i]['dobldgpars'] == True:
            bldgpars = mst.createparsarrays(nx[i], ny[i])[4] #create the building pars array
            #INFO: grouped stuff needs to be larger than 0 at the moment! 0 is also a fillvalue!
            group1 = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeareanum'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='GROUPING1')
            group1 = np.where( (group1[:,:]==0), mst.fillvalues['building_pars'], group1[:,:] )
            group2 = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeareanum'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='GROUPING2')
            group2 = np.where( (group2[:,:]==0), mst.fillvalues['building_pars'], group2[:,:] )
            group3 = gdt.rasterandcuttlm(gebaeudefoots, subdir_rasteredshp+'gebaeudeareanum'+str(ischild[i])+'.asc', 
                                            xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='GROUPING3')
            group3 = np.where( (group3[:,:]==0), mst.fillvalues['building_pars'], group3[:,:] )
            input2group = {0: gebtyp, 1:group1, 2:group2, 3:group3}
            
            for it in range(len(bldgparchanges)):
                # if bldgparchanges[it][2] == 0:
                    # ändere based on building_type von oben die building pars                
                bldgpars = mst.modifyparsarray(bldgpars,int(bldgparchanges[it][0]),bldgparchanges[it][1],input2group[bldgparchanges[it][2]],bldgparchanges[it][3])

            
        #%% do street types
        if flags[i]['dostreettypes'] == True: #for chemistry
            # roadarr = gdt.rasterandcuttlm(streetsonly, subdir_rasteredshp+'streettype'+str(ischild[i])+'.asc', 
            #                                 xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt='OBJEKTART', alltouched=pavealltouched[i])
            # roadarr = mst.mapdicttoarray(roadarr, mpd.tlmstr2palmstyp, mst.fillvalues['street_type'])
            
            gdt.splitroadsshp(streetsonly, subdir_rasteredshp, mpd.majroads, mpd.minroads)
            
            majroads = gdt.rasterandcuttlm(subdir_rasteredshp+'majorroads.shp', subdir_rasteredshp+'streettypemajor'+str(ischild[i])+'.asc', 
                                    xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt=src_luse_type, alltouched=pavealltouched[i])
            majroads = mst.mapdicttoarray(majroads, mpd.str2palmstyp, mst.fillvalues['street_type'])
            minroads = gdt.rasterandcuttlm(subdir_rasteredshp+'minorroads.shp', subdir_rasteredshp+'streettypeminor'+str(ischild[i])+'.asc', 
                                    xmin[i], xmax[i], ymin[i], ymax[i], xres[i], yres[i], burnatt=src_luse_type, alltouched=pavealltouched[i])
            minroads = mst.mapdicttoarray(minroads, mpd.str2palmstyp, mst.fillvalues['street_type'])
            
            roadarr = np.copy(majroads)
            roadarr = np.where( (majroads[:,:] == mst.fillvalues['street_type']), minroads[:,:], majroads[:,:])
                   
        
        #%% cleanup on aisle static driver
        
        #cleanup: where bulidings exist, non lad should exist.    
        if ((flags[i]['dobuildings3d'] == True or flags[i]['dobuildings2d']==True) and flags[i]['dolad'] == True): 
            for m in range(len(zlad)):
                ladarr[m,:,:] = np.where( (gebid[:,:] != mst.fillvalues['building_id']), mst.fillvalues['tree_data'], ladarr[m,:,:])
        #remove vegpars where water type is defined
        if ((flags[i]['dovegpars'] == True) and (flags[i]['dolandcover'] == True)):
            vegpars[:,:,:] = np.where( (watarr[:,:] != mst.fillvalues['water_type']), mst.fillvalues['vegetation_pars'], vegpars[:,:,:] )
        #delete vegpars where there is pavement
        if ((flags[i]['dovegpars'] == True) and (flags[i]['dolandcover'] == True) and (flags[i]['dopavedbb']) == True):
            vegpars[:,:,:] = np.where( paved[:,:] != -9999, mst.fillvalues['vegetation_pars'], vegpars[:,:,:]) 

        #where building_type is set, do not set a vegetation type or pavement type
        if ((flags[i]['dobuildings3d'] == True or flags[i]['dobuildings2d']==True ) and flags[i]['dolandcover'] == True):
#            vegarr[:,:] = np.where( gebtyp[:,:] != np.byte(-127), mst.fillvalues['vegetation_type'], vegarr[:,:] )
#            watarr[:,:] = np.where( gebtyp[:,:] != np.byte(-127), mst.fillvalues['water_type'], watarr[:,:] ) #für 3d evtl falsch? muss ja nicht surf. mounted sein.
            vegarr[:,:] = np.where( np.isin(gebtyp[:,:], np.arange(0,21,1) ), mst.fillvalues['vegetation_type'], vegarr[:,:] ) #
            watarr[:,:] = np.where( np.isin(gebtyp[:,:], np.arange(0,21,1) ), mst.fillvalues['water_type'], watarr[:,:] ) #für 3d evtl falsch? muss ja nicht surf. mounted sein.
            
        if ((flags[i]['dobuildings3d'] == True or flags[i]['dobuildings2d']==True ) and flags[i]['dopavedbb'] == True):
#            pavarr[:,:] = np.where( gebtyp[:,:] != np.byte(-127), mst.fillvalues['pavement_type'], pavarr[:,:] )
            pavarr[:,:] = np.where( np.isin(gebtyp[:,:],[0,1,2,3,4,5,6]), mst.fillvalues['pavement_type'], pavarr[:,:] )

        
        #%% create surface fraction array and soilarray in the end, but still only if dotlm is active.
        if flags[i]['dolandcover'] == True:
            soilarr = mst.makesoilarray2(vegarr,pavarr, mpd.palmveg2palmsoil, mpd.palmpav2palmsoil) #finally do soilarray depending on vegarr and pavarr, mapping see makestaticotools in palmpy
            sfrarr = mst.makesurffractarray(vegarr,pavarr,watarr) #create surfacefraction in end, as now only 0 and 1 fractions are allowed (ca r4400)

        #cleanup those two arrays (sfrarr and soilarr) as well
        if (flags[i]['dobuildings2d'] == True):
            soilarr[:,:] = np.where( gebtyp[:,:] != mst.fillvalues['building_type'], mst.fillvalues['soil_type'], soilarr[:,:] )        
            sfrarr[:,:,:] = np.where( gebtyp[:,:] != mst.fillvalues['building_type'], mst.fillvalues['surface_fraction'], sfrarr[:,:,:])

        if (flags[i]['dobuildings3d'] == True):
            #bei 3d: geh nach erstem gridpoint in bldarr. wenn buliding: set to fillvalue, sonst nicht.
            soilarr[:,:] = np.where( np.isin(gebtyp[:,:], [0,1,2,3,4,5,6]), mst.fillvalues['soil_type'], soilarr[:,:] )        
            sfrarr[:,:,:] = np.where( np.isin(gebtyp[:,:], [0,1,2,3,4,5,6]), mst.fillvalues['surface_fraction'], sfrarr[:,:,:])
#            soilarr[:,:] = np.where( bldarr[0,:,:] == 1, mst.fillvalues['soil_type'], soilarr[:,:] )        
#            sfrarr[:,:,:] = np.where( bldarr[0,:,:] == 1, mst.fillvalues['surface_fraction'], sfrarr[:,:,:])
    


        #%% create static netcdf file
        static = xr.Dataset()
        x,y = mst.createstaticcoords(nx[i],ny[i],xres[i])[0:2] #create x and y cordinates. 
        
        #create coordinates, create data Array and then assign to static dataset and append the encodingdict.
        if flags[i]['doterrain'] == True:
            zt = mst.createdataarrays(ztdat,['y','x'],[y,x]) #create xr.DataArray object
            mst.setneededattributes(zt, 'zt') #set attributes to dataarray object
            static['zt'] = zt    #add dataarray object to dataset object
        if flags[i]['dolandcover'] == True:
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
        if flags[i]['dobldgpars'] == True:
            nbuilding_pars = mst.createstaticcoords(ny[i],nx[i],xres[i])[8]
            building_pars =  mst.createdataarrays(bldgpars, ['nbuilding_pars','y','x'],[nbuilding_pars,y,x])
            mst.setneededattributes(building_pars,'building_pars')
            static['building_pars'] = building_pars
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
        
        static.attrs['creation_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        static.attrs['Conventions'] = 'CF-1.7'
        
        if flags[i]['dobuildings3d'] == True:
            mst.setneededattributes(static.z,'z') #set attributes of coordinate z if buildings are set (only data to require z so far)
        
        encodingdict = mst.setupencodingdict(flags[i]) #create encoding dictionary for saving the netcdf file (maybe not needed if really all fillvalues and dtypes are set correct!)
        mst.setglobalattributes(static,infodict) #set global attributes
        
        #%% output the file
        mst.outputstaticfile(static,outpath+filename, encodingdict) #output the static file as netcdf file.
    
    
    #%% finishing actions and write parameters to a file
    parfile = open(outpath+filenames[:-7]+'_parameters.txt', 'w') 
    
    print('-----------------------------------------\nSIMULATION SETUP SUMMARY', file = parfile)
    print('-----------------------------------------', file = parfile)
    domaincells = totaldomains*[0]
    
    print(f"\norigin_date_time        =        '{origin_time}'", file=parfile)
    print('Topo shifted down by (origin_z):\t\t{:.2f} Meter'.format(origin_z), file=parfile)
    
    

    for n in range(totaldomains):
        print('\nDomain '+str(n)+':', file=parfile)
        print(f'    nx     = {str(int(nx[n]-1)).rjust(6)},\n    ny     = {str(int(ny[n]-1)).rjust(6)},\n    nz     = {str(int(nz[n])).rjust(6)},', file=parfile)
        print(f'    dx     = {str(xres[n]).rjust(6)},\n    dy     = {str(yres[n]).rjust(6)},\n    dz     = {str(zres[n]).rjust(6)},', file=parfile)
        domaincells[n] = nx[n]*ny[n]*nz[n]
        
        # # rti[n] = domaincells[n]*setvmag/xres[n]
        print(f"\tOrigin E/N:\t\t{xmin[n]}/{ymin[n]}", file=parfile)
        # if n > 0:
        #     print('\tll-Position for &nesting_parameters\n\tx,y:\t\t\t'+str(llx[n])+', '+str(lly[n]))
    
    if sum('domain' in s for s in cfp.sections())>1:
        for n in range(totaldomains):
            if n == 0:
                print(f'\nNesting Parameters: Child positions\n    {"domain_layouts".ljust(25)}= "PAR", {n+1}, -1, #CORES,{str(0).rjust(8)}.,{str(0).rjust(8)}.,', file=parfile)
            if n > 0:
                print(f'    {" ".ljust(25)}= "N{str(n+1).zfill(2)}", {n+1},  {n}, #CORES,{str(llx[n]).rjust(9)},{str(lly[n]).rjust(9)},', file=parfile)

    

    print('\n----------------------\nTotal Number of Cells:\t\t'+"%4.2e" % (sum(domaincells)), file=parfile)
    for m in range(len(domaincells)):
        # print('  Domain '+str(m)+':\t\t\t%4.3e\t= %3.2d %%' % (domaincells[m], round(domaincells[m]/sum(domaincells),4)*100), file=parfile)
        print(f'   Domain {m}:\t\t\t{domaincells[m]:4.3e}\t{domaincells[m]/sum(domaincells)*100:.2f}%', file=parfile)
        
    print('\nRuntime length score:\t\t'+str(round((sum(domaincells)*setvmag/min(xres))/1e6,2)), file = parfile)
        
    print('\n\n---------------------\nProbes (for masked output):\n', file = parfile)
    if probes_E == '':
        print('\tNone.', file = parfile)
    if probes_E != '':
        for b in range(totaldomains):
            print(f'Domain {b}:', file = parfile)
            for c in range(len(probes_E)):
                if ((probes_E[c]-xmin[b])>0) and ((probes_N[c]-ymin[b])>0):
                    # print(f"\tProbe {probes_name[c]}: x/y\t\t{probes_E[c]-xmin[b]}/{probes_N[c]-ymin[b]}")
                    print(f"\t{probes_name[c]}: x/y{5*' '}{probes_E[c]-xmin[b]}/{probes_N[c]-ymin[b]}", file = parfile)
                    print(f"\t\t\tmask_x_loop(X,:)   =   {((probes_E[c]-xmin[b])//xres[b])*xres[b]-xres[b]},{((probes_E[c]-xmin[b])//xres[b])*xres[b]+2*xres[b]},{xres[b]}", file = parfile)
                    print(f"\t\t\tmask_y_loop(X,:)   =   {((probes_N[c]-ymin[b])//yres[b])*yres[b]-yres[b]},{((probes_N[c]-ymin[b])//yres[b])*yres[b]+2*yres[b]},{yres[b]}", file = parfile)


    source = {0:'Source Data classes', 1:'PALM classes'}
    print('\n\n----------------------\nChanges to vegetation/albedo/water/pavement/soil_pars', file=parfile)
    if (vegparchanges == [''] and albedoparchanges == [''] and watparchanges == [''] and 
        pavparchanges == [''] and soilparchanges == [''] and bldgparchanges == [''] ):
        print('\tNone.', file=parfile)
    if vegparchanges != ['']:
        print('\nManual overrides for vegetation type:', file=parfile)
        for e in vegparchanges:
            print(f"\tFor class {int(e[3])}, set npar {int(e[0])} to {e[1]} based on {source[e[2]]}.", file=parfile)
            
    if albedoparchanges != ['']:
        print('\nManual overrides for albedo type:', file=parfile)
        for e in albedoparchanges:
            print(f"\tFor class {int(e[3])}, set npar {int(e[0])} to {e[1]} based on {source[e[2]]}.", file=parfile)
        
    if watparchanges != ['']:
        print('\nManual overrides for vegetation type:', file=parfile)
        for e in watparchanges:
            print(f"\tFor class {int(e[3])}, set npar {int(e[0])} to {e[1]} based on {source[e[2]]}.", file=parfile)
    
    if pavparchanges != ['']:
        print('\nManual overrides for vegetation type:', file=parfile)
        for e in pavparchanges:
            print(f"\tFor class {int(e[3])}, set npar {int(e[0])} to {e[1]} based on {source[e[2]]}.", file=parfile)
        
    if soilparchanges != ['']:
        print('\nManual overrides for vegetation type:', file=parfile)
        for e in soilparchanges:
            print(f"\tFor class {int(e[3])}, set npar {int(e[0])} to {e[1]} based on {source[e[2]]}.", file=parfile)

    print(f'\n\nCreated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', file=parfile)
    
    parfile.close() 
  
    #%% read the file and print it to console.
    with open(outpath+filenames[:-7]+'_parameters.txt','r') as param_file:
        print(param_file.read())

    
    #%% create inifor namelist and save to file
    
    namelist = open(outpath+filenames[:-7]+'_inifornamelist', 'w')
    print('&inipar nx = {:d}, ny = {:d}, nz = {:d},\n' \
          '        dx = {:.1f}, dy = {:.1f}, dz = {:.1f},\n    /'.format(int(nx[0])-1, 
                                                                 int(ny[0]-1), 
                                                                 int(nz[0]),
                                                                 xres[0], yres[0], 
                                                                 zres[0]),
          file=namelist)
    print('&d3par    end_time = {:.1f}\n    /'.format(simtime), file = namelist)
    print(f"\n\n! Created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", file=namelist)
    namelist.close() 
    
    print('\nCreated inifor namelist.')


    plt.show()
