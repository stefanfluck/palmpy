<header>
    <font size="+4"><b>palmpy 1.0 Documentation</b></font>
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

































 <a href="#top">Back to top</a>

<br/>

# Glossary











 <a href="#top">Back to top</a>



