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
from netCDF4 import Dataset
import pandas as pd
from sklearn.decomposition import PCA
from pandas import DataFrame
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap,addcyclic, shiftgrid,cm
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm
import matplotlib
from datetime import datetime, timedelta
import h5py
matplotlib.use('Agg')
from lunarcalendar import Converter, Solar, Lunar, DateNotExist
import calendar, json, argparse

def get_doy(this_date):
    Y = this_date.year
    M = this_date.month
    D = this_date.day
    """ given year, month, day return day of year
        Astronomical Algorithms, Jean Meeus, 2d ed, 1998, chap 7 """
    if is_leap_year(Y):
        K = 1
    else:
        K = 2
    N = int((275 * M) / 9.0) - K * int((M + 9) / 12.0) + D - 30
    return N



def GenerateMonthlyMean(date_start, date_end):
    doy_start = get_doy(date_start)
    doy_end = get_doy(date_end)
    year = date_start.year
    alldoy = np.linspace(doy_start, doy_end, doy_end - doy_start + 1)
    alldoy = ["%03d" % i for i in alldoy]
    all_radiance = []

    for doy in alldoy:
        imonth, iday, iyear = JulianDate_to_MMDDYYY(year, int(doy))
        the_file = input_dir + 'night_rad_' + region +'_'+ str(iyear)+'_'+doy + '.nc'

        all_nc_files, n_all = get_files(input_dir, the_file)
        if n_all ==0:
            continue

        theRadiance = extract_h4_by_name(the_file, 'Radiance')
        lats = extract_h4_by_name(the_file, 'nlat')
        lons = extract_h4_by_name(the_file, 'nlon')
        cloud_mask = extract_h4_by_name(the_file, 'Cloud mask')
        isif = theRadiance.shape

        all_radiance.append(theRadiance)

    all_radiance = np.array(all_radiance)
    all_radiance_mean = np.nanmean(all_radiance, axis=0)
    sif = all_radiance_mean.shape

    n_pixels = sif[0]
    all_radiance_mean = np.array(all_radiance_mean)

    outfile_nc = output_dir + region + str(year)+'_'+ period + '_mean_NTL.nc'
    # create nc file
    fid = netcdf.netcdf_file(outfile_nc, 'w')
    # create dimension variable, so we can use it in the netcdf
    fid.createDimension('n_pixels', n_pixels)

    nc_var = fid.createVariable('nlat', 'f4', ('n_pixels',))
    nc_var[:] = lats
    nc_var.long_name = 'latitude'
    nc_var.standard_name = 'latitude'
    nc_var.units = 'degrees_north'

    nc_var = fid.createVariable('nlon', 'f4', ('n_pixels',))
    nc_var[:] = lons
    nc_var.long_name = 'longitude'
    nc_var.standard_name = 'longitude'
    nc_var.units = 'degrees_east'

    nc_var = fid.createVariable('monthly_mean_radiance', 'f4', ('n_pixels',))
    nc_var[:] = all_radiance_mean
    nc_var.units = 'nW/(cm2 sr)'

    fid.close()

