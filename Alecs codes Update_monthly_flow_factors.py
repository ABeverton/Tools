# Databricks notebook source
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import csv
import re
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import matplotlib.colors as mcolors 
import matplotlib.dates as mdates
from matplotlib.patches import Wedge, Patch


# COMMAND ----------

flow_dict = {
    "Input_name":["Black Beck","Blelham Beck","Cunsey Beck","Cunsey Beck Esthwaite","Esthwaite Hall Beck","How Beck","Mill Beck","River Brathay 1","River Brathay 2","River Leven 1", "River Leven 2","River Rothay","Smooth Beck","Trout Beck", "Unnamed river Esthwaite site"],
    "Input_cc_path":["335750_497550_climate_mean_flows_FULL_LDG_landscape","337000_501850_climate_mean_flows_FULL_LDG_landscape","338450_493600_climate_mean_flows_FULL_LDG_landscape","336550_495250_climate_mean_flows_FULL_LDG_landscape","335900_495900_climate_mean_flows_FULL_LDG_landscape","335600_497200_climate_mean_flows_FULL_LDG_landscape","340200_497700_climate_mean_flows_FULL_LDG_landscape","337000_503550_climate_mean_flows_FULL_LDG_landscape","337150_503150_climate_mean_flows_FULL_LDG_landscape","336850_486400_climate_mean_flows_FULL_LDG_landscape","337950_486950_climate_mean_flows_FULL_LDG_landscape","337100_503650_climate_mean_flows_FULL_LDG_landscape","335950_497400_climate_mean_flows_FULL_LDG_landscape","339500_499600_climate_mean_flows_FULL_LDG_landscape","335600_496800_climate_mean_flows_FULL_LDG_landscape"],
    "Input_time_series_path":["Catchment_at_335750497550_time_series_FULL_LDG","Catchment_at_337000501850_time_series_FULL_LDG","Catchment_at_338450493600_time_series_FULL_LDG","Catchment_at_336550495250_time_series_FULL_LDG","Catchment_at_335900495900_time_series_FULL_LDG","Catchment_at_335600497200_time_series_FULL_LDG","Catchment_at_340200497700_time_series_FULL_LDG","Catchment_at_337000503550_time_series_FULL_LDG","Catchment_at_337150503150_time_series_FULL_LDG","Catchment_at_336850486400_time_series_FULL_LDG","Catchment_at_337950486950_time_series_FULL_LDG","Catchment_at_337100503650_time_series_FULL_LDG","Catchment_at_335950497400_time_series_FULL_LDG","Catchment_at_339500499600_time_series_FULL_LDG","Catchment_at_335600496800_time_series_FULL_LDG"]
}


# COMMAND ----------

index = 13

# COMMAND ----------

# Define the input future monthly flow path
Qube_future_flow_path = f'/Workspace/Users/alec.hutchings@environment-agency.gov.uk/Windermere_data/Hydrological/Qube_data/{flow_dict["Input_name"][index]}/{flow_dict["Input_cc_path"][index]}.csv'
# Define the input present time series flow path
Qube_time_series_path = f'/Workspace/Users/alec.hutchings@environment-agency.gov.uk/Windermere_data/Hydrological/{flow_dict["Input_name"][index]}/{flow_dict["Input_time_series_path"][index]}.csv'
Output_folder_path = f'/Workspace/Users/alec.hutchings@environment-agency.gov.uk/Windermere_data/Hydrological/Qube_data/{flow_dict["Input_name"][index]}'

print(Qube_future_flow_path)
print(Qube_time_series_path)
print(Output_folder_path)

# COMMAND ----------

# Read in the dataframes
Qube_future_flow = pd.read_csv(Qube_future_flow_path)
Qube_future_flow_df = pd.DataFrame(Qube_future_flow)
Qube_time_series = pd.read_csv(Qube_time_series_path)
Qube_time_series_df = pd.DataFrame(Qube_time_series)

# COMMAND ----------

Qube_time_series_df.head()

# COMMAND ----------

# Convert date to datatime format of time series
Qube_time_series_df['Date'] = pd.to_datetime(Qube_time_series_df['Date'])

# Extract the year, month, day, and day-month and create a new column
Qube_time_series_df['Year'] = Qube_time_series_df['Date'].dt.year
Qube_time_series_df['Month'] = Qube_time_series_df['Date'].dt.month
Qube_time_series_df['Day'] = Qube_time_series_df['Date'].dt.day
Qube_time_series_df['Day-Month'] = Qube_time_series_df['Date'].dt.strftime('%d-%m')

