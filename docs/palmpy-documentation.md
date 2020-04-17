<header>
    <font size="+3"><b>palmpy Framework 1.0 Documentation</b></font>
</header>

**Table of Contents**

[TOC]

---

<div style="page-break-after: always; break-after: page;"></div>

# Introduction

Welcome to palmpy! This package will help you create static files for your PALM simulation. It contains various elements that deal with certain aspects of handling data for PALM, initially built around geodata products by swisstopo (*swissALTI3D, swissTLM3D*) and expanded since. Palmpy assists you in the following tasks:

- input data processing
  - raster data and shapefiles -> _static files
  - COSMO data preprocessor scripts to make them usable with INIFOR
- runtime analysis
  - plotting of *tmp/id.#/RUN_CONTROL* data (available soon)
- postprocessing of output data
  - regridding (available soon)



...with a clear focus on the first, as it is clearly the most labor-intensive and tedious step of them all. Part of the Framework are also supporting files, such as conda environment setup files and bash routines, that support PALM simulation activities in general.

This Framework is the result of student work at the Center for Aviation, ZHAW School of Engineering in Winterthur and is work in progress.

DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and the produced results carefull. Reporting of bugs is highly appreciated.



## Applied Paradigms - how it works

Framework Components

- palmpy Python Package
- supporting Bash Scripts
- 





collection of functions

make static script to make static file

manual control with python programming language.





---

<div style="page-break-after: always; break-after: page;"></div>

<div style="page-break-after: always; break-after: page;"></div>

# Palmpy Description





## *geodatatools*



## *makestatictools*



## *mapdicts*



## Installation of palmpy

### Python Environment