def congrid(a, newdims, method='linear', centre=False, minusone=False):
    '''Arbitrary resampling of source array to new dimension sizes.
    Currently only supports maintaining the same number of dimensions.
    To use 1-D arrays, first promote them to shape (x,1).
     
    Uses the same parameters and creates the same co-ordinate lookup points
    as IDL''s congrid routine, which apparently originally came from a VAX/VMS
    routine of the same name.
 
    method:
    neighbour - closest value from original data
    nearest and linear - uses n x 1-D interpolations using
                         scipy.interpolate.interp1d
    (see Numerical Recipes for validity of use of n 1-D interpolations)
    spline - uses ndimage.map_coordinates
 
    centre:
    True - interpolation points are at the centres of the bins
    False - points are at the front edge of the bin
 
    minusone:
    For example- inarray.shape = (i,j) & new dimensions = (x,y)
    False - inarray is resampled by factors of (i/x) * (j/y)
    True - inarray is resampled by(i-1)/(x-1) * (j-1)/(y-1)
    This prevents extrapolation one element beyond bounds of input array.
    '''
    if not a.dtype in [np.float64, np.float32]:
        a = np.cast[float](a)
 
    m1 = np.cast[int](minusone)
    ofs = np.cast[int](centre) * 0.5
    old = np.array( a.shape )
    ndims = len( a.shape )
    if len( newdims ) != ndims:
        print ("[congrid] dimensions error. " \
              "This routine currently only support " \
              "rebinning to the same number of dimensions.")
        return None
    newdims = np.asarray( newdims, dtype=int )
    dimlist = []

    if method == 'neighbour':
        for i in range( ndims ):
            base = np.indices(newdims)[i]
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        cd = np.array( dimlist ).round().astype(int)
        newa = a[list( cd )]
        return newa
 
    elif method in ['nearest','linear']:
        # calculate new dims
        for i in range( ndims ):
            base = np.arange( newdims[i] )
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        # specify old dims
        olddims = [np.arange(i, dtype = np.float) for i in list( a.shape )]
 
        # first interpolation - for ndims = any
        mint = scipy.interpolate.interp1d( olddims[-1], a, kind=method )
        newa = mint( dimlist[-1] )
 
        trorder = [ndims - 1] + range( ndims - 1 )
        for i in range( ndims - 2, -1, -1 ):
            newa = newa.transpose( trorder )
 
            mint = scipy.interpolate.interp1d( olddims[i], newa, kind=method )
            newa = mint( dimlist[i] )
 
        if ndims > 1:
            # need one more transpose to return to original dimensions
            newa = newa.transpose( trorder )
 
        return newa
    elif method in ['spline']:
        oslices = [ slice(0,j) for j in old ]
        oldcoords = np.ogrid[oslices]
        nslices = [ slice(0,j) for j in list(newdims) ]
        newcoords = np.mgrid[nslices]
 
        newcoords_dims = range(np.rank(newcoords))
        #make first index last
        newcoords_dims.append(newcoords_dims.pop(0))
        newcoords_tr = newcoords.transpose(newcoords_dims)
        # makes a view that affects newcoords
 
        newcoords_tr += ofs
 
        deltas = (np.asarray(old) - m1) / (newdims - m1)
        newcoords_tr *= deltas
 
        newcoords_tr -= ofs
 
        newa = scipy.ndimage.map_coordinates(a, newcoords)
        return newa
    else:
        print ("Congrid error: Unrecognized interpolation type.\n", \
              "Currently only \'neighbour\', \'nearest\',\'linear\',", \
              "and \'spline\' are supported.")
        return None

def get_files(dir,ext):
    allfiles=[]
    for file in glob.glob(dir+'*.nc'):
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

def is_leap_year(year):
    """ if year is a leap year return True
        else return False """
    if year % 100 == 0:
        return year % 400 == 0
    return year % 4 == 0

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

def JulianDate_to_MMDDYYY(y,jd):
    month = 1
    day = 0
    while jd - calendar.monthrange(y,month)[1] > 0 and month <= 12:
        jd = jd - calendar.monthrange(y,month)[1]
        month = month + 1
    return month,jd,y
# -----------------------------------------------------------------------------
# -||||||||||||||||||||||||Main function|||||||||||||||||||||||||||||||||||||||
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Provide arguments.')
    parser.add_argument("-r", "--region", type=str, help="Specify the region of interest.", required=True)
    parser.add_argument("-s", "--startdate", type=str, help="The Start Date - format YYYY-MM-DD", required=True)
    parser.add_argument("-e", "--enddate", type=str, help="Specify the start date.", required=True)
    parser.add_argument("-td", "--timedelta", type=int, help="Specify the days.", required=True)

    args = parser.parse_args()

    # Set up the start and end date of your study period
    region = args.region
    start_date = args.startdate
    end_date = args.enddate
    time_delta = args.timedelta

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    before_sd = start_date
    before_ed = start_date + timedelta(time_delta)
    after_sd = end_date - timedelta(time_delta)
    after_ed = end_date

    # Indicate your input raw data and output folder
    input_dir = './Data/Input/NC-Files/'+region+'/daily/'
    output_dir = './Data/Input/NC-Files/'+region+'/period/'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    lon_west, lon_east, lat_north, lat_south = 0.0, 0.0, 0.0, 0.0
    with open('./Data/Input/ukraine_json.json') as f:
        # returns JSON object as
        # a dictionary
        data = json.load(f)    
        # Iterating through the json
        # list
        for i in data['Ukraine']:
            if i['name'] == region:
                lon_west = i['lon_west']
                lon_east = i['lon_east']
                lat_north = i['lat_north']
                lat_south = i['lat_south']

    periods = ['before','after']

    for period in periods:

        if period == 'before':
            GenerateMonthlyMean(before_sd, before_ed)

        elif period == 'after':
            GenerateMonthlyMean(after_sd, after_ed)