# COMMAND ----------

display(Qube_future_flow_df)

# COMMAND ----------

# Create a set of factors based on each ensemble (near and far)
columns_to_ratio = ['Near - RCM01 (m3/s)', 'Near - RCM04 (m3/s)', 'Near - RCM05 (m3/s)','Near - RCM06 (m3/s)','Near - RCM07 (m3/s)','Near - RCM08 (m3/s)','Near - RCM09 (m3/s)','Near - RCM10 (m3/s)','Near - RCM11 (m3/s)','Near - RCM12 (m3/s)','Near - RCM13 (m3/s)','Near - RCM15 (m3/s)','Far - RCM01 (m3/s)','Far - RCM04 (m3/s)','Far - RCM05 (m3/s)','Far - RCM06 (m3/s)','Far - RCM07 (m3/s)','Far - RCM08 (m3/s)','Far - RCM09 (m3/s)','Far - RCM10 (m3/s)','Far - RCM11 (m3/s)','Far - RCM12 (m3/s)','Far - RCM13 (m3/s)','Far - RCM15 (m3/s)'] 

# Calculate ratios for each column
for col in columns_to_ratio:
    new_col_name = f'{col}_uplift'
    Qube_future_flow_df[new_col_name] = Qube_future_flow_df[col] / Qube_future_flow_df['Natural - Full POR (m3/s)']

# # Plot each column against 'Annual'
# plt.figure(figsize=(10, 6))  # Optional: adjust figure size

# for col in columns_to_ratio:
#     new_col_name = f'{col}_uplift'
#     plt.plot(Qube_future_flow_df['Month'], Qube_future_flow_df[new_col_name], marker='o', linestyle = "",label=new_col_name)

# # Set title and labels
# plt.title('Ratio of Flow Columns vs Annual')
# plt.xlabel('Annual')
# plt.ylabel('Ratio')
# #plt.legend()  # Optional: add legend

# COMMAND ----------

# Merge the monthly factors with the time series data
merged_flow_df = pd.merge(Qube_time_series_df,Qube_future_flow_df,  on='Month', how='inner')
# Drop unnecessary columns
merged_flow_df = merged_flow_df.drop(columns=columns_to_ratio)

# COMMAND ----------

display(merged_flow_df)

# COMMAND ----------

# Create the updated flows for near and far future
uplift_cols = ['Near - RCM01 (m3/s)_uplift', 'Near - RCM04 (m3/s)_uplift', 'Near - RCM05 (m3/s)_uplift','Near - RCM06 (m3/s)_uplift','Near - RCM07 (m3/s)_uplift','Near - RCM08 (m3/s)_uplift','Near - RCM09 (m3/s)_uplift','Near - RCM10 (m3/s)_uplift','Near - RCM11 (m3/s)_uplift','Near - RCM12 (m3/s)_uplift','Near - RCM13 (m3/s)_uplift','Near - RCM15 (m3/s)_uplift','Far - RCM01 (m3/s)_uplift','Far - RCM04 (m3/s)_uplift','Far - RCM05 (m3/s)_uplift','Far - RCM06 (m3/s)_uplift','Far - RCM07 (m3/s)_uplift','Far - RCM08 (m3/s)_uplift','Far - RCM09 (m3/s)_uplift','Far - RCM10 (m3/s)_uplift','Far - RCM11 (m3/s)_uplift','Far - RCM12 (m3/s)_uplift','Far - RCM13 (m3/s)_uplift','Far - RCM15 (m3/s)_uplift'] 

merged_df_corrected = merged_flow_df.copy()

for col in uplift_cols:
    new_col_name = f'{col}_corrected'
    merged_df_corrected[new_col_name] = merged_df_corrected[col] * merged_df_corrected['Natural flow (m3/s)']

# Drop unnecessary columns
merged_df_corrected = merged_df_corrected.drop(columns=uplift_cols)

# COMMAND ----------

display(merged_df_corrected)

# COMMAND ----------

# Subset for years of interest
factored_flows_period = merged_df_corrected[(merged_df_corrected['Year'] >= 2014) & (merged_df_corrected['Year'] <= 2018)]
# Sort by date
factored_flows_period_sorted = factored_flows_period.sort_values(by='Date')

display(factored_flows_period)

# COMMAND ----------

