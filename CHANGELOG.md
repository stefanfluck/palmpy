## 2023-02-22
changes merged from dev branch into master branch:
- Added automatic shift of nest lower left corner coords if they are invalid
- Added: land use data for vegetation and pavements can be provided as one file under the bb path. For that, set `surf_data_mode` in namelist to 'together'. 
- Added: land use data can be provided as tiff. the code checks for file endings tif(f) or shp.
- Added: option to have discrete `zt` rounded to `zres` value.
- Added mapdialect for LULC land use dataset from Uni Geneva 2018 (https://doi.org/10.3390/land11050615)
- Changed: parameters.txt now contains formatted, ready to copy/paste text for p3d files
- Changed: parameters.txt contains domain_layouts variable ready to copy.
- Changed: Probes: Names can be set, and they are only put to parameters.txt if they are within a certain domain
- Removed need for tmp file path - always in output file path.
- Removed: paths don't require trailing / or \ anymore.
- Changed: update template namelist
- Fixed origin_lon/lat calculation. For that an EPSG code needs to be provided in the namelist in the path section.
- Fixed bug where when `dolad == False`, unclassified points would be set to the bulk vegetation type. indentation was wrong.
- Deprecated: info that cropfields will be deprecated at some stage.



## 2022-05-06
- Added capability to input 3d vegetation as a raster instead of shapefile. Set `veg_format` to `shp` or `tiff` and provide the shp in the namelist as `resolvedforest` etc, or the tiff under `veg_raster`.
- Added feature to define the name of the surface type attribute column in the shapefile the respective surface information is read from. Set `src_luse_type` for the vegetation/water shapefile, and `srv_pav_type` for the sealed surface file. Defaults are "OBJEKTART" and "BELAGSART" respectively to maintain backward compatibility. 
- Fixed creation and immediate deletion of tmp.tif files in the github repo folder.
- Changed documentation to reflect changes.



## Start changelog on 2022-05-06.
Keywords:
- Added
- Changed
- Deprecated
- Removed
- Fixed
- Security