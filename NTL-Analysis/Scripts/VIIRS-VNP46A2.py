import glob, os,sys
# import netCDF4
import math
import scipy.interpolate
import scipy.ndimage
import numpy as np
import matplotlib as mpl
import scipy.stats as stats
import matplotlib.mlab as mlab
import h5py
from scipy.io import netcdf
from scipy.stats import lognorm
from scipy.stats import gamma
from scipy.stats import chisquare
#from compiler.ast import flatten
from sklearn import datasets, linear_model
from sklearn.linear_model import LinearRegression
from scipy.stats import norm
import netCDF4
from netCDF4 import Dataset
import pandas as pd
from sklearn.decomposition import PCA
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap,addcyclic, shiftgrid,cm
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm
import matplotlib
import datetime
from pyhdf.SD import SD, SDC
from pyhdf.HDF import *
from pyhdf.VS import *
matplotlib.use('Agg')
import calendar
from lunardate import LunarDate
from lunarcalendar import Converter, Solar, Lunar, DateNotExist
import json
import argparse
from datetime import datetime

def JulianDate_to_MMDDYYY(y,jd):
    month = 1
    day = 0
    while jd - calendar.monthrange(y,month)[1] > 0 and month <= 12:
        jd = jd - calendar.monthrange(y,month)[1]
        month = month + 1
    return month,jd,y

def get_files(dir,ext):
    allfiles=[]
    for file in glob.glob(os.path.join(dir, ext)):
        allfiles.append(file)
    return allfiles, len(allfiles)

# read netcdf 3 file by dataset name
def extract_nc3_by_name(filename, dsname):
    nc_data = netcdf.netcdf_file(filename, "r")
    ds = np.array(nc_data.variables[dsname][:])
    nc_data.close()
    return ds

def extract_h5_by_name(filename,dsname):
    h5_data = h5py.File(filename)
    ds = np.array(h5_data[dsname][:])
    h5_data.close()
    return ds

def extract_h4_by_name(filename,dsname):
    h4_data = Dataset(filename)
    ds = np.array(h4_data[dsname][:])
    h4_data.close()
    return ds

def read_vpn46a1_boundary(file):
    with h5py.File(file, mode='r') as f:
        group = f['/']
        min_lon = group.attrs['WestBoundingCoord']
        max_lon = group.attrs['EastBoundingCoord']
        min_lat = group.attrs['SouthBoundingCoord']
        max_lat = group.attrs['NorthBoundingCoord']
        return np.array([min_lon,max_lon,min_lat,max_lat])
    
def is_leap_year(year):
    """ if year is a leap year return True
        else return False """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

def doy(Y,M,D):
    """ given year, month, day return day of year
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N

def ymd(Y,N):
    """ given year = Y and day of year = N, return year, month, day
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    M = int((9 * (K + N)) / 275.0 + 0.98)
    if N < 32:
        M = 1
    D = N - int((275 * M) / 9.0) + K * int((M + 9) / 12.0) + 30
    return Y, M, D
