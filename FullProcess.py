# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 12:53:29 2018

@author: tomzh
"""
from Collocation2 import match_directory
import os
from SaveMatchedPixels import get_file_pairs, process_all, add_dist_col, add_time_col
from tqdm import tqdm
from FileDownloader import download_matches, NASA_download


Home_directory = "/home/hep/trz15/Masters_Project"
NASA_FTP_directory = "528836af-a8ec-45eb-8391-8d24324fe1b6"
calipso_directory = ""
CATS_directory = "/vols/lhcb/egede/cloud/CATS/2017/08/"
SLSTR_target_directory = "/vols/lhcb/egede/cloud/SLSTR/2017/08"
MatchesFilename = "Matches12.txt"
pkl_output_name = "Aug17.pkl"
timewindow = 20
creds_path = '/home/hep/trz15/Masters_Project/credentials.txt'

# Download Calipso file from NASA
NASA_download(NASA_FTP_directory, calipso_directory, CATS_directory)

# Find the SLSTR filenames which match the Calipso Filename
print("Beginning matching...")

os.chdir(Home_directory)
if calipso_directory != "":
    match_directory(calipso_directory, MatchesFilename, timewindow)
elif CATS_directory != "":
    match_directory(CATS_directory, MatchesFilename, timewindow)

# Download the files found by match_directory
failed_downloads = download_matches(MatchesFilename, SLSTR_target_directory, creds_path)

# Find matching pixels and store in pkl file
Cpaths, Spaths = get_file_pairs(SLSTR_target_directory, MatchesFilename, failed_downloads, calipso_directory, CATS_directory)
df = process_all(Spaths, Cpaths, pkl_output_name)
df['Profile_Time'] += 725846390.0
df = add_dist_col(df)
df = add_time_col(df)
processed_pkl_name = pkl_output_name[:-4] + "P1.pkl"
df.to_pickle(processed_pkl_name)
