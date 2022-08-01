# Ukraine-RapidResponse

## Steps to download OMI Daily NO2 Data:
    First follow setup terminal directions
1. Go to https://disc.gsfc.nasa.gov/datasets/OMNO2d_003/summary
![Screen Shot 2022-07-27 at 11 56 06 AM](https://user-images.githubusercontent.com/47231057/181294364-b693f174-2d5a-47b0-a98e-691182c765f5.png)


2. Click the Subset/Get Data link located in the blue Data Acess box on the right-hand side of the screen


4. Under method options, click Refine Data Range and select the day you would like to download the data for
![Screen Shot 2022-07-27 at 11 57 58 AM](https://user-images.githubusercontent.com/47231057/181294513-45e0b717-0126-4d4f-806b-e3cfb5933b70.png)


6. Press the green get data button
7. Click the 'Download Links List' in the popup window
![Screen Shot 2022-07-27 at 11 58 12 AM](https://user-images.githubusercontent.com/47231057/181294473-ec0f4e3a-9596-4f93-b601-0165d453eee7.png)



8. Next, check your downloads folder and find the document.
9. Right click on the document and get the pathname. This is different based on what kind of computer you use. For macs- hover over the copy name and click the option key. 
10. In your terminal type the following: ***wget --load-cookies /.urs_cookies --save-cookies /.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i <url.txt>***
14. Delete the entire <url.txt> and replace it with the pathname you copied
15. Run in your terminal. 
16. Open finder(mac) or the equivalent file explorer, and move the file from the general folder -> input -> present
17. Next in the terminal type: **python Scripts/GeneratePresentDailyMean-1.py -s 2022-06-26 -e 2022-06-26**
18. Replace the date listed(2022-06-2022) with the day your are downloading data for
19. Run in your terminal
20. Next go to your output folder and find the final file, upload where nessesary
21. Done!

--------------------------------------


## How to download historical data
1. Open the jupyter notebook located in the files section of the repository
2. Change the date for the data you would like to download located in block 4
3. Go to the top and click kernel --> Restart and Run All
4. Once it has run, go to block 9 and click on the 3rd link (It should look like this:  https://acdisc.gesdisc.eosdis.nasa.gov/opendap/HDF-EOS5/Aura_OMI_Level3/OMNO2d.003/2014/OMI-Aura_L3-OMNO2d_2014m0703_v003-2019m1122t155950.he5.nc4?ColumnAmountNO2Trop,lat,lon)
5. Go to downloads folder and move file where needed
6. Done!


## Table

|Period| Satellite | Latest |
| ------|----- | ----------- |
| 2022 | OMI-NO2 | xxx|
| 2022 | Tropomi-NO2 | xxx|
|History(2012-2022)|OMI-NO2|xxx|  