Near_ensemble = ['Near - RCM01 (m3/s)_uplift_corrected', 'Near - RCM04 (m3/s)_uplift_corrected', 'Near - RCM05 (m3/s)_uplift_corrected','Near - RCM06 (m3/s)_uplift_corrected','Near - RCM07 (m3/s)_uplift_corrected','Near - RCM08 (m3/s)_uplift_corrected','Near - RCM09 (m3/s)_uplift_corrected','Near - RCM10 (m3/s)_uplift_corrected','Near - RCM11 (m3/s)_uplift_corrected','Near - RCM12 (m3/s)_uplift_corrected','Near - RCM13 (m3/s)_uplift_corrected','Near - RCM15 (m3/s)_uplift_corrected'] 

# Determine mean, min, and max of near ensemble
factored_flows_period_sorted['Average_ensemble_flow_near'] = factored_flows_period_sorted[Near_ensemble].mean(axis=1)
factored_flows_period_sorted['Median_ensemble_flow_near'] = factored_flows_period_sorted[Near_ensemble].median(axis=1)
factored_flows_period_sorted['Minimum_ensemble_flow_near'] = factored_flows_period_sorted[Near_ensemble].min(axis=1)
factored_flows_period_sorted['Maximum_ensemble_flow_near'] = factored_flows_period_sorted[Near_ensemble].max(axis=1)

Far_ensemble = ['Far - RCM01 (m3/s)_uplift_corrected', 'Far - RCM04 (m3/s)_uplift_corrected', 'Far - RCM05 (m3/s)_uplift_corrected','Far - RCM06 (m3/s)_uplift_corrected','Far - RCM07 (m3/s)_uplift_corrected','Far - RCM08 (m3/s)_uplift_corrected','Far - RCM09 (m3/s)_uplift_corrected','Far - RCM10 (m3/s)_uplift_corrected','Far - RCM11 (m3/s)_uplift_corrected','Far - RCM12 (m3/s)_uplift_corrected','Far - RCM13 (m3/s)_uplift_corrected','Far - RCM15 (m3/s)_uplift_corrected'] 

# Determine mean, min, and max of far ensemble
factored_flows_period_sorted['Average_ensemble_flow_far'] = factored_flows_period_sorted[Far_ensemble].mean(axis=1)
factored_flows_period_sorted['Median_ensemble_flow_far'] = factored_flows_period_sorted[Far_ensemble].median(axis=1)
factored_flows_period_sorted['Minimum_ensemble_flow_far'] = factored_flows_period_sorted[Far_ensemble].min(axis=1)
factored_flows_period_sorted['Maximum_ensemble_flow_far'] = factored_flows_period_sorted[Far_ensemble].max(axis=1)

# Set the figure size and create subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(24, 24), sharex=False, sharey = True)

# Plot recorded natural flow
ax1.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Natural flow (m3/s)'], 
         linestyle="-", color='black')
ax1.set_title('Natural Flow Over Time', fontsize=16)
ax1.set_ylabel('Flow (m³/s)', fontsize=14)
ax1.tick_params(axis='both', which='major', labelsize=12)
ax1.grid(True)

# Plot near ensemble average and range
ax2.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Average_ensemble_flow_near'], 
         linestyle="-", color='red', label='Average Ensemble Flow (Near)')
ax2.fill_between(
    factored_flows_period_sorted['Date'],
    factored_flows_period_sorted['Minimum_ensemble_flow_near'],
    factored_flows_period_sorted['Maximum_ensemble_flow_near'],
    color='pink', alpha=0.5, label='Ensemble Range (Near)'
)
ax2.set_title('Near Ensemble Flow Over Time', fontsize=16)
ax2.set_ylabel('Flow (m³/s)', fontsize=14)
ax2.tick_params(axis='both', which='major', labelsize=12)
ax2.legend(fontsize=12)
ax2.grid(True)

# Plot far ensemble average and range
ax3.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Average_ensemble_flow_far'], 
         linestyle="-", color='blue', label='Average Ensemble Flow (Far)')
ax3.fill_between(
    factored_flows_period_sorted['Date'],
    factored_flows_period_sorted['Minimum_ensemble_flow_far'],
    factored_flows_period_sorted['Maximum_ensemble_flow_far'],
    color='lightblue', alpha=0.5, label='Ensemble Range (Far)'
)
ax3.set_title('Far Ensemble Flow Over Time', fontsize=16)
ax3.set_ylabel('Flow (m³/s)', fontsize=14)
ax3.set_xlabel('Date', fontsize=14)
ax3.tick_params(axis='both', which='major', labelsize=12)
ax3.legend(fontsize=12)
ax3.grid(True)

