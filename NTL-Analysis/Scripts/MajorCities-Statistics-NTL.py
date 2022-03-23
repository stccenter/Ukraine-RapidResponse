from netCDF4 import Dataset
import numpy as np
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime, date, timedelta
import geopandas as gpd
import csv
import pandas as pd
import argparse

def ExtractNC4ByName(filename, dsname):
    nc_data = Dataset(filename)
    #    print(h4_data)
    ds = np.array(nc_data[dsname][:])
    nc_data.close()
    return ds

def GenerateUKRStats(period):
    csv_filename = 'UKR_NTL_'+period+'.csv'
    if period == 'period':
        rc1 = 'Period'
    else:
        rc1 = 'Date'
    cols = [rc1, 'Mean', 'Standard Deviation']
    with open(out_path+csv_filename, 'w',encoding="utf-8", newline='') as f: 
        countries_result_list = []
        write = csv.writer(f)
        write.writerow(cols)
        for file in sorted(listdir(in_path)):
            f_split = os.path.splitext(file)
            ext = f_split[-1].lower()
            filename = f_split[0]
            if ext == '.nc':
                print(f'Processing file {filename}')
                if period == 'period':
                    period_value = filename.split('_')[1]
                    netcdf4_path = join(in_path, file)
                    radiance = ExtractNC4ByName(netcdf4_path, 'monthly_mean_radiance')
                    radiance_mean = np.nanmean(radiance)
                    radiance_std = np.nanstd(radiance)
                    countries_result_list.append([period_value, radiance_mean, radiance_std])
                else:
                    f_split = filename.split('_')
                    f_year = f_split[3]
                    f_doy = f_split[4]
                    start_date = date(int(f_year), 1, 1) # 1st Jaunary
                    # converting to date 
                    actual_date = start_date + timedelta(days=int(f_doy) - 1) 
                    date_string = actual_date.strftime("%m-%d-%Y")
                    netcdf4_path = join(in_path, file)
                    # nlon = ExtractNC4ByName(netcdf4_path, 'nlon')
                    # nlat = ExtractNC4ByName(netcdf4_path, 'nlat')
                    radiance = ExtractNC4ByName(netcdf4_path, 'Radiance')
                    radiance_mean = np.nanmean(radiance)
                    radiance_std = np.nanstd(radiance)
                    countries_result_list.append([date_string, radiance_mean, radiance_std])

        write.writerows(countries_result_list)
        print('Finished..')
        return countries_result_list
   

