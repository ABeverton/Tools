# Databricks notebook source
pip install geopandas

# COMMAND ----------

import geopandas as gpd

# Load the shapefiles
river_shapefile = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/River Shp/WatercourseLink.shp'  # Replace with the path to your river network shapefile
polygon_shapefile = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/River Shp/River_Limits.shp'      # Replace with the path to your polygon shapefile

# Read the river network (polylines) and polygon shapefiles
river_gdf = gpd.read_file(river_shapefile)
polygon_gdf = gpd.read_file(polygon_shapefile)

# Ensure both shapefiles are in the same coordinate reference system (CRS)
if river_gdf.crs != polygon_gdf.crs:
    polygon_gdf = polygon_gdf.to_crs(river_gdf.crs)

# Perform the clipping: clip the river network to the polygon
clipped_river_gdf = gpd.clip(river_gdf, polygon_gdf)

# Save the clipped river network to a new shapefile
output_clipped_shapefile = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/River Shp/Clipped_Rivers.shp'  # Replace with the desired output file path
clipped_river_gdf.to_file(output_clipped_shapefile)

print(f"Clipped shapefile saved to {output_clipped_shapefile}")

