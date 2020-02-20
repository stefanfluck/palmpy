# palmpy

Processing scripts for the PALM model system
-------------

This is a github repo for PALM scripts that should facilitate the usage of [PALM](https://palm.muk.uni-hannover.de/trac). This repository contains various elements, that deal with certain aspects of handling data for PALM, especially with geodata products by swisstopo in mind (_swissALTI3D, swissTLM3D_). These elements can be grouped in actions regarding

  - input data processing
      - swissALTI3D & swissTLM3D -> <id>_static files
      - COSMO data preprocessor for INIFOR compatibility
  - runtime analysis
      - plotting of _tmp/<id>.#/RUN_CONTROL_ data (available soon)
  - postprocessing of output data
      - output (available soon)

with a clear focus on the first, as it is clearly the most labor-intensive and tedious step of them all. This repo also contains the conda environment needed for all those functions.

Depending on your system, choose the appropriate <env>.yml file. Try to use the one with package version info first 
```
  conda env create -f palmenv-versinfo.yml -n <newname>
```
This may not work on systems other than windows 10 x86.

This repository is a the result of student work at the Center for Aviation, ZHAW School of Engineering in Winterthur and is work in progress. 




DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and reporting of bugs is highly appreciated.
