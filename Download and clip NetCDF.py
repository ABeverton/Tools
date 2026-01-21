# Databricks notebook source
pip install netCDF4 xarray beautifulsoup4 requests

# COMMAND ----------

# MAGIC %sh
# MAGIC wget -O "/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/file.nc" "https://catalogue.ceh.ac.uk/datastore/eidchub/8651771d-aa6d-4d0f-8bcd-b3be1f733852/pet/chess-pe_pet_gb_1km_daily_19610101-19610131.nc"

# COMMAND ----------

# MAGIC %sh
# MAGIC file "/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/chess-pe_pet_gb_1km_daily_19610101-19610131.nc"
# MAGIC

# COMMAND ----------

import netCDF4 as nc

# Path to the NetCDF file
netcdf_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/rainfall_hadukgrid_uk_1km_day_18910201-18910228.nc'

# Open the NetCDF file
with nc.Dataset(netcdf_path, mode='r') as dataset:
    # Print the dataset summary
    print("NetCDF Dataset Summary:")
    print(dataset)

    # List variables in the dataset
    print("\nVariables:")
    for var_name in dataset.variables:
        var = dataset.variables[var_name]
        print(f"\nVariable Name: {var_name}")
        print(f"  Dimensions: {var.dimensions}")
        print(f"  Shape: {var.shape}")
        print(f"  Data Type: {var.datatype}")
        print(f"  Attributes: {dict(var.__dict__)}")

    # Print coordinate variables if they exist
    print("\nCoordinate Variables:")
    for coord_var in ['longitude', 'latitude', 'easting', 'northing']:
        if coord_var in dataset.variables:
            var = dataset.variables[coord_var]
            print(f"\nCoordinate Variable: {coord_var}")
            print(f"  Dimensions: {var.dimensions}")
            print(f"  Shape: {var.shape}")
            print(f"  Data Type: {var.datatype}")
            print(f"  Attributes: {dict(var.__dict__)}")


# COMMAND ----------

import netCDF4 as nc
import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask
import os

plt.clf()

# Path to the NetCDF file
netcdf_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/NETCDFs/chess-pe_pet_gb_1km_daily_19760201-19760229.nc'
shapefile_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Denver_AOI.shp'  # Path to your shapefile

# Load the shapefile
shapefile = gpd.read_file(shapefile_path)

# Open the NetCDF file
with nc.Dataset(netcdf_path, mode='r') as dataset:
    # Get the variables for PET and coordinates
    pet_data = dataset.variables['pet'][:]  # Assuming the PET data is in this variable
    easting = dataset.variables['x'][:]
    northing = dataset.variables['y'][:]
    
    # Check how many days are in the dataset
    num_days = pet_data.shape[0]  # Assuming first dimension is time

    # Create a figure for side-by-side plots
    fig, axes = plt.subplots(nrows=num_days, ncols=2, figsize=(12, 3 * num_days))
    
    # Iterate through each day
    for day_index in range(num_days):
        # Get the specific day data
        pet_day = pet_data[day_index, :, :]  # Extract data for this day

        # Plotting the full area
        ax_full = axes[day_index, 0]  # Left plot for full area
        ax_full.invert_yaxis()
        im_full = ax_full.imshow(pet_day, cmap='viridis', extent=(easting[0], easting[-1], northing[-1], northing[0]), vmin=0)
        
        # Add the shapefile boundary for better visualization
        shapefile.boundary.plot(ax=ax_full, color='red')

        ax_full.set_title(f'NetCDF Data for Day {day_index + 1}')
        plt.colorbar(im_full, ax=ax_full, label='Potential Evapotranspiration (PET)')

        # Clip the raster using the shapefile for the current day
        with rasterio.open(netcdf_path) as src:
            # Get the shape geometries for clipping
            shapes = [feature["geometry"] for feature in shapefile.__geo_interface__['features']]
            out_image, out_transform = mask(src, shapes, crop=True)
            
            # Use the first band of out_image since it could have multiple bands
            #out_image = np.squeeze(out_image)  # Remove single-dimensional entries from the shape

            # Flip the clipped image vertically for correct orientation
            out_image = np.flip(out_image[day_index], axis=0)

            # Get the new extents for the clipped image
            minx, miny, maxx, maxy = shapefile.total_bounds

            # Plot the clipped raster
            ax_clipped = axes[day_index, 1]  # Right plot for clipped area
            im_clipped = ax_clipped.imshow(out_image, cmap='viridis', extent=(minx, maxx, maxy, miny), vmin=0)
            ax_clipped.invert_yaxis()
            # Add the shapefile boundary for better visualization
            shapefile.boundary.plot(ax=ax_clipped, color='red')

            ax_clipped.set_title(f'Clipped NetCDF Data for Day {day_index + 1}')
            plt.colorbar(im_clipped, ax=ax_clipped, label='Potential Evapotranspiration (PET)')

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()


