# Ukraine-RapidResponse


## Daily Data Download

|Pollutant|Period| Satellite |Source | Latest |
|--------|-----|----|----- | ----------- |
| NO2 |2022 | OMI-NO2 | [Link](https://disc.gsfc.nasa.gov/datasets/OMNO2d_003/summary) | 2022-09-18|
| NO2 |History(2012-2021)| OMI-NO2 | [Link](https://disc.gsfc.nasa.gov/datasets/OMNO2d_003/summary) |2021-12-31|
| NO2 |2022 | Tropomi-NO2 | [Link](https://disc.gsfc.nasa.gov/datasets/S5P_L2__NO2____HiR_2/summary?keywords=S5P_L2__NO2) |2022-09-11|
| NO2 |Historical 2021(Version 1)| Tropomi-NO2| [Link](https://disc.gsfc.nasa.gov/datasets/S5P_L2__NO2____HiR_1/summary?keywords=S5P_L2__NO2____HiR)|2021-07-01|
| NO2 | Historical 2021(Version 2)| Tropomi-NO2| [Link](https://disc.gsfc.nasa.gov/datasets/S5P_L2__NO2____HiR_2/summary?keywords=S5P_L2__NO2____HiR)|2021-12-31|  
| SO2 |2022 | OMI-SO2 | [Link](https://disc.gsfc.nasa.gov/datasets/OMSO2G_003/summary?keywords=Sulphur%20Dioxide) |2022-09-19|
| SO2 | History(2012-2021) | OMI-SO2 | [Link](https://disc.gsfc.nasa.gov/datasets/OMSO2G_003/summary?keywords=Sulphur%20Dioxide) | xxx |  
| SO2 |2022| Tropomi-SO2 | [Link](https://disc.gsfc.nasa.gov/datasets/S5P_L2__SO2____HiR_2/summary?keywords=SO2%20sentinel) |2022-09-18|
| O3 |2022| OMI-O3|  [Link](https://disc.gsfc.nasa.gov/datasets/OMTO3G_003/summary?keywords=aura) |2022-09-19|
| O3 | History(2012-2021) | OMI-O3 | [Link](https://disc.gsfc.nasa.gov/datasets/OMTO3G_003/summary?keywords=aura) | xxx |  
| O3 |2022| Tropomi-O3 | [Link](https://disc.gsfc.nasa.gov/datasets/S5P_L2__O3_TOT_HiR_2/summary?keywords=S5P_L2__O3) |2022-09-18|

## Air pollutants processing status

<table>
  <tr>
    <td>Temporal</td>
    <td>Satellite</td>
  </tr>
  <tr>
    <td  rowspan="2">Daily</td>
  </tr>
</table>

## Data Sources table
|Pollutant|Source|Spatial Extent|Spatial Res|Temporal Res|Temporal Extent|Short Name | Level | Link|
|--------|-----|----|----|-----|-----|-----|-----|----------- |
|O3|Sentinel TROPOMI|-180.0,-90.0,180.0,90.0|5.5 km x 3.5 km|101.5 minutes|2020-07-13 to 2022-08-07|S5P_L2__O3_TOT_HiR|L2|https://www.google.com/url?q=https://disc.gsfc.nasa.gov/datasets/S5P_L2__O3_TOT_HiR_2/summary?keywords%3DS5P_L2__O3&sa=D&source=editors&ust=1660156936974980&usg=AOvVaw041YZ-sLdoQ5-vjzRf062U|
|O3|OMI|-180.0,-90.0,180.0,90.0|0.25° x 0.25°|1 day|2004-10-01 to  2022-08-09|OMTO3G|L2|https://www.google.com/url?q=https://disc.gsfc.nasa.gov/datasets/OMTO3G_003/summary?keywords%3Daura&sa=D&source=editors&ust=1660156936983179&usg=AOvVaw1YyRv1zWv_l9QetRViXhN0|
|S02|Sentinel TROPOMI|-180.0,-90.0,180.0,90.0|5.5 km x 3.5 km|101.5 minutes|2020-07-13 to 2022-08-07|S5P_L2__SO2____HiR|L2|https://www.google.com/url?q=https://disc.gsfc.nasa.gov/datasets/S5P_L2__SO2____HiR_2/summary?keywords%3DSO2%2520sentinal&sa=D&source=editors&ust=1660156936978300&usg=AOvVaw0bx_6r_pUIZwVr5YLR84KB|
|SO2|OMI|-180.0,-90.0,180.0,90.0|0.25° x 0.25°|1 day|2004-10-01 to  2022-08-09|OMSO2G|L2|https://www.google.com/url?q=https://disc.gsfc.nasa.gov/datasets/OMSO2G_003/summary?keywords%3DSulphur%2520Dioxide&sa=D&source=editors&ust=1660156936980670&usg=AOvVaw08rjswE4UVcV8g6i3pGM6h|

## Steps to download OMI Daily NO2 Data:
    First follow setup terminal directions
    
1a. create account on Earth :
    https://urs.earthdata.nasa.gov
    
1b. Follow steps for downloading data using wget:
    https://disc.gsfc.nasa.gov/data-access#mac_linux_wget

1c. Go to https://disc.gsfc.nasa.gov/datasets/OMNO2d_003/summary
![Screen Shot 2022-07-27 at 11 56 06 AM](https://user-images.githubusercontent.com/47231057/181294364-b693f174-2d5a-47b0-a98e-691182c765f5.png)


2. Click the Subset/Get Data link located in the blue Data Acess box on the right-hand side of the screen


4. Under method options, click Refine Data Range and select the day you would like to download the data for
![Screen Shot 2022-07-27 at 11 57 58 AM](https://user-images.githubusercontent.com/47231057/181294513-45e0b717-0126-4d4f-806b-e3cfb5933b70.png)


6. Press the green get data button
7. Click the 'Download Links List' in the popup window
![Screen Shot 2022-07-27 at 11 58 12 AM](https://user-images.githubusercontent.com/47231057/181294473-ec0f4e3a-9596-4f93-b601-0165d453eee7.png)



8. Next, check your downloads folder and find the document.
9. Right click on the document and get the pathname. This is different based on what kind of computer you use. For macs- hover over the copy name and click the option key. 
10. In your terminal type the following. Replace the <url.txt> and replace it with the pathname you copied.

```wget --load-cookies /.urs_cookies --save-cookies /.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i <url.txt>```

11. Run in your terminal. 
12. Open finder(mac) or the equivalent file explorer, and move the file from the general folder -> input -> present--(modify to change to wd)
13. Next in the terminal type: **python Scripts/GeneratePresentDailyMean-1.py -s 2022-06-26 -e 2022-06-26**
14. Replace the date listed(2022-06-2022) with the day your are downloading data for
15. Run in your terminal
16. Next go to your output folder and find the final file, upload where nessesary
17. Done!

--------------------------------------


## How to download OMI historical data
1. Open the jupyter notebook located in the files section of the repository
2. Change the date for the data you would like to download located in block 4
3. Go to the top and click kernel --> Restart and Run All
4. Once it has run, go to block 9 and click on the 3rd link (It should look like this:  https://acdisc.gesdisc.eosdis.nasa.gov/opendap/HDF-EOS5/Aura_OMI_Level3/OMNO2d.003/2014/OMI-Aura_L3-OMNO2d_2014m0703_v003-2019m1122t155950.he5.nc4?ColumnAmountNO2Trop,lat,lon)
5. Go to downloads folder and move file where needed
6. Done!
