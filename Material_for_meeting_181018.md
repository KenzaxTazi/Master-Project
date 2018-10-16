 
# Material for meeting 18/10/18

Tom and I first found that the conda files for satpy are old. We needed to dowload those from the github folder. Tom has fixed the files to run on Windows and Kenza will be using her Mac. 
 
We succesfully dowloaded the data, access the arrays and produce images. The S7, S8, and S9 files channels were not accessible. The error was spotted previously by another Github user. We went into files of the library to fix this too, but it did not work. 

File format e.g.: 
S3A_SL_1_RBT____20180822T000619_20180822T000919_20180822T015223_0179_035_016_3240_SVL_O_NR_003.SEN3

Mission ID | Processing level | Datatype | Start time | End time | Creation time | Duration | Cycle | Relative orbit| Frame | Center | Mode | Timeliness | Collection 
---------- | ---------------- | -------- | ---------- | ---------| ------------- | -------- | ----- | --------------| ----- | ------ | ---- | ---------- | ------------
S3A | 1S | RBT |20180822T000619 | 20180822T000919| 20180822T015223 | 0179 | 035 | 016 | 3240 | SVL | O | NR | 003
Sentinel 3A | Level 1 | 22nd August 2018 @ 00:06:19 UTC | 22nd August 2018 @ 00:09:19 UTC| 22nd August 2018 @ 01:52:23 UTC | 179s | 35 multiples of 385 orbits (385 orbits are completed before the ground tracks are repeated) | 35th orbits in cycle | 16 | Svalbard processing center |  

Tom also found KLM files to plot out the satelite's ground tracks on Fusion Tables or Google Earth.This will help us easily identify which files we want to look out without having to dowload them. 
https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-3/satellite-description/orbit

 
Below we have generated images from a single channel, a false colour image, images with the included cloud masks, and only one of the bits in the cloud mask.

![pic1](/Images/S1_n.png)
Northwestern Australia using channel S1

![pic2](/Images/northeraustralia_falsecolour.png)
 False colour image of Northwestern Australia using channel S1, S2, S3 (S1=blue, S2=green, S3=red)
 
ACTION: FIND atlantic file + upload to 

Questions:
- why are there no b channels for S1-3?
- what do the missing cells in the table mean? 
- should we fix the S7-9 channel reading?