# COMMAND ----------



# COMMAND ----------

import netCDF4 as nc
import rasterio
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from rasterio.mask import mask
import os
from pathlib import Path

# Configuration
netcdf_folder = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/NETCDFs/'
shapefile_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Denver_AOI.shp'  # Path to your shapefile
output_folder = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/2010_AOI'  # Specify the output folder for GeoTIFFs
debug_plot = False  # Set to True to enable plotting

# Load the shapefile
shapefile = gpd.read_file(shapefile_path)

# Iterate through all NetCDF files in the specified folder
for netcdf_file in Path(netcdf_folder).glob('*.nc'):
    print(f'Processing {netcdf_file.name}')
    
    # Open the NetCDF file
    with nc.Dataset(netcdf_file, mode='r') as dataset:
        # Get the variables for PET and coordinates
        pet_data = dataset.variables['pet'][:]  # Assuming the PET data is in this variable
        easting = dataset.variables['x'][:]
        northing = dataset.variables['y'][:]
        
        # Check how many days are in the dataset
        num_days = pet_data.shape[0]  # Assuming first dimension is time

        # Create a figure for side-by-side plots if debug_plot is True
        if debug_plot:
            fig, axes = plt.subplots(nrows=num_days, ncols=2, figsize=(12, 3 * num_days))

        # Iterate through each day
        for day_index in range(num_days):
            # Get the specific day data
            pet_day = pet_data[day_index, :, :]  # Extract data for this day

            # Plotting the full area
            if debug_plot:
                ax_full = axes[day_index, 0]  # Left plot for full area
                ax_full.invert_yaxis()
                im_full = ax_full.imshow(pet_day, cmap='viridis', extent=(easting[0], easting[-1], northing[-1], northing[0]), vmin=0)
                
                # Add the shapefile boundary for better visualization
                shapefile.boundary.plot(ax=ax_full, color='red')

                ax_full.set_title(f'NetCDF Data for Day {day_index + 1}')
                plt.colorbar(im_full, ax=ax_full, label='Potential Evapotranspiration (PET)')

            # Clip the raster using the shapefile for the current day
            with rasterio.open(netcdf_file) as src:
                # Get the shape geometries for clipping
                shapes = [feature["geometry"] for feature in shapefile.__geo_interface__['features']]
                out_image, out_transform = mask(src, shapes, crop=True)
                
                # Flip the clipped image vertically for correct orientation
                out_image = np.flip(out_image[day_index], axis=0)
                print(out_image.shape)
                # Get the new extents for the clipped image
                minx, miny, maxx, maxy = shapefile.total_bounds

                # Save the clipped raster as GeoTIFF
                output_filename = f"{netcdf_file.stem}_Day_{day_index + 1:02d}.tif"
                output_path = os.path.join(output_folder, output_filename)

                with rasterio.open(
                    output_path, 'w',
                    driver='GTiff',
                    height=out_image.shape[0],
                    width=out_image.shape[1],
                    count=1,
                    dtype=out_image.dtype,
                    crs=src.crs,
                    transform=out_transform
                ) as dst:
                    dst.write(out_image, 1)
                print(f'Saved clipped GeoTIFF to {output_path}')

            # Plot the clipped raster if debug_plot is True
            if debug_plot:
                ax_clipped = axes[day_index, 1]  # Right plot for clipped area
                im_clipped = ax_clipped.imshow(out_image, cmap='viridis', extent=(minx, maxx, maxy, miny), vmin=0)
                ax_clipped.invert_yaxis()

                # Add the shapefile boundary for better visualization
                shapefile.boundary.plot(ax=ax_clipped, color='red')

                ax_clipped.set_title(f'Clipped NetCDF Data for Day {day_index + 1}')
                plt.colorbar(im_clipped, ax=ax_clipped, label='Potential Evapotranspiration (PET)')

        if debug_plot:
            plt.tight_layout()  # Adjust layout to prevent overlap
            plt.show()



