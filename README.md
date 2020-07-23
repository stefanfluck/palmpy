# palmpy 

palmpy consists of a python package and a python and bash scripts that support a user in the data preprocessing steps for conducting simulations with the [PALM Model System](https://palm.muk.uni-hannover.de/trac). The supplied static generator script makes it easy to generate static driver files containing the terrain variable, vegetation/water/pavement/soil_types, resolved vegetation and more. It is built to handle standard geodata formats (shape file vector data and geotiff raster data). 



![geodatatostaticwithpalmpy](C:\Users\stefa\Documents\Python Scripts\palmpy-repo\README.assets\geodatatostaticwithpalmpy.jpg)





## What is the PALM Model System?

The  [PALM Model System](https://palm.muk.uni-hannover.de/trac) is an advanced large-eddy simulation model for atmospheric and oceanic boundary-layer flows. The PALM model system is currently being developed to become a powerful urban climate model, allowing to answer relevant research question regarding urban climate and city planning activities. 



## Features

``palmpy`` can do the following:

- generate static driver files for PALM simulations that include
  - terrain
  - land cover information
  - resolved vegetation
  - modify vegetation parameters (level 3 classification)
  - modify building parameters (level 3 classification)
  - street types
- static generator script steered by a namelist (config file)
- nested domains are supported
- process geodata in their standard formats
  - vector data as shape files (.shp)
  - raster data as geotiffs (.tif)
- perform checks if generated domain will be usable in PALM
- generate namelist for inifor routine (dynamic driver file generator shipped with PALM)
- output probe location coordinates for masked output in PALM relative to each domain



## Documentation

In the folder ``docs``, an extensive documentation of ``palmpy`` can be found, including guidance on how to preprocess geodata so it can be used with ``palmpy``. The documentation covers:

- Installation
- Description of submodules and functions
- Geodata preprocessing tips
- Description of the Static Generator
- Namelist Documentation
- Further information regarding simulations with PALM



## Installation

``palmpy`` requires numpy, matplotlib, netcdf4, gdal and more to be installed in the environment. Guidance is included in the documentation on how to set up a suitable environment for `palmpy`.

Static files can be generated simply by running the static generator script ``make_static.py``. In order for it to run, just download the ``palmpy`` folder into an appropriate location, e.g. the python `$PATH`.  Then, copy the path to the ``palmpy`` folder into the ``make_static.ini`` configuration file that is required to define the desired domain. 

In order to individually access functions of the ``palmpy`` package, more steps are recommended. As of yet, palmpy is not available through pip or conda. In order to use the package, copy the ``palmpy`` folder in this repository to a location that is included in the python $PATH. This will be one of the locations that is displayed by running the following code in your python console:

```python
import sys
print(sys.path)
```

It is recommended to import palmpy with the following command:

```python
#static file generation
import palmpy.staticcreation.geodatatools as gdt      	# geodata modification tools
import palmpy.staticcreation.makestatictools as mst   	# static generation tools
import palmpy.staticcreation.mapdicts.<dialect> as mpd	# mapping dictionaries for mst
```





## Example Usage













---

DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and reporting of bugs is highly appreciated.





