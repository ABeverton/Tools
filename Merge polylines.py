# Databricks notebook source
pip install geopandas shapely fiona

# COMMAND ----------

import fiona
fiona.supported_drivers['ESRI Shapefile'] = 'raw'
fiona.drvsupport.SHAPE_RESTORE_SHX = 'YES'

import geopandas as gpd
from shapely.ops import linemerge

def merge_river_network(shapefile_path, output_path):
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf[gdf.geometry.type == 'LineString']
    merged_geometries = linemerge([geom for geom in gdf.geometry])
    merged_gdf = gpd.GeoDataFrame(geometry=[merged_geometries], crs=gdf.crs)
    merged_gdf.to_file(output_path)

input_shapefile = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/River Shape/Clipped_Rivers.shp'
output_shapefile = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/River Shape/merge_Clipped_Rivers.shp'

merge_river_network(input_shapefile, output_shapefile)