# -----------------------------------------------------------------------------
# -||||||||||||||||||||||||Main function|||||||||||||||||||||||||||||||||||||||
# -----------------------------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Provide arguments.')
    parser.add_argument("-r", "--region", type=str, help="Specify the region of interest.", required=True)
    parser.add_argument("-s", "--startdate", type=str, help="The Start Date - format YYYY-MM-DD", required=True)
    parser.add_argument("-e", "--enddate", type=str, help="Specify the start date.", required=True)
    args = parser.parse_args()

    # Set up the start and end date of your study period
    start_date = args.startdate
    end_date = args.enddate
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    year = start_date.year
    day_start = start_date.day
    month_start = start_date.month
    day_end = end_date.day
    month_end = end_date.month
    
    print(os.getcwd())
    
    # Set up you study region, you need to find the latitude and longitude of the four corners of your study region
    region = args.region
    # Indicate your input raw data and output folder
    Data_infolder = './Data/Input/VIIRS-VNP46A2/2022/'
    output_dir = './Data/Input/NC-Files/'+region+'/daily/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    lon_west, lon_east, lat_north, lat_south = 0.0, 0.0, 0.0, 0.0
    with open('./Data/Input/ukraine_json.json') as f:
        # returns JSON object as
        # a dictionary
        data = json.load(f)    
        for i in data['Ukraine']:
            if i['name'] == region:
                lon_west = i['lon_west']
                lon_east = i['lon_east']
                lat_north = i['lat_north']
                lat_south = i['lat_south']


    doy_start = doy(year, month_start, day_start)
    doy_end = doy(year, month_end, day_end)
    alldoy = np.linspace(doy_start, doy_end, doy_end - doy_start + 1)
    alldoy = ["%03d" % i for i in alldoy]
    ratio = (lon_east - lon_west) / (lat_north - lat_south)

    for doy in alldoy:
        imonth, iday, iyear = JulianDate_to_MMDDYYY(year,int(doy))
        all_nc_files, n_all = get_files(Data_infolder, 'VNP46A2.A' + str(year)+str(doy)+'*.h5')
        all_nc_files = np.sort (all_nc_files)
        j = 0
        for i in range(n_all):
            the_file = all_nc_files[i]
            the_filename = os.path.basename(the_file)
            print(f'Reading {the_filename}..')
            theRadiance = 0.1*extract_h5_by_name(the_file, '/HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/Gap_Filled_DNB_BRDF-Corrected_NTL')
            isif = theRadiance.shape
            n_lon = isif[0]
            n_lat = isif[1]
            coors = read_vpn46a1_boundary(the_file)
            max_lon = coors[1]
            min_lon = coors[0]
            max_lat = coors[3]
            min_lat = coors[2]

            x = np.linspace(min_lon, max_lon,n_lon)
            y = np.linspace(max_lat,min_lat,n_lat)
            lon_grid,lat_grid = np.meshgrid(x,y)
            theRadiance = theRadiance.reshape(-1)
            idx_nan=np.where(theRadiance<0)
            theRadiance[idx_nan]=np.nan
            idx_nan2=np.where(theRadiance>1000)
            theRadiance[idx_nan2] = np.nan
            lats = lat_grid.reshape(-1)
            lons = lon_grid.reshape(-1)
            #zenith = 0.01*extract_h5_by_name(the_file, 'HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/Solar_Zenith')
            #zenith = zenith.reshape(-1)
            cloud_mask = extract_h5_by_name(the_file, 'HDFEOS/GRIDS/VNP_Grid_DNB/Data Fields/QF_Cloud_Mask')
            cloud_mask = cloud_mask.reshape(-1)
            cloud_mask = cloud_mask & 0b00011000000
            sea_mask = cloud_mask & 0b00000001110
            region_lon = np.logical_and(lons > lon_west, lons < lon_east)
            region_lat = np.logical_and(lats > lat_south, lats < lat_north)
            region_loc = np.logical_and(region_lon, region_lat)
            idx_cloud = np.where(cloud_mask>64)
            idx_sea = np.where(sea_mask==6)
            theRadiance[idx_sea] = np.nan

            #theRadiance[idx_cloud]=np.nan
            theRadiance = np.array(theRadiance)
            #idx_clear = np.logical_and(cloud_mask<=64, region_loc)
            #idx_region, = np.where(idx_clear)
            idx_region, = np.where(region_loc)
            if len(idx_region)==0:
                continue
            theRadiance = theRadiance[idx_region]
            lats = lats[idx_region]
            lons = lons[idx_region]
            cloud_mask = cloud_mask[idx_region]

            theRadiance = np.array(theRadiance)
            lats = np.array(lats)
            lons = np.array(lons)
            cloud_mask = np.array(cloud_mask)
            isif = theRadiance.shape
            if j == 0:
                global_radiance = theRadiance
                global_lat = lats
                global_lon = lons
                global_cloud = cloud_mask
                j = 1
            else:
                global_radiance = np.concatenate((global_radiance, theRadiance), axis=0)
                global_lat = np.concatenate((global_lat, lats), axis=0)
                global_lon = np.concatenate((global_lon, lons), axis=0)
                global_cloud = np.concatenate((global_cloud, cloud_mask), axis=0)
        global_radiance = np.array(global_radiance)
        global_lat = np.array(global_lat)
        global_lon = np.array(global_lon)
        global_cloud = np.array(global_cloud)
        sif = global_radiance.shape

        # print (sif)
        if sif[0] == 0:
            continue
        #save figure
        y_min=global_lat.min()
        y_max=global_lat.max()
        x_min=global_lon.min()
        x_max=global_lon.max()
        mindata=global_radiance[~np.isnan(global_radiance)].min()
        maxdata=global_radiance[~np.isnan(global_radiance)].max()
        # save as nc file
        outfile_nc = output_dir + 'night_rad_' + region +'_' + str(iyear)+'_'+doy + '.nc'
        fid = netcdf.netcdf_file(outfile_nc, 'w')
        # create dimension variable, so we can use it in the netcdf
        fid.createDimension('npixels', sif[0])

        # latitude
        nc_var = fid.createVariable('nlat', 'f4', ('npixels',))
        nc_var[:] = global_lat
        nc_var.long_name = 'latitude'
        nc_var.standard_name = 'latitude'
        nc_var.units = 'degrees_north'
        # longitude
        nc_var = fid.createVariable('nlon', 'f4', ('npixels',))
        nc_var[:] = global_lon
        nc_var.long_name = 'longitude'
        nc_var.standard_name = 'longitude'
        nc_var.units = 'degrees_east'

        # radiance
        nc_var = fid.createVariable('Radiance', 'f4', ('npixels',))
        nc_var[:] = global_radiance
        nc_var.units = 'nW/(cm2 sr)'

        nc_var = fid.createVariable('Cloud mask', 'f4', ('npixels',))
        nc_var[:] = global_cloud
        nc_var.units = ''
        # end output
        fid.close()
        print ('finish '+str(iyear)+str(doy))






