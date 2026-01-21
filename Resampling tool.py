# Databricks notebook source
import rasterio
from rasterio.enums import Resampling
import numpy as np

# Input and output file paths
input_geotiff = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/New Clipped/chess-pe_pet_gb_1km_daily_20100101-20100131_Day_01.tif' #THis is your tif that you want to be resampled
reference_geotiff = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/Corine Land Cover/Feature_shp11_CODE12.tif' # This is one of your filesa at the correct resolution to check against.
output_geotiff = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/New Clipped/Resampled to 100m2/test.tif'

# Open the input GeoTIFF (1km²) and reference GeoTIFF (100m²)
with rasterio.open(input_geotiff) as src, rasterio.open(reference_geotiff) as ref:
    # Read the data from the input file
    data = src.read(1)
    
    # Use the transform, width, and height from the reference (100m²) GeoTIFF
    new_transform = ref.transform
    new_width = ref.width
    new_height = ref.height

    # Resample the input data to match the reference's shape and resolution
    new_data = src.read(
        out_shape=(src.count, new_height, new_width),
        resampling=Resampling.bilinear
    )

    # Update metadata based on reference GeoTIFF
    new_meta = src.meta.copy()
    new_meta.update({
        'height': new_height,
        'width': new_width,
        'transform': new_transform,
        'driver': 'GTiff',
        'dtype': new_data.dtype
    })

    # Write the output GeoTIFF, aligned to the reference grid
    with rasterio.open(output_geotiff, 'w', **new_meta) as dst:
        dst.write(new_data)

print(f"Resampled and aligned GeoTIFF saved as {output_geotiff}")


# COMMAND ----------

import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show

# Input TIFF file paths
PET_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH CHESS/New Clipped/Resampled to 100m2/test.tif'
Precip_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/HadUK Precip/Clipped/rainfall_hadukgrid_uk_1km_day_20100101-20100131_Day_01.tif'
SoilMoisture_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/UKCEH SM/AOI_Clipped/SM_201001_Day_25.tif'
LandCover_file = '/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex/Corine Land Cover/Feature_shp11_CODE12.tif'

# Open the TIFFs and collect metadata
PET = rasterio.open(PET_file)
Precip = rasterio.open(Precip_file)
SoilMoisture = rasterio.open(SoilMoisture_file)
LandCover = rasterio.open(LandCover_file)

tiffs = [PET, Precip, SoilMoisture, LandCover]
metadata = []
for src in tiffs:
    metadata.append({
        'filename': src.name,
        'crs': src.crs,
        'resolution': (src.res[0], src.res[1]),
        'bounds': src.bounds,
        'width': src.width,
        'height': src.height
    })

# Check if the coordinate systems (CRS) are the same
crs_equal = all(md['crs'] == metadata[0]['crs'] for md in metadata)

# Check if the resolutions are the same
resolutions = [md['resolution'] for md in metadata]
res_equal = all(md['resolution'] == metadata[0]['resolution'] for md in metadata)

# Check if the bounds overlap
def check_overlap(bounds1, bounds2):
    return not (bounds1.right < bounds2.left or bounds1.left > bounds2.right or 
                bounds1.top < bounds2.bottom or bounds1.bottom > bounds2.top)

overlaps = [check_overlap(metadata[0]['bounds'], md['bounds']) for md in metadata[1:]]

# Print cleaner output for comparison results
print("Comparison results:")
print(f"Same Coordinate System (CRS)? {'Yes' if crs_equal else 'No'}")

print(f"Resolutions: {resolutions[0][0]}x{resolutions[0][1]}, {resolutions[1][0]}x{resolutions[1][1]}, "
      f"{resolutions[2][0]}x{resolutions[2][1]}, {resolutions[3][0]}x{resolutions[3][1]}")
print(f"Same Resolution? {'Yes' if res_equal else 'No'}")

print(f"Overlap between PET and Precip? {'Yes' if overlaps[0] else 'No'}")
print(f"Overlap between PET and SoilMoisture? {'Yes' if overlaps[1] else 'No'}")
print(f"Overlap between PET and LandCover? {'Yes' if overlaps[2] else 'No'}")

# Plot the TIFFs for visual comparison
fig, axs = plt.subplots(1, 4, figsize=(20, 5))

axs[0].set_title('PET')
show(PET, ax=axs[0])

axs[1].set_title('Precip')
show(Precip, ax=axs[1])

axs[2].set_title('SoilMoisture')
show(SoilMoisture, ax=axs[2])

axs[3].set_title('LandCover')
show(LandCover, ax=axs[3])

plt.tight_layout()
plt.show()