# Adjust layout and display the plot
plt.tight_layout()

# Construct the full path for saving
output_flow_figure = f"{Output_folder_path}/{flow_dict['Input_name'][index]}_flow_alterations.png"

# Save the figure
plt.savefig(output_flow_figure, dpi=300, bbox_inches='tight')
plt.show()


# COMMAND ----------

factored_flows_period_sorted['Near_anomaly'] = factored_flows_period_sorted['Average_ensemble_flow_near'] - factored_flows_period_sorted['Natural flow (m3/s)']
factored_flows_period_sorted['Far_anomaly'] = factored_flows_period_sorted['Average_ensemble_flow_far'] - factored_flows_period_sorted['Natural flow (m3/s)']

fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(24,16), sharex=True, sharey=True)

ax1.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Near_anomaly'], linestyle = "-",color = 'red')
ax1.set_title('Flow anomaly - near future', fontsize=16)
ax1.set_ylabel('Flow difference from present day (m³/s)', fontsize=14)
ax1.tick_params(axis='both', which='major', labelsize=12)
ax1.grid(True)


ax2.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Far_anomaly'], linestyle = "-",color = 'blue')
ax2.set_title('Flow anomaly - near future', fontsize=16)
ax2.set_ylabel('Flow difference from present day (m³/s)', fontsize=14)
ax2.set_xlabel('Date',fontsize = 14)
ax2.tick_params(axis='both', which='major', labelsize=12)
ax2.grid(True)

# Construct the full path for saving
output_anomaly_figure = f"{Output_folder_path}/{flow_dict['Input_name'][index]}_flow_anomalies.png"

# Save the figure
plt.savefig(output_anomaly_figure, dpi=300, bbox_inches='tight')
plt.show()


# COMMAND ----------

factored_flows_period_sorted['Near_percent_anomaly'] = (factored_flows_period_sorted['Near_anomaly']/factored_flows_period_sorted['Natural flow (m3/s)'])*100
factored_flows_period_sorted['Far_percent_anomaly'] = (factored_flows_period_sorted['Far_anomaly']/factored_flows_period_sorted['Natural flow (m3/s)'])*100

# fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(24,16), sharex=True)

# ax1.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Near_percent_anomaly'], linestyle = "-",color = 'red')
# ax2.plot(factored_flows_period_sorted['Date'], factored_flows_period_sorted['Far_percent_anomaly'], linestyle = "-",color = 'blue')

# COMMAND ----------

columns_to_remove = ['Near - RCM01 (m3/s)_uplift_corrected', 'Near - RCM04 (m3/s)_uplift_corrected', 'Near - RCM05 (m3/s)_uplift_corrected','Near - RCM06 (m3/s)_uplift_corrected','Near - RCM07 (m3/s)_uplift_corrected','Near - RCM08 (m3/s)_uplift_corrected','Near - RCM09 (m3/s)_uplift_corrected','Near - RCM10 (m3/s)_uplift_corrected','Near - RCM11 (m3/s)_uplift_corrected','Near - RCM12 (m3/s)_uplift_corrected','Near - RCM13 (m3/s)_uplift_corrected','Near - RCM15 (m3/s)_uplift_corrected','Far - RCM01 (m3/s)_uplift_corrected', 'Far - RCM04 (m3/s)_uplift_corrected', 'Far - RCM05 (m3/s)_uplift_corrected','Far - RCM06 (m3/s)_uplift_corrected','Far - RCM07 (m3/s)_uplift_corrected','Far - RCM08 (m3/s)_uplift_corrected','Far - RCM09 (m3/s)_uplift_corrected','Far - RCM10 (m3/s)_uplift_corrected','Far - RCM11 (m3/s)_uplift_corrected','Far - RCM12 (m3/s)_uplift_corrected','Far - RCM13 (m3/s)_uplift_corrected','Far - RCM15 (m3/s)_uplift_corrected','Near_anomaly', 'Far_anomaly','Near_percent_anomaly','Far_percent_anomaly','Natural - Full POR (m3/s)','Day-Month'] 

cleaned_df = factored_flows_period_sorted.copy()
cleaned_df = cleaned_df.drop(columns=columns_to_remove)

display(cleaned_df)

# COMMAND ----------

cleaned_df.to_csv(f"{Output_folder_path}/{flow_dict['Input_name'][index]}_cleaned.csv")

