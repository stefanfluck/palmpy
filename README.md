# palmpy 

palmpy consists of a python package and a python and bash scripts that support a user in the data preprocessing steps for conducting simulations with the [PALM Model System](https://palm.muk.uni-hannover.de/trac). The supplied static generator script makes it easy to generate static driver files containing the terrain variable, vegetation/water/pavement/soil_types, resolved vegetation and more. It is built to handle standard geodata formats (shape file vector data and geotiff raster data). 


![Geodata to Static Driver with palmpy](https://github.com/stefanfluck/palmpy/blob/master/docs/palmpy-documentation.assets/geodatatostaticwithpalmpy.jpg?raw=true)




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
Refer to the wiki for an extensive documentation of palmpy. It includes guidance on how to preprocess geodata so it can be used with ``palmpy``. The documentation covers:

- Installation
- Description of submodules and functions
- Geodata preprocessing tips
- Description of the Static Generator
- Namelist Documentation
- Further information regarding simulations with PALM



## Installation
[More detail here.](https://github.com/stefanfluck/palmpy/wiki/palmpy-Installation)

``palmpy`` requires numpy, matplotlib, netcdf4, gdal and more to be installed in the environment. Guidance is included in the documentation on how to set up a suitable environment for `palmpy`. With the following one-liner, you can install an env in conda and install all required packages.
```python
conda create -n palmpyenv -c conda-forge pandas geopandas numpy scipy matplotlib pillow netcdf4 gdal rasterio xarray
```

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

In the ``examples`` folder, a ``tutorial example`` is included to create your first static driver file. This folder contains a palmpy configuration file ``tutorialcase.ini`` and the geodata in a separate directory, which will be processed in this example. The geodata provided for this example is publicly available data from the city of Zurich and is taken from their [Open Data Catalog](https://data.stadt-zuerich.ch/). This geodata has already been preprocessed to contain the required columns for use in ``palmpy``. See the documentation in ``docs`` for guidance on how to preprocess geodata for ``palmpy``.

The following steps will produce a static driver file for a PALM simulation containing

- terrain,
- land cover (vegetation and water bodies),
- paved surfaces,
- buildings, and
- trees.



The procedure is as follows: 

1. Create a new *conda* environment using one of the ``.yml`` files from the ``envs`` folder in the repository. More guidance can be found [here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file).

   ```
   #In anaconda prompt
   conda env create --name palm --file palm2.yml
   ```

2. Open the ``tutorialcase.ini`` configuration file (included in ``palmpy\\examples\\tutorial_example``). 

3. All parameters are already set up for this particular test case. However, you will need to change the ``[paths]`` section of this configuration file to reflect your particular file locations.

   1. change the ``modulepath`` variable to the path, where the ``palmpy`` folder is located
   2. change the ``inputfilepath`` variable to the path, where the input geodata is located. Mind the trailing ``\`` on windows or ``/`` on linux. 
   3. change the ``outpath`` and ``tmp`` variables to where the output shall be saved. in the ``tmp`` folder, intermediate results will be saved. Mind the trailing ``\`` on windows or ``/`` on linux. 

4. Activate your created *conda* environment and run the ``make_static.py`` script. 

   ```bash
   conda activate palm
   
   #navigate into static generator folder in palmpy repo
   
   #run the script
   python make_static.py ..\\examples\\tutorial_example\\tutorialcase.ini
   ```

   If you supply the ``tutorialcase.ini`` file in the execution command, it will automatically read it in. If you omit it, a window will open allowing you to browse your system for the file. 

5. The static driver file will be generated. Congratulations, you have just created a static driver file from geodata. The output consists of your static driver file, a "parameter" file containing all relevant information to set up the PALM-namelist and even a potential INIFOR-namelist. Look at the data using a netcdf file viewer or ``ncview``, depending on your system.

6. Have a look at the extensive documentation regarding guidance on geodata preprocessing and further options available in `palmpy`.





---

DISCLAIMER: No liability is assumed regarding the correctness of the provided routines. Users shall check the behavior and reporting of bugs is highly appreciated.





