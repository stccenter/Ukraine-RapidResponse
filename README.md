# Ukraine-RapidResponse

## Steps to download Daily NO2 Data:
    First follow setup terminal directions
--------------------------------------
1. Go to https://disc.gsfc.nasa.gov/datasets/OMNO2d_003/summary
2. Click the Subset/Get Data link located in the blue Data Acess box on the right-hand side of the screen
3. Under method options, click Refine Data Range and select the day you would like to download the data for
4. Press the green get data button
5. Click the 'Download Links List' in the popup window
6. Next, check your downloads folder and find the document. 
7. Right click on the document and get the pathname. This is different based on what kind of computer you use. For macs- hover over the copy name and click the option key. 
8. In your terminal type the following: 	**wget --load-cookies /.urs_cookies --save-cookies /.urs_cookies --auth-no-challenge=on --keep-session-cookies --content-disposition -i <url.txt>**
9. Delete the entire <url.txt> and replace it with the pathname you copied
10. Run in your terminal. 
11. Open finder(mac) or the equivalent file explorer, and move the file from the general folder -> input -> present
12. Next in the terminal type: **python Scripts/GeneratePresentDailyMean-1.py -s 2022-06-26 -e 2022-06-26**
13. Replace the date listed(2022-06-2022) with the day your are downloading data for
14. Run in your terminal
15. Next go to your output folder and find the final file, upload where nessesary
16. Done!


# How to download historical data
1. Open the jupyter notebook located in the files section of the repository
2. Change the date for the data you would like to download located in block 4
3. Go to the top and click kernel --> Restart and Run All
4. Once it has run, go to block 9 and click on the 3rd link (It should look like this:  https://acdisc.gesdisc.eosdis.nasa.gov/opendap/HDF-EOS5/Aura_OMI_Level3/OMNO2d.003/2014/OMI-Aura_L3-OMNO2d_2014m0703_v003-2019m1122t155950.he5.nc4?ColumnAmountNO2Trop,lat,lon)
5. Go to downloads folder and move file where needed
6. Done!