# COMMAND ----------

import rasterio
import matplotlib.pyplot as plt

# Path to the GeoTIFF file
geotiff_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/AP17_Clipped/chess-pe_pet_gb_1km_daily_19760101-19760131_Day_18.tif'  # Update this with the actual path to your GeoTIFF

# Open the GeoTIFF file
with rasterio.open(geotiff_path) as src:
    # Read the data
    data = src.read(1)  # Read the first band (assuming single-band)
    
    # Get the extent of the data for proper display
    extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

# Plot the GeoTIFF data
plt.figure(figsize=(10, 6))
plt.imshow(np.flip(data,axis=0), cmap='viridis', extent=extent, vmin=0)  # Change vmin as needed
plt.colorbar(label='Value')  # Adjust label as necessary
plt.title('GeoTIFF Data Plot')
plt.xlabel('Easting (m)')
plt.ylabel('Northing (m)')
plt.axis('equal')  # Maintain aspect ratio
plt.show()


# COMMAND ----------

import geopandas as gpd

def calculate_area_of_aoi(shapefile_path):
    """
    Calculate the area of the Area of Interest (AOI) from a shapefile.

    Parameters:
    - shapefile_path (str): Path to the AOI shapefile.

    Returns:
    - float: Total area in square meters.
    """
    # Read the shapefile using geopandas
    aoi = gpd.read_file(shapefile_path)

    # Ensure the geometry is in a projected coordinate system (meters)
    if aoi.crs.is_geographic:
        aoi = aoi.to_crs(epsg=27700)  # Convert to a suitable projection (e.g., Mercator)

    # Calculate the area in square meters
    aoi['area_m2'] = aoi.geometry.area
    total_area = aoi['area_m2'].sum()  # Sum the areas of all features

    return total_area

# Example usage
if __name__ == "__main__":
    shapefile_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Denver_AOI.shp'  # Path to your AOI shapefile
    area_m2 = calculate_area_of_aoi(shapefile_path)
    print(f"Total area of the AOI: {area_m2:.2f} m²")
    print(area_m2/1000000,'Km^2')


# COMMAND ----------

#1 kg/m2 is equivalent to 1mm. 
#Therefore multiply each cell value by 1,000,000m2 (1km2) to create volume of water lost (m3) from each cell.
#Divide by number of seconds in a day (86400)

import rasterio

# Load the GeoTIFF file
file_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/AP17_Clipped/chess-pe_pet_gb_1km_daily_19760101-19760131_Day_01.tif'

with rasterio.open(file_path) as src:
    # Read the first band as a 2D array (you can change the band if needed)
    tiff_data = src.read(1)

# Now `tiff_data` is a 2D numpy array containing the raster values
print(np.min(tiff_data))

#Change -99999 to nan
tiff_data = np.where((tiff_data == -99999.0), np.nan,tiff_data)
print(np.min(tiff_data))

volume_array = tiff_data * 1000000
total_volume = np.nansum(volume_array)
print(total_volume)
flow = total_volume / 864000
print(flow)



# COMMAND ----------

import os
import rasterio
import pandas as pd
import numpy as np
from glob import glob

# Directory containing the GeoTIFF files
directory = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/'

# Create a list to store daily evaporation values and corresponding dates
evaporation_data = []

# Get a sorted list of GeoTIFF files
tiff_files = sorted(glob(os.path.join(directory, '*.tif')))

