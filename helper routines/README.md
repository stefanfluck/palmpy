This folder contains various helper routines, aimed at facilitating some procedures around simulations in PALM. 

## cosmo2inifor

These routines will convert COSMO1-analysis-datasets from MeteoSwiss into a format, which can be read by the INIFOR routine that is shipped with PALM.
cosmo2inifor_revC can be used for files starting with ``lafYYYYMMDDHH.nc``. cosmo2inifor_revD has been written for a custom data format, where data is spread over four files.

## rcplot3.py

This routine can be used to plot u/v/wmax, dt, divold/divnew and other metrics while a simulation is running. Run it from the palm working directory.
```
python rcplot3.py
```

## <...>batchrun

Use these as guidance if multiple runs shall be started unsupervised. ``complexbatchrun`` includes copying restart namelists into the case folder.
