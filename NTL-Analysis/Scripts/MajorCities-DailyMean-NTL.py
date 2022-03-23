import glob, os
import numpy as np
import h5py
from scipy.io import netcdf
from netCDF4 import Dataset
import matplotlib
matplotlib.use('Agg')
import calendar
from datetime import datetime, timedelta
import geopandas as gpd

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


def extract_h4_by_name(filename,dsname):
    h4_data = Dataset(filename)
    ds = np.array(h4_data[dsname][:])
    h4_data.close()
    return ds

def extract_h5_by_name(filename,dsname):
    h5_data = h5py.File(filename)
    ds = np.array(h5_data[dsname][:])
    h5_data.close()
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

def get_doy(Y,M,D):
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

def GenerateMonthlyMean(period_start, period_end):

    year = period_start.year
    day_start = period_start.day
    month_start = period_start.month
    day_end = period_end.day
    month_end = period_end.month
   
    doy_start = get_doy(year, month_start, day_start)
    doy_end = get_doy(year, month_end, day_end)

    alldoy = np.linspace(doy_start, doy_end, doy_end - doy_start + 1)
    alldoy = ["%03d" % i for i in alldoy]
    all_radiance = []

    for doy in alldoy:
        print(f'day of the year  {doy} {period}')
        imonth, iday, iyear = JulianDate_to_MMDDYYY(year, int(doy))
        the_file = output_daily_dir + 'night_rad_' + city +'_'+ str(iyear)+'_'+doy + '.nc'

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

    outfile_nc = output_period_dir + city + str(year)+'_'+ period + '_mean_NTL.nc'

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
    return outfile_nc

def GenerateDifference(pre_file, post_file):

    pre_rad =np.array(extract_h4_by_name(pre_file, 'monthly_mean_radiance'))
    idx_bg1 = np.where(pre_rad<5)
    pre_rad[idx_bg1] = 0

    post_rad =np.array(extract_h4_by_name(post_file, 'monthly_mean_radiance'))
    idx_bg2 = np.where(post_rad<5)
    post_rad[idx_bg2] = 0

    #exit()
    lats =np.array(extract_h4_by_name(pre_file, 'nlat'))
    lons = np.array(extract_h4_by_name(pre_file, 'nlon'))
    
    rad_diff = post_rad - pre_rad
    sif = rad_diff.shape
    n_pixels = sif[0]

    outfile_nc_diff = output_period_diff + '/'+'difference_'+city + '_after_before'+'.nc4'
    # create nc file
    fid1 = netcdf.netcdf_file(outfile_nc_diff, 'w')
    # create dimension variable, so we can use it in the netcdf
    fid1.createDimension('n_pixels', n_pixels)

    nc_diff_var = fid1.createVariable('nlat', 'f4', ('n_pixels',))
    nc_diff_var[:] = lats
    nc_diff_var.lat_name = 'latitude'
    nc_diff_var.standard_name = 'latitude'
    nc_diff_var.units = 'degrees_north'

    nc_diff_var = fid1.createVariable('nlon', 'f4', ('n_pixels',))
    nc_diff_var[:] = lons
    nc_diff_var.long_name = 'longitude'
    nc_diff_var.standard_name = 'longitude'
    nc_diff_var.units = 'degrees_east'

    nc_diff_var = fid1.createVariable('radiance difference', 'f4', ('n_pixels',))
    nc_diff_var[:] = rad_diff
    nc_diff_var.units = 'nW/(cm2 sr)'
    fid1.close()