# COMMAND ----------

monthly_averages = cleaned_df.groupby('Month').agg({
    'Natural flow (m3/s)': 'mean',
    'Average_ensemble_flow_near': 'mean',
    'Average_ensemble_flow_far': 'mean'
}).reset_index()

# COMMAND ----------

import calendar

monthly_averages['Month_name'] = monthly_averages['Month'].apply(lambda x: calendar.month_name[x])

plt.figure(figsize=(10, 6))
plt.plot(monthly_averages['Month_name'], monthly_averages['Natural flow (m3/s)'], marker='o', label='Natural Flow')
plt.plot(monthly_averages['Month_name'], monthly_averages['Average_ensemble_flow_near'], marker='o', label='Average Ensemble Flow Near')
plt.plot(monthly_averages['Month_name'], monthly_averages['Average_ensemble_flow_far'], marker='o', label='Average Ensemble Flow Far')
plt.legend()
plt.xlabel('Month',fontsize = 14)
plt.xticks(rotation=45)
plt.ylabel('Mean flow (m3/s)',fontsize = 14)

# Construct the full path for saving
output_monthly_figure = f"{Output_folder_path}/{flow_dict['Input_name'][index]}_monthly_averages.png"

# Save the figure
plt.savefig(output_monthly_figure, dpi=300, bbox_inches='tight')
plt.show()

# COMMAND ----------

monthly_averages.to_csv(f"{Output_folder_path}/{flow_dict['Input_name'][index]}_monthly_averages.csv")

# COMMAND ----------

# # Set up the figure and axes
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12), sharex=True)

# # Plot the data
# #ax1.plot(factored_flows_period_sorted['Day-Month'], factored_flows_period_sorted['Natural flow (m3/s)'], linestyle="-", color='black', label='Natural flow')
# ax1.plot(factored_flows_period_sorted['Day-Month'], factored_flows_period_sorted['Average_ensemble_flow'], linestyle="-", color='red', label='Average ensemble flow')

# # Fill between Minimum and Maximum ensemble flows
# ax1.fill_between(
#     factored_flows_period_sorted['Day-Month'],
#     factored_flows_period_sorted['Minimum_ensemble_flow'],
#     factored_flows_period_sorted['Maximum_ensemble_flow'],
#     color='lightgray', alpha=0.5, label='Ensemble range'
# )

# # Set labels and title
# ax1.set_ylabel('Flow (m3/s)')
# ax1.set_title('Ensemble Flow with Min and Max Ranges')
# ax1.legend()

# ax1.set_xticks(factored_flows_period_sorted['Day-Month'][::31])
# ax1.tick_params(axis='x', rotation=45)

# COMMAND ----------

# # Set up the figure and axes
# fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

# # Define a color map for different years
# years = factored_flows_period_sorted['Year'].unique()
# colors = plt.cm.viridis_r(np.linspace(0, 1, len(years)))  # Choose a colormap and adjust as needed

# # Plot each year with different colors
# for i, year in enumerate(years):
#     year_data = factored_flows_period_sorted[factored_flows_period_sorted['Year'] == year]
    
#     # Plot Average Ensemble Flow
#     ax1.plot(year_data['Day-Month'], year_data['Average_ensemble_flow'], linestyle="-", color=colors[i], label=f'Average Ensemble Flow {year}')
    
#     # Fill between Minimum and Maximum Ensemble Flows
#     ax1.fill_between(
#         year_data['Day-Month'],
#         year_data['Minimum_ensemble_flow'],
#         year_data['Maximum_ensemble_flow'],
#         color=colors[i], alpha=0.3
#     )

# # Set labels and title
# ax1.set_ylabel('Flow (m3/s)')
# ax1.set_title('Ensemble Flow with Min and Max Ranges by Year')
# ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

# # Set x-axis ticks to show Day-Month format
# ax1.xaxis.set_major_locator(plt.MaxNLocator(12))  # Show fewer ticks
# ax1.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: factored_flows_period_sorted['Day-Month'].iloc[int(x) % len(factored_flows_period_sorted['Day-Month'])]))

# # Rotate x-axis labels
# plt.xticks(rotation=45)

# # Plot additional data on ax2 if needed
# # ax2.plot(...)
# # ax2.set_title('Additional Data')
# # ax2.set_ylabel('Another Metric')

# # Set x-axis label and adjust layout
# plt.xlabel('Day-Month')
# plt.tight_layout()
# plt.show()