# Iterate through the sorted GeoTIFF files
for tiff_file in tiff_files:
    # Extract the date range and day from the filename
    filename = os.path.basename(tiff_file)
    date_range = filename.split('_')[-3]  # e.g., '19760201-19760229'
    day = filename.split('_')[-1]          # e.g., 'Day_13'
    
    # Extract the starting date from the date range
    date_str = date_range.split('-')  # e.g., '19760201'
    #print(date_str[0],day)
    date = str(date_str[0])[:6]+day[:2]
    date = pd.to_datetime(date, format='%Y%m%d')
    print('the date is',date)

    # Read the GeoTIFF file
    with rasterio.open(tiff_file) as src:
        # Read the data from the first band
        data = src.read(1)
        data[data == -99999.0] = np.nan
        #print(np.nanmin(data),np.nanmax(data))
        
        # Calculate the total daily rate of evaporation in mm
        # Convert kg/m² to mm (1 kg/m² = 1 mm)
        daily_evaporation = np.nansum(data)  # Sum the pixel values
        
    # Append the date and daily evaporation to the list
    evaporation_data.append({'date': date, 'evaporation_mm': daily_evaporation})

# Create a DataFrame from the evaporation data
evaporation_df = pd.DataFrame(evaporation_data)

# Save the DataFrame to a CSV file
output_csv_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation.csv'
evaporation_df.to_csv(output_csv_path, index=False)

print(f'Daily evaporation data saved to {output_csv_path}')


# COMMAND ----------

import pandas as pd

# Define the input and output file paths
input_csv = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation.csv'  # Change to your input file path
output_csv = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation_m3_per_s.csv'   # Change to your output file path

# Define the area over which the kg/m² is measured in square meters
area = area_m2  # Change this to your actual area in m²

# Load the CSV file containing kg/m² data
df = pd.read_csv(input_csv)

# Check if the expected column 'mass_kg_m2' exists
if 'evaporation_mm' not in df.columns:
    raise ValueError("The expected column 'evaporation_mm' is missing from the CSV file.")

# Density of water in kg/m³
density = 1000  # Density of water

# Convert kg/m² to m³/s
df['flow_m3_s'] = (df['evaporation_mm'] * area) / (density * 86400)

# Save the results to a new CSV file
df.to_csv(output_csv, index=False)

print(f"Conversion complete. The results are saved in '{output_csv}'")


# COMMAND ----------

import pandas as pd

# Define the input and output file paths
input_csv = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation.csv'  # Change to your input file path
output_csv = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation_flow.csv'   # Change to your output file path

# Define the area over which the evaporation is measured in square meters
# For example, if your area is 1000 m², set area = 1000
area = area_m2  # Adjust this value according to your area

# Load the CSV file containing mm/day data
df = pd.read_csv(input_csv)

# Check if the expected column 'evaporation_mm_day' exists
if 'evaporation_mm' not in df.columns:
    raise ValueError("The expected column 'evaporation_mm_day' is missing from the CSV file.")

# Convert mm/day to m³/s
df['evaporation_m3_s'] = (df['evaporation_mm'] * area) / 86400

# Save the results to a new CSV file
df.to_csv(output_csv, index=False)

print(f"Conversion complete. The results are saved in '{output_csv}'")



# COMMAND ----------

import pandas as pd

# Path to the CSV file containing daily evaporation in mm/day
input_csv_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation.csv'

# Load the CSV file into a DataFrame
evaporation_df = pd.read_csv(input_csv_path)

# Specify the area over which the evaporation is measured (in m²)
# For example, if you have a specific catchment area, use that value
# Here, assuming an area of 1 km² (1,000,000 m²) as an example
area_m2 = 1_000_000  # Replace with your actual area if known

# Convert mm/day to m³/day
evaporation_df['evaporation_m3_day'] = evaporation_df['evaporation_mm'] * area_m2 * 0.001  # 1 mm = 0.001 m

# Convert m³/day to m³/s
evaporation_df['evaporation_m3_s'] = evaporation_df['evaporation_m3_day'] / 86400  # Convert to m³/s

# Save the updated DataFrame to a new CSV file
output_csv_path = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation_m3_s.csv'
evaporation_df[['date', 'evaporation_m3_s']].to_csv(output_csv_path, index=False)

print(f'Daily evaporation data converted to m³/s and saved to {output_csv_path}')