if __name__ == '__main__':

    # Indicate your input raw data and output folder
    Data_infolder = './Data/Input/VIIRS-VNP46A2/2022/'
    shpfilepath = './Data/Input/Shapefiles/'
    major_cities = ['Chernihiv','Cherkasy','Chernivtsi','Donetsk','Dnipro','Ivano-Frankivsk','Kherson',\
        'Kharkiv','Kyiv','Khmelnytskyi','Kropyvnytskyi','Kryvyi Rih','Luhansk','Lutsk','Lviv',\
        'Mariupol','Mykolaiv','Odesa','Poltava','Rivne','Sevastopol','Simferopol','Sumy','Ternopil','Uzhhorod','Vinnytsia',\
        'Yalta','Zaporizhzhia','Zhytomyr']


    cities_gpd = gpd.GeoDataFrame.from_file(shpfilepath+'/UKR_MajorCities.shp')
    admin1_gpd = gpd.GeoDataFrame.from_file(shpfilepath+'/UKR_adm1.shp')
    admin2_gpd =  gpd.GeoDataFrame.from_file(shpfilepath+'/UKR_adm2.shp')

    start_date = datetime.strptime('2022-02-14', '%Y-%m-%d')
    end_date = datetime.strptime('2022-03-05', '%Y-%m-%d')

    year = start_date.year
    day_start = start_date.day
    month_start = start_date.month
    day_end = end_date.day
    month_end = end_date.month

    time_delta = 10

    before_sd = start_date
    before_ed = start_date + timedelta(time_delta) - timedelta(1)
    after_sd = end_date - timedelta(time_delta) + timedelta(1)
    after_ed = end_date

    print(before_sd, before_ed, after_sd, after_ed)
    
    pt_change_list, city_admin = [], []
    lon_west, lon_east, lat_north, lat_south = 0.0, 0.0, 0.0, 0.0
    for city in major_cities:
        output_daily_dir = './Data/Input/NC-Files/MajorCities/2022/'+city+'/daily/'
        output_period_dir = './Data/Input/NC-Files/MajorCities/2022/'+city+'/period/'
        output_period_diff = './Data/Input/NC-Files/MajorCities/2022/'+city+'/difference/'
        

        if not os.path.exists(output_daily_dir):
            print('inside if')
            os.makedirs(output_daily_dir)
    
        if not os.path.exists(output_period_dir):
            os.makedirs(output_period_dir)

        if not os.path.exists(output_period_diff):
            os.makedirs(output_period_diff)

        if city == 'Chernivtsi':
            selected_city_gpd = cities_gpd[(cities_gpd['city'] == city) & (cities_gpd['admin_name'] == 'Chernivets?ka Oblast?')]
        elif city == 'Mykolaiv':
            selected_city_gpd = cities_gpd[(cities_gpd['city'] == city) & (cities_gpd['admin_name'] == 'Mykolayivs?ka Oblast?')]
        elif city == 'Yalta':
            selected_city_gpd = cities_gpd[(cities_gpd['city'] == city) & (cities_gpd['admin_name'] == 'Krym, Avtonomna Respublika')]
        elif city == 'Rivne':
            selected_city_gpd = cities_gpd[(cities_gpd['city'] == city) & (cities_gpd['admin_name'] == 'Rivnens?ka Oblast?')]
        else:
            selected_city_gpd = cities_gpd[(cities_gpd['city'] == city) ]
        
        
        if city == 'Kyiv':
            kiev_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == 'Kiev City']
            admin_boundary = kiev_row['NAME_1']
            admin_boundary = (admin_boundary).astype('str')
            region_boundary = kiev_row['geometry'].bounds
            lon_west = region_boundary['minx'].to_numpy()
            lat_south = region_boundary['miny'].to_numpy()
            lon_east = region_boundary['maxx'].to_numpy()
            lat_north = region_boundary['maxy'].to_numpy()
            ratio = (lon_east - lon_west) / (lat_north - lat_south)
            print(lon_west, lon_east, lat_north, lat_south)

        elif city == 'Sevastopol':
            seva_row = admin1_gpd.loc[admin1_gpd['NAME_1'] == "Sevastopol'"]
            admin_boundary = seva_row['NAME_1']
            admin_boundary = (admin_boundary).values[0]
            region_boundary = seva_row['geometry'].bounds
            lon_west = region_boundary['minx'].to_numpy()
            lat_south = region_boundary['miny'].to_numpy()
            lon_east = region_boundary['maxx'].to_numpy()
            lat_north = region_boundary['maxy'].to_numpy()
            ratio = (lon_east - lon_west) / (lat_north - lat_south)
            print(lon_west, lon_east, lat_north, lat_south)

        else:
            for index, row in admin2_gpd.iterrows():
                if selected_city_gpd.within(row['geometry']).any():
                    admin_boundary = row['NAME_2']
                    admin2_boundary = row['geometry'].bounds
                    lon_west = admin2_boundary[0]
                    lat_south = admin2_boundary[1]
                    lon_east = admin2_boundary[2]
                    lat_north = admin2_boundary[3]
                    print(lon_west, lon_east, lat_south, lat_north)
                    ratio = (lon_east - lon_west) / (lat_north - lat_south)

        doy_start = get_doy(year, month_start, day_start)
        doy_end = get_doy(year, month_end, day_end)

        #daily-mean
        alldoy = np.linspace(doy_start, doy_end, doy_end - doy_start + 1)
        alldoy = ["%03d" % i for i in alldoy]

        #daily-mean
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
                theRadiance = np.array(theRadiance)

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
            outfile_nc = output_daily_dir + 'night_rad_' + city +'_' + str(iyear)+'_'+doy + '.nc'
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
            print (f'Finished generating daily netcdf4 of {city} on {str(iyear)}-{str(imonth)}-{str(iday)} day of the year is {doy}')

        #periodic-mean
        periods = ['before','after','difference', 'percent-change']
        
        for period in periods:

            if period == 'before':
                pre_file = GenerateMonthlyMean(before_sd, before_ed)

            elif period == 'after':
                post_file = GenerateMonthlyMean(after_sd, after_ed)

            elif period == 'difference':
                GenerateDifference(pre_file, post_file)
        
            #percent change
            elif period == 'percent-change':

                lats =np.array(extract_h4_by_name(pre_file, 'nlat'))
                lons = np.array(extract_h4_by_name(pre_file, 'nlon'))

                pre_rad = np.array(extract_h4_by_name(pre_file, 'monthly_mean_radiance'))
                post_rad = np.array(extract_h4_by_name(post_file, 'monthly_mean_radiance'))
                
                lon_index = np.where((lons >= lon_west) & (lons <= lon_east))
                lat_index = np.where((lats >= lat_south) & (lats <= lat_north))

                radiance_lon_selected = list(pre_rad[lon_index])
                radiance_lat_selected = list(pre_rad[lat_index])
                total_pre_list = radiance_lon_selected + radiance_lat_selected

                radiance_lon_selected = list(post_rad[lon_index])
                radiance_lat_selected = list(post_rad[lat_index])
                total_post_list = radiance_lon_selected + radiance_lat_selected

                total_pre_list = [x for x in total_pre_list if str(x) != 'nan']
                region_pre_mean = np.nanmean(total_pre_list)

                total_post_list = [x for x in total_post_list if str(x) != 'nan']
                region_post_mean = np.nanmean(total_post_list)

                print(region_pre_mean, region_post_mean)

                # lon_rad_selected = lons[lon_index]
                # lat_rad_selected = lats[lat_index]

                rad_diff = region_post_mean - region_pre_mean
                print(rad_diff)
                rad_pc = (rad_diff/ region_pre_mean)*100
                print(rad_pc)
                rad_pc_mean = np.nanmean(rad_pc)

                print(f'Finished calculating percent change of {city} - {rad_pc_mean}')
                city_admin.append([city, admin_boundary])
                print(f'{city} lies inside {admin_boundary}')

                pt_change_list.append([city,rad_pc_mean])


    for i in pt_change_list:
        print(i[0])
        for index, row in cities_gpd.iterrows():
            if row['city'] == i[0]:
                cities_gpd.loc[index, 'ptchange'] = i[1]
    print(cities_gpd)
    cities_pc_gpd = cities_gpd
    cities_pc_gpd.to_file(shpfilepath+"MajorCities_PtChange.shp")



        