def GenerateCityStats(region, period):
    print(region, period)
    if period == 'period':
        rc1 = 'Period'
    else:
        rc1 = 'Date'
    cols = [rc1, 'Mean','Standard Deviation']
    selected_city_gpd = cities_gpd[(cities_gpd['city'] == region)]
    csv_filename =  'UKR_'+region+'_NTL_'+period+'.csv'
    with open(out_path+csv_filename, 'w',encoding="utf-8", newline = '') as f: 
        cities_result_list = []
        cols = [rc1, 'Mean','Standard Deviation']
        write = csv.writer(f)
        write.writerow(cols)
        for file in sorted(listdir(in_path)):
            f_split = os.path.splitext(file)
            ext = f_split[-1].lower()
            filename = f_split[0]
            if ext == '.nc':
                print(f'Processing file {file}')
                if period == 'period':
                    f_split = filename.split('_')
                    period_value = f_split[1]
                    netcdf4_path = join(in_path, file)
                    nlon = ExtractNC4ByName(netcdf4_path, 'nlon')
                    nlat = ExtractNC4ByName(netcdf4_path, 'nlat')
                    radiance = ExtractNC4ByName(netcdf4_path, 'monthly_mean_radiance')
                    if region == 'Kyiv':
                        kiev_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == 'Kiev City']
                        region_boundary = kiev_row['geometry'].bounds
                        min_x = region_boundary['minx'].to_numpy()
                        min_y = region_boundary['miny'].to_numpy()
                        max_x = region_boundary['maxx'].to_numpy()
                        max_y = region_boundary['maxy'].to_numpy()
                        print(min_x, min_y, max_x, max_y)
                    elif region == 'Sevastopol':
                        seva_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == "Sevastopol'"]
                        region_boundary = seva_row['geometry'].bounds
                        min_x = region_boundary['minx'].to_numpy()
                        min_y = region_boundary['miny'].to_numpy()
                        max_x = region_boundary['maxx'].to_numpy()
                        max_y = region_boundary['maxy'].to_numpy()
                        print(min_x, min_y, max_x, max_y)
                    else: 
                        selected_city_gpd = cities_gpd[(cities_gpd['city'] == region)]
                        for index, row in admin2_gpd.iterrows():
                            if selected_city_gpd.within(row['geometry']).any():
                                region_boundary = row['geometry'].bounds
                                min_x = region_boundary[0]
                                min_y = region_boundary[1]
                                max_x = region_boundary[2]
                                max_y = region_boundary[3]
                                print(min_x, max_x, min_y, max_y)
                    lon_index = np.where((nlon >= min_x) & (nlon <= max_x))
                    lat_index = np.where((nlat >= min_y) & (nlat <= max_y))
                    radiance_lon_selected = list(radiance[lon_index])
                    radiance_lat_selected = list(radiance[lat_index])
                    total_list = radiance_lon_selected + radiance_lat_selected
                    total_list = [x for x in total_list if str(x) != 'nan']
                    region_mean = np.nanmean(total_list)
                    region_sd = np.nanstd(total_list)
                    cities_result_list.append([period_value, region_mean, region_sd])

                elif period == 'daily':
                    f_split = filename.split('_')
                    f_year = f_split[3]
                    f_doy = f_split[4]
                    start_date = date(int(f_year), 1, 1) # 1st Jaunary
                    # converting to date 
                    actual_date = start_date + timedelta(days=int(f_doy) - 1) 
                    date_string = actual_date.strftime("%m-%d-%Y")
                    netcdf4_path = join(in_path, file)
                    nlon = ExtractNC4ByName(netcdf4_path, 'nlon')
                    nlat = ExtractNC4ByName(netcdf4_path, 'nlat')
                    radiance = ExtractNC4ByName(netcdf4_path, 'Radiance')
                    if region == 'Kyiv':
                        kiev_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == 'Kiev City']
                        region_boundary = kiev_row['geometry'].bounds
                        min_x = region_boundary['minx'].to_numpy()
                        min_y = region_boundary['miny'].to_numpy()
                        max_x = region_boundary['maxx'].to_numpy()
                        max_y = region_boundary['maxy'].to_numpy()
                    elif region == 'Sevastopol':
                        seva_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == "Sevastopol'"]
                        region_boundary = seva_row['geometry'].bounds
                        min_x = region_boundary['minx'].to_numpy()
                        min_y = region_boundary['miny'].to_numpy()
                        max_x = region_boundary['maxx'].to_numpy()
                        max_y = region_boundary['maxy'].to_numpy()
                        print(min_x, min_y, max_x, max_y)
                    else: 
                        selected_city_gpd = cities_gpd[(cities_gpd['city'] == region)]
                        for index, row in admin2_gpd.iterrows():
                            if selected_city_gpd.within(row['geometry']).any():
                                region_boundary = row['geometry'].bounds
                                min_x = region_boundary[0]
                                min_y = region_boundary[1]
                                max_x = region_boundary[2]
                                max_y = region_boundary[3]
                    lon_index = np.where((nlon >= min_x) & (nlon <= max_x))
                    lat_index = np.where((nlat >= min_y) & (nlat <= max_y))
                    radiance_lon_selected = list(radiance[lon_index])
                    radiance_lat_selected = list(radiance[lat_index])
                    total_list = radiance_lon_selected + radiance_lat_selected
                    total_list = [x for x in total_list if str(x) != 'nan']
                    region_mean = np.nanmean(total_list)
                    region_sd = np.nanstd(total_list)
                    cities_result_list.append([date_string, region_mean, region_sd])

        write.writerows(cities_result_list)
        print('Finished...')
        return(cities_result_list)

if __name__ == "__main__":

    regions = ['Chernihiv','Cherkasy','Chernivtsi','Donetsk','Dnipro','Ivano-Frankivsk','Kherson',\
        'Kharkiv','Kyiv','Khmelnytskyi','Kropyvnytskyi','Kryvyi Rih','Luhansk','Lutsk','Lviv',\
        'Mariupol','Mykolaiv','Odesa','Poltava','Rivne','Sevastopol','Simferopol','Sumy','Ternopil','Uzhhorod','Vinnytsia',\
        'Yalta','Zaporizhzhia','Zhytomyr']
    
    parser = argparse.ArgumentParser(description='Provide arguments.')
    parser.add_argument("-y", "--year", type=int, help="Year of interest", required=True)
    args = parser.parse_args()
    year = args.year

    periods = ['period','daily']
    countries_list,  cities_list  = [], []
    shpfilepath = './Data/Input/Shapefiles/'
    cities_df = pd.read_csv(shpfilepath+'/ua.csv')
    cities_gpd = gpd.GeoDataFrame(cities_df, geometry=gpd.points_from_xy(cities_df.lng, cities_df.lat))
    admin1_gpd = gpd.GeoDataFrame.from_file(shpfilepath+'/UKR_adm1.shp')
    admin2_gpd =  gpd.GeoDataFrame.from_file(shpfilepath+'/UKR_adm2.shp')
    cities_gpd = cities_gpd.set_crs(4326)
    lon_west, lon_east, lat_north, lat_south, size = 0.0, 0.0, 0.0, 0.0, 0
    for region in regions:
        for period in periods:
            in_path = './Data/Input/NC-Files/MajorCities/'+year+'/'+region+'/'+period+'/'
            out_path = './Data/Output/Statistics/MajorCities/'+year+'/'+period+'/'+region+'/'
            if not os.path.exists(out_path):
                os.makedirs(out_path)

            if region == 'Ukraine':
                countries_list = GenerateUKRStats(period)
                
            else:
                cities_list = GenerateCityStats(region, period)
