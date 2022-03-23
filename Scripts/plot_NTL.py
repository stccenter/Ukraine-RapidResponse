import glob, os,sys
# import netCDF4
import math
import scipy.interpolate
import scipy.ndimage
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import scipy.stats as stats
import matplotlib.mlab as mlab
#import h5py
from scipy.io import netcdf
from scipy.stats import lognorm
from scipy.stats import gamma
from scipy.stats import chisquare
#from compiler.ast import flatten
from sklearn import datasets, linear_model
from sklearn.linear_model import LinearRegression
from scipy.stats import norm
from netCDF4 import Dataset
from scipy.interpolate import griddata
from mpl_toolkits.basemap import Basemap,addcyclic, shiftgrid,cm
import datetime as dt
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
import pandas as pd
import os
import calendar,json, argparse

def JulianDate_to_MMDDYYY(y,jd):
    month = 1
    day = 0
    while jd - calendar.monthrange(y,month)[1] > 0 and month <= 12:
        jd = jd - calendar.monthrange(y,month)[1]
        month = month + 1
    return month,jd,y
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
def get_files(dir,ext):
    allfiles=[]
    for file in glob.glob(os.path.join(dir, ext)):
        allfiles.append(file)
    return allfiles, len(allfiles)
# -----------------------------------------------------------------------------
# -||||||||||||||||||||||||Main function|||||||||||||||||||||||||||||||||||||||
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide arguments.')
    parser.add_argument("-r", "--region", type=str, help="Specify the region of interest.", required=True)
    args = parser.parse_args()
    region = args.region
    admin_key = {
        'Kyiv': 'Kiev City',
        'Kharkiv':"Kharkivs'ka",
        'Donetsk':"Donets'ka",
        'Ivano-Frankivsk':"L'viv",
        'Kherson': 'Kherson',
        'Luhansk': "Luhans'ka",
        'Lutsk': 'Volyn',
        'Lviv': "L'viv",
        'Mariupol': "Mariupol's'ka",
        'Ukraine': 'Ukraine'
    }
    name_1 = admin_key[region]

    lon_west, lon_east, lat_north, lat_south, size = 0.0, 0.0, 0.0, 0.0, 0
    with open('./Data/Input/ukraine_json.json') as f:
        data = json.load(f)    
        # Iterating through the json
        # list
        for i in data['Ukraine']:
            if i['name'] == region:
                lon_west = i['lon_west']
                lon_east = i['lon_east']
                lat_north = i['lat_north']
                lat_south = i['lat_south']
                size = i['size']


    tags = ['period', 'daily','Difference']
    for tag in tags:
        if tag == 'Difference':
            inputDir = './Data/Input/NC-Files/'+tag+'/'
        else:
            inputDir='./Data/Input/NC-Files/'+region+'/'+tag+'/'

        outdir = './Data/Output/plot/'+tag+'/'+region+'/'
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        if tag == 'daily':
            all_nc_files, n_files = get_files(inputDir, 'night_rad_'+region+'*.nc')
        if tag == 'period':
            all_nc_files, n_files = get_files(inputDir, region+'*.nc')
        if tag == 'Difference':
            all_nc_files, n_files = get_files(inputDir, '*.nc')

        all_nc_files = np.sort(all_nc_files)

        for i in range(n_files):
            the_filename = all_nc_files[i]
            filename = os.path.basename(the_filename)

            if tag == 'daily':
                filename_bname = os.path.basename(the_filename).split('.')[0]
                filename_split = filename_bname.split('_')
                doy = int(filename_split[-1])
                year = int(filename_split[-2])
                imonth, iday, iyear = JulianDate_to_MMDDYYY(year, int(doy))
                imonth = '%02d' % imonth
                iday = '%02d' % iday
                #year = the_filename.split('night_rad_'+region+'_')[1][:4]
                all_radiance_mean = extract_h4_by_name(the_filename, 'Radiance')
                outfile = outdir + region + '_' + str(imonth) + str(iday) + str(iyear)

            if tag == 'period':
                #period = the_filename.split(region+year+'_')[1][:5]
                all_radiance_mean = extract_h4_by_name(the_filename, 'monthly_mean_radiance')
                outfile = outdir + filename.split('.nc')[0][:]
                period_tag = the_filename.split('_')[1][:]

            if tag == 'Difference':
                print(the_filename)
                all_radiance_mean = extract_h4_by_name(the_filename, 'radiance difference')
                outfile = outdir + filename.split('.nc')[0][:] + '_' + region
                print(outfile)
                period_tag = the_filename.split('_')[1][:]

            all_radiance_mean = all_radiance_mean.squeeze()
            lats=extract_h4_by_name(the_filename,'nlat')
            lons=extract_h4_by_name(the_filename,'nlon')

            x_min = lon_west
            x_max = lon_east
            y_min = lat_south
            y_max = lat_north

            ratio = (x_max - x_min) / (y_max - y_min)
            idx_nan = np.where(all_radiance_mean == np.nan)
            # all_radiance_mean[idx_nan] = 0
            all_radiance_mean = np.array(all_radiance_mean)
            mindata = all_radiance_mean[~np.isnan(all_radiance_mean)].min()
            maxdata = all_radiance_mean[~np.isnan(all_radiance_mean)].max()

            if tag == 'Difference':
                mindata = -15
                maxdata = 15
                cmap = mpl.cm.seismic
            else:
                mindata = 0
                maxdata = 100
                cmap = mpl.cm.jet

            fig = plt.figure(figsize=(16, 12))  # Create a new figure window
            rect = [0.125, 0.25, 0.5, 0.5 / ratio]  # [left, bottom, width, height] (ratio 0~1)0.256
            ax = plt.axes(rect)

            if tag == 'daily':
                plt.title(region+' ' + str(imonth) +'-'+ str(iday) +'-'+ str(iyear))
            if tag == 'period':
                plt.title(region + ' ' + period_tag + ' the war')
            if tag == 'Difference':
                plt.title(region + ' difference between after and before the war')

            # create a basemap
            map = Basemap(projection='cyl', llcrnrlat=y_min, urcrnrlat=y_max, \
                        llcrnrlon=x_min, urcrnrlon=x_max, ax=ax)  # lon_0=0.0,

            # convert lat and lon to map projection coordinates
            lons, lats = map(lons, lats)

            # create render
            ticker_width = maxdata - mindata
            nticks = 10
            ticker_interval = ticker_width / nticks
            nticks += 1
            normticks = np.arange(mindata, maxdata, ticker_interval)
            norm = mpl.colors.Normalize(vmin=mindata, vmax=maxdata, clip=True)
            cs = map.scatter(lons, lats, s=size, marker='s', c=all_radiance_mean, cmap=cmap, norm=norm, edgecolors='none')
            # create color bar
            cbaxes = fig.add_axes([rect[0], rect[1] - 0.05, rect[2], 0.02])
            # divider = make_axes_locatable(ax)
            # cbaxes = divider.append_axes("bottom", size="5%", pad=0.05)
            cbar = fig.colorbar(cs, cmap=cmap, ax=ax, cax=cbaxes, orientation='horizontal',
                                ticks=normticks, fraction=0.046, pad=0.05, extend='both', extendfrac='auto')  #
            # cbar.set_label('Some Units')
            tick_locator = mpl.ticker.MaxNLocator(nbins=nticks)
            cbar.locator = tick_locator
            cbar.ax.xaxis.set_ticks_position('bottom')

            # draw grid
            x_ivl = (x_max - x_min) / 5
            y_ivl = (y_max - y_min) / 5
            map.drawparallels(np.arange(y_min, y_max, y_ivl), linewidth=0.0, color='k', labels=[True, False, False, False])
            map.drawmeridians(np.arange(x_min, x_max, x_ivl), linewidth=0.0, color='k', labels=[False, False, False, True])

            if region == 'Ukraine':
                map.readshapefile('./Data/Input/Shapefiles/UKR_adm0', 'comarques')
                for info, shape in zip(map.comarques_info, map.comarques):
                    if info['NAME_FAO'] == name_1:
                        x, y = zip(*shape) 
                        map.plot(x, y, marker=None,color='r', linewidth = 1)    

            elif region == 'Kyiv':
                map.readshapefile('./Data/Input/Shapefiles/UKR_Selected_State_Boundary', 'comarques')
                for info, shape in zip(map.comarques_info, map.comarques):
                    if info['NAME_1'] == name_1:
                        x, y = zip(*shape) 
                        map.plot(x, y, marker=None,color='r', linewidth = 1)

            else: 
                map.readshapefile('./Data/Input/Shapefiles/UKR_adm2', 'comarques')
                for info, shape in zip(map.comarques_info, map.comarques):
                    if info['NAME_2'] == name_1:
                        x, y = zip(*shape) 
                        map.plot(x, y, marker=None,color='r', linewidth = 1)

            # set x title and y title
            ax.set_xlabel("", fontsize=2)
            ax.set_ylabel("", fontsize=2)
            plt.savefig(outfile, bbox_inches='tight', dpi=300)
            print(f'Finished saving {outfile}')