# COMMAND ----------

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_river_flows_and_evaporation(flow_csv_file, evaporation_csv_file, year, start_month=None, end_month=None, outflow_column=None, ymin=None, ymax=None, custom_legend_labels=None, font_size=14):
    # Load the river flow data
    flow_df = pd.read_csv(flow_csv_file, parse_dates=['date'])
    flow_df['date'] = pd.to_datetime(flow_df['date'], errors='coerce')  # Handle parsing errors
    print("River Flow Data:")
    print(flow_df.head())  # Debug: Check the structure of the flow data
    
    flow_df_year = flow_df[flow_df['date'].dt.year == year]
    
    if start_month and end_month:
        flow_df_year = flow_df_year[(flow_df_year['date'].dt.month >= start_month) & (flow_df_year['date'].dt.month <= end_month)]
    
    flow_df_year.set_index('date', inplace=True)

    # Load the evaporation data
    evaporation_df = pd.read_csv(evaporation_csv_file, parse_dates=['date'])
    evaporation_df['date'] = pd.to_datetime(evaporation_df['date'], errors='coerce')  # Handle parsing errors
    print("\nEvaporation Data:")
    print(evaporation_df.head())  # Debug: Check the structure of the evaporation data
    evaporation_df.set_index('date', inplace=True)

    # Create the figure and set the background to white
    fig, ax = plt.subplots(figsize=(15, 10))
    fig.patch.set_facecolor('white')  # Set the figure background to white
    ax.set_facecolor('white')         # Set the plot background to white

    # Plot inflows as stacked area plot
    inflow_series = flow_df_year.drop(columns=[outflow_column]) if outflow_column and outflow_column in flow_df_year.columns else flow_df_year
    inflow_series.plot(kind='area', stacked=True, ax=ax, cmap='tab20c', alpha=0.7)
    
    # Plot outflow as a black line if available
    if outflow_column and outflow_column in flow_df_year.columns:
        plt.plot(flow_df_year.index, flow_df_year[outflow_column], color='black', linewidth=1.5, label=outflow_column)

    # Plot evaporation as a line plot (in m³/s)
    plt.plot(evaporation_df.index, evaporation_df['evaporation_m3_s'], color='blue', linewidth=2, label='Evaporation (m³/s)')

    # Set labels and title with the provided font size
    plt.xlabel(f'Observed year: {year}', fontsize=font_size)
    plt.ylabel('Mean Daily Flow / Evaporation (m³/s)', fontsize=font_size)

    # Set y-axis limits
    if ymin is not None and ymax is not None:
        plt.ylim(ymin, ymax)

    # Format x-axis for months
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    plt.gcf().autofmt_xdate()

    # Set font size for ticks
    ax.tick_params(axis='both', which='major', labelsize=font_size)

    # Customize the grid
    plt.grid(True, linestyle='--', linewidth=0.7, color='lightgrey')
    ax.set_axisbelow(True)

    # Add a frame around the plot
    for spine in ax.spines.values():
        spine.set_edgecolor('black')  # Set the color of the frame
        spine.set_linewidth(0.5)        # Set the thickness of the frame

    # Set custom legend labels if provided, else use default
    if custom_legend_labels is not None:
        handles, labels = ax.get_legend_handles_labels()
        if len(custom_legend_labels) == len(labels):
            ax.legend(handles, custom_legend_labels + ['Evaporation (m³/s)'], title='Tributaries & Outflow', bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, framealpha=1, facecolor='white', fontsize=font_size)
        else:
            print("Warning: Number of custom legend labels does not match the number of series.")
    else:
        plt.legend(title='Tributaries & Outflow', loc='upper left', frameon=True, framealpha=1, facecolor='white', fontsize=font_size)
    
    # Show the plot
    plt.tight_layout()
    plt.show()

# Example usage
flow_csv_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/Flow obs data/Raw flows/Raw_flows_combined_NO_ELY_OUSE.csv'
evaporation_csv_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/Clipped/daily_evaporation_flow.csv'
year = 1976
start_month = 5
end_month = 9
outflow_column = 'id_33035_flow_1'
ymin = 0
ymax = 10

custom_legend_labels = ['Lark', 'Rhee', 'Snail', 'Stringside', 'Wissey', 'Little Ouse','Lea Brooke', 'Cam', 'Granta', 'Swafham Lode', 'Quy Water', 'Denver']

# Control font size with this variable
font_size = 18

plot_river_flows_and_evaporation(flow_csv_file, evaporation_csv_file, year, start_month, end_month, outflow_column, ymin, ymax, custom_legend_labels, font_size)

