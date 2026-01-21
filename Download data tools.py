# Databricks notebook source
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import os

# Function to download files from a given URL
def download_files(url, save_directory):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all links (assumes links are directly to files)
    links = soup.find_all('a')
    
    # Iterate over each link
    for link in links:
        href = link.get('href')
        file_url = urljoin(url, href)
        
        # Check if it's a file (you may need to customize this condition)
        if '.' in href:
            # Get the filename
            filename = os.path.join(save_directory, os.path.basename(href))
            
            # Download the file
            print(f"Downloading {filename}...")
            r = requests.get(file_url, allow_redirects=True)
            open(filename, 'wb').write(r.content)
            print(f"{filename} downloaded successfully.")

# Example usage:
if __name__ == "__main__":
    # URL of the online archive
    archive_url = 'http://dap.ceda.ac.uk/thredds/fileServer/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.3.0.ceda/1km/rainfall/day/v20240514'#'https://data.ceda.ac.uk/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.3.0.ceda/1km/rainfall/day/v20240514'#https://catalogue.ceh.ac.uk/datastore/eidchub/beb62085-ba81-480c-9ed0-2d31c27ff196/'
    
    # Directory where files will be saved
    save_directory = r'/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex'
    
    # Create the save directory if it doesn't exist
    os.makedirs(save_directory, exist_ok=True)
    
    # Call the function to download files
    download_files(archive_url, save_directory)


# COMMAND ----------

import os
import requests

# CEDA authentication credentials
USERNAME = "abeverton001"  # Replace with your CEDA username
PASSWORD = "Andy2002"  # Replace with your CEDA password

# File URL
file_url = "https://dap.ceda.ac.uk/badc/ukmo-hadobs/data/insitu/MOHC/HadOBS/HadUK-Grid/v1.3.0.ceda/1km/rainfall/day/v20240514/rainfall_hadukgrid_uk_1km_day_18910101-18910131.nc"

# Directory where files will be saved
save_directory = r'/Workspace/Users/andy.beverton@environment-agency.gov.uk/Denver Complex'

# Ensure the save directory exists
os.makedirs(save_directory, exist_ok=True)

# Get the filename from the URL
filename = os.path.join(save_directory, os.path.basename(file_url))

# Start a session to handle authentication
session = requests.Session()
session.auth = (USERNAME, PASSWORD)  # HTTP Basic Authentication

# Download the file
response = session.get(file_url, stream=False)
response.raise_for_status()  # Raise an error if request fails

# Save the file in chunks
with open(filename, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

print(f"Download complete: {filename}")

