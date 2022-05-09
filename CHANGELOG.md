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