# PALMPY

Processing scripts for the PALM model system
-------------

This is a collection of scripts and a python package that should facilitate the usage of [PALM](https://palm.muk.uni-hannover.de/trac). This repository contains various elements, that deal with certain aspects of handling data for PALM. These elements can be grouped in actions regarding

  - input data processing
      - vector and raster geodata to static files, with some simplifications
      - COSMO-1 data reformatter (from meteoswiss) for INIFOR compatibility (written for COSMO-DE)
  - runtime analysis
      - plotting of _tmp/id.#/RUN_CONTROL_ data (available soon)


This repository also contains the conda environment needed for all those functions.

Depending on your system, choose the appropriate <env>.yml file. Try to use the one with package version info first 
```
  conda env create -f palmenv-versinfo.yml -n <newname>
```
This may not work on systems other than windows 10 x86.

This repository is a the result of student work at the Center for Aviation, ZHAW School of Engineering in Winterthur and is work in progress. 

For guidance, please see the documentation in the docs folder. The palmpy folder contains the python package. Put the folder in a location as described in the documentation.



DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and reporting of bugs is highly appreciated.
