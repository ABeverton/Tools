# Databricks notebook source
pip install pandas geopandas shapely openpyxl

# COMMAND ----------

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the Excel file
file_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Scratch/Stations.xlsx'  # Replace with the path to your Excel file
df = pd.read_excel(file_path)

# Specify the column names for easting and northing
easting_col = 'Easting'  # Replace with your easting column name
northing_col = 'Northing'  # Replace with your northing column name

# Create a GeoDataFrame, using the easting and northing to create Point geometries
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df[easting_col], df[northing_col])
)

# Set the coordinate reference system (CRS) to British National Grid (EPSG:27700)
gdf.set_crs(epsg=27700, inplace=True)

# Save the GeoDataFrame as a shapefile
output_shp_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Scratch/Stations.shp'  # Replace with the desired output file path
gdf.to_file(output_shp_path)

print(f"Shapefile saved to {output_shp_path}")


# COMMAND ----------

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load the Excel file, skipping the first N rows (replace N with the number of rows to skip)
file_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/MIDAS data/midas-open_uk-radiation-obs_dv-202407_station-metadata.csv'
df = pd.read_csv(file_path, skiprows=48)  # Replace N with the number of rows to skip

# Specify the column names for latitude and longitude
lat_col = 'station_latitude'  # Replace with your latitude column name
lon_col = 'station_longitude'  # Replace with your longitude column name

# Create a GeoDataFrame, using the latitude and longitude to create Point geometries
gdf = gpd.GeoDataFrame(
    df, 
    geometry=gpd.points_from_xy(df[lon_col], df[lat_col])
)

# Set the CRS to WGS 84 (EPSG:4326) for lat/long or British National Grid (EPSG:27700)
gdf.set_crs(epsg=4326, inplace=True)

# Save the GeoDataFrame as a shapefile
output_shp_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Scratch/MIDAS_Stations.shp'
gdf.to_file(output_shp_path)

print(f"Shapefile saved to {output_shp_path}")