It is strongly recommended to set up python with the conda package management ecosystem. There are many ways to do it. Users relatively unfamiliar with python can install the full [Anaconda](https://www.anaconda.com/) software, which comes with the most relevant python packages for doing science, but also with some baggage in form of software. More experienced users, who know what packages they need and are able to install them easily, can install python with a [Miniconda](https://docs.conda.io/en/latest/miniconda.html) installer, which only installs the bare minimum of packages and python on the machine (much smaller download size). Most importantly, the conda package manager is installed as well. 

Once a running conda environment (usually named ``base``, you can check it with entering ``conda env list`` into the Anaconda Prompt (in Windows) or your regular shell (in Linux)) is present. we set up a new environment that contains all necessary packages to run palmpy. Environment are an essential tool when it comes to software development and allows to "freeze" an environment to have defined package versions and dependencies for a particular project. After the following process, an environment "palm" (or however you name it) shall be present in the conda environment list.



<img src="palmpy-documentation.assets\image-20200415113429165.png" alt="image-20200415113429165" style="zoom:80%;" />

<center><font size="-1">Different conda environments on a computer.</font></center>



Depending on your system, choose the appropriate .yml file from the ``env`` folder. Try to use the one with package version info first. This may not work on systems other than Windows 10 x86.

```bash
  conda env create -f palmenv-versinfo.yml -n <envname>
```

If it does not work, use the .yml file without version numbers attached to the packages.





### Package Installation

When importing a package in python with ``import package``, python automatically scans its $PATH variable for the required package. Therefore, if we want palmpy to be fount, we need to move the palmpy folder into one of those locations. In order to know, where you should put it, open a python console in your newly created environment (eg. open ``Spyder (envname)`` to open Spyder with your desired environment or open Anaconda promt, run ``conda activate envname``, followed by ``python`` to enter the python interpreter).  Run the following:

```python
import sys
print(sys.path)
```

This will output a list of paths, that are searched for the module. Your best bet is to put the palmpy module folder into your ``...\\Miniconda3\\envs\envname\\lib`` folder.

If you are able to import the module palmpy with ``import palmpy`` and no error appears, the package was installed correctly.






### Basic Usage

It is recommended to load the different modules of the palmpy package as follows:

```python
#static file generation
import palmpy.staticcreation.geodatatools as gdt      # geodata modification tools
import palmpy.staticcreation.makestatictools as mst   # static generation tools
import palmpy.staticcreation.mapdicts as mpd		  # mapping dictionaries for mst

#post processing
import palmpy.postprocessing.tools as ppt             # postprocessing tools
```



To create a static file, you need the palmpy *geodatatools*, *makestatictools* and the dictionaries for mapping shp-file classes to PALM classes - which are separately available in *mapdicts*. Should a default mapping be not suitable for a particular project, this *mapdict*s file can be modified accordingly. For individual application of palmpy, these dicts can be accessed through python individually.





---

<div style="page-break-after: always; break-after: page;"></div>

# Create a PALM Static driver using palmpy

### QGIS Input File Preparation



#### Paradigms and Standards





#### Rastered Data

geotiff

##### Topography



##### Surface Classification





#### Shapefiles

insert Table here



##### Resolved Vegetation



##### Pavement / Sealed Surfaces



##### Crops



##### Buildings







### Static File Generation Script



#### Script



#### Namelist

















---

<div style="page-break-after: always; break-after: page;"></div>

# Further Information

## Dynamic Driver Generation with INIFOR

PALM can be forced with COSMO-Data. PALM is shipped with a routine called INIFOR, which interpolates boundary conditions from hourly COSMO-DE data for the lateral and top boundary, furthermore, it creates an initial condition volume field for the domain. Also, geostrophic wind components are extracted from the COSMO pressure field, as well as a surface pressure value. 

With its orientation towards data available in Germany, INIFOR is intended to be used with COSMO-DE data, which is available in 2 km resolution and with a specific naming of the variables. Swiss COSMO-Data, which was made available so far with the ZHAW, is in a different format and in 1 km resolution. Apart from this, the variable naming does not seem to be consistent anyway, which requires some modifications to the COSMO-Files before being able to use them in INIFOR. To convert them into INIFOR-readable format, two scripts for two different conventions have been written (routines cosmo2inifor). Their operation is detailed below. After conversion, INIFOR can be run, this process is also outlined below.



### cosmo2inifor

cosmo2inifor is a bash script, that converts COSMO-1 Data to INIFOR-appropriate format. Two revisions exist, which support two different variable conventions:

| Name              | Use with                                                     |
| ----------------- | ------------------------------------------------------------ |
| cosmo2inifor_revC | lafYYYYMMDDHH.nc files from ETH Server                       |
| cosmo2inifor_revD | meteotest_....nc file (multiple files per hour), received for project at the ZHAW |

Should you encounter a COSMO-Output format that cannot be processed with one of the above routines, a specifically tailored one needs to be set up or can be derived from the above routines.

These routines make use of 

- nco (4.8.1): ncks, ncrename, ncatted, ncap2
- netcdf (4.6.1): ncdump



**Using cosmo2inifor**

1. On the ZAV cluster (Twins), these modules can be loaded with the command ``module load nco/4.8.1 netcdf/4.6.1-gnu``. 

2. Put the files, that are to be converted, into a directory with the cosmo2inifor routine. If you simulate a time span of 1200Z-1600Z, you need the files with results of the hours 12, 13, 14, 15 *and* 16.
3. Run the script with ``./cosmo2inifor_revX``. It will extract a ``hhl.nc``, ``soil.nc`` and for each hour a ``segYYYYMMDDHH-flow.nc`` and ``segYYYYMMDDHH-soil.nc`` file.



### INIFOR

INIFOR will interpolate (bilinear, as of April 2020) boundary conditions from the COSMO data. It requires a soil.nc, hhl.nc and for each hour a -flow.nc and a -soil.nc file, which need to be available in a single location. It also requires a namelist containing information of the parent domain (the one that will be forced). It can look like the following:

```fortran
&inipar nx = 127, ny = 127, nz = 96,
        dx = 32.0, dy = 32.0, dz = 32.0,
    /
&d3par    end_time = 86400.0
    /
```

Under ``&inipar``, grid information of the parent is given. Under ``&d3par`` the endtime is given. This namelist file is automatically generated when running make_static.py, taking all necessary information from the corresponding namelist for the make_static routine. Coordinates are taken from the static-driver, so it has to be ensured that this information is correct. Furthermore, even though the static-file origin_time attribute is unused for now, it will be used in the future, so it should be correctly set as well. It has the format ``YYYY-MM-DD HH:MM:SS +ZZ``. 

Load required modules to run PALM before running INIFOR. INIFOR is executed as follows in the bash shell:

```bash
inifor -p <path> -d <date> -i <init-mode> -n <namelist> --input-prefix <input-prefix> -t <static-driver> -o <output> -a <averaging-angle>
```



**Hints / Troubleshooting:**

- Date format: YYYYMMDDHH. Start time stamp is used, it know how far to process from the end_time parameter in the namelist.
- input-prefix is ``seg``, if the files were processed with cosmo2inifor. Standard is ``laf``.
- Averaging angle ``-a`` might not work if the is below 0.2. So far, no real changes were visible when going from an averaging angle of 0.1 to 0.01.

- If a segmentation-fault occurs during processing, create a copy of the .palm.config.twins18 and recompile it with ``palmbuild -c twins18(copy)``. This seems to recompile INIFOR too. Usually it works again after that. Negative averaging angles also lead to a segmentation fault.





## VAPOR Visualization

VAPOR is a visualization tool for scientific 3D data. From VAPOR 3 and above, netCDF files can be imported easily, if they conform to the CF-1.7 standard. This requires to have an "axis"-attribute for each coordinate variable (e.g.``axis:X``for the ``x`` variable, and so forth for ``xu, y, yv, zu_3d, zw_3d, zs_3d``). This was missing until recently in PALM, this axis is now automatically added (from March 2020 onwards). Before, it could be added with ``ncatted -O -a axis,x,o,c,"X" <file>`` for example.

In order to have terrain in the 3D, file this information needs to be copied from the static driver to the 3D-File. This can be achieved with the following command:

```
ncks -A -v <static-file> <3d_output_file>
```

Bear in mind, that this is currently only easily doable for netcdf-3 output on the PALM side (netcdf_output_format == 3). 

VAPOR works on the basis of vdc files. NetCDF files can be converted into vdc files with a series of VAPOR command line tools - however, I have not managed to complete the whole process. It should be doable with the commands (in this order) ``cfvdccreate <outputfile> <file.vdc>``, which creates a header file. Then, ``cf2vdc outputfile file.vdc`` should populate the file with data from the nc-file. 



## PALM Simulation Lessons Learned

The following questions are written down here for a reason. They are important questions to ask yourself when simulating with PALM.



- Are the static driver time stamps, end_times and skip_time_data_output parameters in the namelists correct?
- Are you simulating the correct day?
- Have you supplied ``-a "d3#/r restart"`` when you want to continue your run after? If not, its all lost.
- Have you checked that output variables are really only supplied ones, especially the _av ones? (These arrays are set up after skip_time_data_output, if you skip large parts of your simulations, an error is raised and the simulation is lost)
- A simulation can be started with ``palmrun ...... -v > logfile &``. With this, the output is piped into a logfile and with ``&`` the command is executed in a subshell. This means, that one can log out of the cluster without the palmrun routine being aborted. This could also be achieved with ``nohup palmrun .... -v``, which apparently also pipes the output to a nohup.log file (not tested).

---

<div style="page-break-after: always; break-after: page;"></div>


# Useful Code Snippets

## Castor / Pollux Cluster

load required modules to run PALM (**basic configuration**, without parallel I/O, no RRTMG!)

```bash
module load gnu mpich2/3.3.1-gnu hdf5/1.8.15-gnu7 netcdf/4.6.1-gnu7 netcdf/4.4.4-gfort7
```

use RRTMG as well (if compiled): run the following command before starting a simulation:

```bash
export LD_LIBRARY_PATH=/cluster/home/<rrtmg_install_location>/lib/rrtmg/shared/lib:$LD_LIBRARY_PATH
```





## NCO

```bash
ncatted -O -a grid_mapping,SOILTYP,o,c,'rotated_pole' soil.nc

ncea -d y_1,-0.5,0.5 -d x_1,-1.0,0.0 filein fileout

ncap2 -O -s ‘time=time+39600’ <in> <out>
```



## CDO

**Regridding**

Make a gridfile (target.grid) of the form:

```
gridtype   =     lonlat
xsize      =     500
ysize      =     200
xfirst     =     5.7
xinc       =     0.01
yfirst     =     45.70
yinc       =     0.01
```

and run ``cdo remapbil,target.grid input output``.

Industry Standard seems to be ``remapcon`` (conservative), ``remapbil`` is bilinear remapping.







---

<div style="page-break-after: always; break-after: page;"></div>

# Glossary










