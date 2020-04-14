<header>
    <font size="+2"><b>palmpy 1.0 Documentation</b></font>
</header>

**Table of Contents**

[TOC]

---



# Introduction

Welcome to palmpy! This package will help you create static files for your PALM Simulation. It contains various elements that deal with certain aspects of handling data for PALM, initially built around geodata products by swisstopo (*swissALTI3D, swissTLM3D*) and expanded since. Palmpy deals with various aspects of PALM data processing, which can be summarized by the following:

 

- input data processing
  - raster data and shapefiles -> _static files
  - COSMO data preprocessor scripts to make them usable with INIFOR
- runtime analysis
  - plotting of *tmp/id.#/RUN_CONTROL* data (available soon)
- postprocessing of output data
  - regridding (available soon)
  - plotting (available soon)



with a clear focus on the first, as it is clearly the most labor-intensive and tedious step of them all. This repo also contains the conda environment needed for all those functions.

Depending on your system, choose the appropriate .yml file. Try to use the one with package version info first

```
  conda env create -f palmenv-versinfo.yml -n <newname>
```

This may not work on systems other than Windows 10 x86.

This repository is a the result of student work at the Center for Aviation, ZHAW School of Engineering in Winterthur and is work in progress.

DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and reporting of bugs is highly appreciated.



## How it works

collection of functions

make static script to make static file







-----



 <a href="#top">Back to top</a>

<br/>

# Installation of palmpy

## Python Environment





## Package Installation

where to install it, path specification



## Basic Usage

```
This is code. started with ```
```









 <a href="#top">Back to top</a>

---



<br/>

# Palmpy Description



## Preprocessing & Static File Generation





### *geodatatools*



### *makestatictools*



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





















# Further Information

## Dynamic Driver Generation with INIFOR

PALM can be forced with COSMO-Data. PALM is shipped with a routine called INIFOR, which interpolates boundary conditions from hourly COSMO-DE data for the lateral and top boundary, furthermore, it creates an initial condition volume field for the domain. Also, geostrophic wind components are extracted from the COSMO pressure field, as well as a surface pressure value. 

With its orientation towards data available in Germany, INIFOR is intended to be used with COSMO-DE data, which is available in 2km resolution and with a specific naming of the variables. Swiss COSMO-Data, which was made available so far with the ZHAW, is in a different format and in 1km resolution. Apart from this, the variable naming does not seem to be consistent anyway, which requires some modifications to the COSMO-Files before being able to use them in INIFOR. To convert them into INIFOR-readable format, two scripts for two different conventions have been written (routines cosmo2inifor). Their operation is detailed below. After conversion, INIFOR can be run, this process is also outlined below.



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

Under ``&inipar``, grid information of the parent is given. under ``&d3par`` the endtime is given. Coordinates are taken from the static-driver, so it has to be ensured that this information is correct. Furthermore, even though the static-file origin_time attribute is unused for now, it will be used in the future, so it should be correctly set as well. It has the format ``YYYY-MM-DD HH:MM:SS +ZZ``. 

Load required modules to run PALM before running INIFOR. INIFOR is executed as follows in the bash shell:

```bash
inifor -p <path> -d <date> -i <init-mode> -n <namelist> --input-prefix <input-prefix> -t <static-driver> -o <output> -a <averaging-angle>
```



**Hints / Troubleshooting:**

- Date format: YYYYMMDDHH. Start time stamp is used, it know how far to process from the end_time parameter in the namelist.
- input-prefix is ``seg``, if the files were processed with cosmo2inifor. Standard is ``laf``.
- Averaging angle ``-a`` might not work if the is below 0.2. So far, no real changes were visible when going from an averaging angle of 0.1 to 0.01.

- If a segmentation-fault occurs during processing, create a copy of the .palm.config.twins18 and recompile it with ``palmbuild -c twins18(copy)``. This seems to recompile INIFOR too. Usually it works again after that. Negative averaging angles also lead to a segmentation fault.




 <a href="#top">Back to top</a>

<br/>



# Useful Code Snippets

## Castor / Pollux Cluster

load required modules to run PALM (without parallel I/O, no RRTMG!)

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



# Glossary











 <a href="#top">Back to top</a>



