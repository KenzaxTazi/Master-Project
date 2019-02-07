
##############################################
# (c) Copyright 2018-2019 Kenza Tazi and Thomas Zhu                                        
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPLv3)
##############################################

import io
import os
import zipfile
from ftplib import FTP

import requests
from tqdm import tqdm


def FTPlogin(creds_path='credentials.txt'):
    ftp = FTP('ftp.ceda.ac.uk')
    with open(creds_path, 'r') as file:
        username, password = file.readlines()
        ftp.login(username.strip(), password.strip())
    ftp.cwd('neodc/sentinel3a/data/SLSTR/L1_RBT')
    return(ftp)


def FTPdownload(ftpobj, path, destination):
    startdir = os.getcwd()
    os.chdir(destination)
    if path[:3] == "S3A":   # given path is folder name
        foldername = path
        path = path = path[16:20] + '/' + path[20:22] + \
            '/' + path[22:24] + '/' + path[:]
    elif path[:2] == "20":   # given path is path from /L1_RBT
        foldername = path[11:]
    try:
        ftpobj.retrbinary("RETR " + str(path),
                          open(str(foldername), "wb").write)
    except:
        print("Permission Error")
        print(foldername)
        try:
            os.remove(foldername)
        except:
            pass
        return(1)
    os.chdir(startdir)
    print('Download complete')
    return(0)

def NASA_download(NASA_FTP_directory, calipso_directory="", CATS_directory=""):
    """Download Calipso or CATS files from NASA"""
    print("Connecting to NASA server...")
    ftp = FTP('xfr140.larc.nasa.gov')
    ftp.login('anonymous', 'trz15@imperial.ac.uk')
    ftp.cwd(NASA_FTP_directory)
    available_files = ftp.nlst()

    # Select all .hdf files if Calipso
    if calipso_directory != "":
        files_to_download = [str(i)
                             for i in available_files if str(i)[-1] == 'f']
        print("Beginning download...")
        try:
            os.chdir(calipso_directory)
        except FileNotFoundError:
            os.mkdir(calipso_directory)
            os.chdir(calipso_directory)

    # Select all .hdf5 files if CATS
    if CATS_directory != "":
        files_to_download = [str(i)
                             for i in available_files if str(i)[-1] == '5']
        print("Beginning download...")
        try:
            os.chdir(CATS_directory)
        except FileNotFoundError:
            os.mkdir(CATS_directory)
            os.chdir(CATS_directory)

    files_present = os.listdir()

    for i in tqdm(files_to_download):
        if i not in files_present:
            ftp.retrbinary("RETR " + str(i), open(str(i), "wb").write)


def CEDA_download_matches(MatchesFilename, SLSTR_target_directory, creds_path='credentials.txt'):
    """Function to download SLSTR files in a Matches.txt from CEDA's FTP server"""
    failed_downloads = []

    with open(MatchesFilename, 'r') as file:
        data = file.readlines()

    # Get list of unique SLSTR files from Matches file
    Sfiles = [i.split(',')[1] for i in data]

    ftp = FTPlogin(creds_path)

    startdir = os.getcwd()

    try:
        os.chdir(SLSTR_target_directory)
    except FileNotFoundError:
        os.mkdir(SLSTR_target_directory)
        os.chdir(SLSTR_target_directory)

    # List of files which are already downloaded
    q = os.listdir()

    # List of files which have not been downloaded yet
    Sfiles1 = []

    for i in range(len(Sfiles)):
        if Sfiles[i] + ".SEN3" not in q:
            Sfiles1.append(Sfiles[i])

    # List of file paths on CEDA which need to be downloaded
    Sfiles2 = []

    for i in tqdm(range(len(Sfiles1))):
        path = Sfiles1[i]
        path = path[16:20] + '/' + path[20:22] + \
            '/' + path[22:24] + '/' + path[:] + '.zip'
        Sfiles2.append(path)

    # Complete the downloads
    for i in tqdm(range(len(Sfiles2))):
        targetfile = Sfiles2[i]  # File on CEDA to download
        # Name of file when downloaded
        downloadedfile = str(Sfiles1[i] + ".zip")
        tqdm.write('Downloading ' + str(targetfile))
        try:
            ftp.retrbinary("RETR " + targetfile,
                           open(downloadedfile, "wb").write)
            z = zipfile.ZipFile(downloadedfile)
            z.extractall()
            os.remove(downloadedfile)
        except Exception as e:
            tqdm.write('Error downloading ' + str(targetfile))
            tqdm.write('Error: %s' % e)
            failed_downloads.append(Sfiles1[i])
            try:
                os.remove(downloadedfile)
            except FileNotFoundError:
                pass

    os.chdir(startdir)
    return(failed_downloads)


def ESA_download_matches(MatchesFilename, SLSTR_target_directory):
    with open(MatchesFilename, 'r') as file:
        data = file.readlines()
        Sfiles = [i.split(',')[1] for i in data]
        Sdownloads = [i.split(',')[2].strip() for i in data]

    # List of files which are already downloaded
    q = os.listdir(SLSTR_target_directory)

    # List of files and URLs which have are not already present in the final directory
    Sfiles1 = []
    Sdownloads1 = []

    for i in range(len(Sfiles)):
        if Sfiles[i] + ".SEN3" not in q:
            Sfiles1.append(Sfiles[i])
            Sdownloads1.append(Sdownloads[i])

    olddir = os.getcwd()

    try:
        os.chdir(SLSTR_target_directory)
    except FileNotFoundError:
        os.mkdir(SLSTR_target_directory)
        os.chdir(SLSTR_target_directory)

    # Keep track of files which fail to download
    faileddownloads = []

    # Download the files which are not yet present
    for i in tqdm(range(len(Sdownloads1))):
        S_URL = Sdownloads1[i]
        tqdm.write('Downloading from ' + S_URL)
        if S_URL.endswith('$value'):
            url = S_URL
        else:
            url = S_URL + '$value'
        r = requests.get(url, auth=('s3guest', 's3guest'))
        if r.status_code != 200:
            tqdm.write("Error downloading " + str(S_URL))
            faileddownloads.append(Sfiles1[i])
        else:
            try:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall()
            except Exception as e:
                tqdm.write("Error extracting " + str(S_URL))
                tqdm.write('Error: %s' % e)
                faileddownloads.append(Sfiles1[i])

    # Go back to previous directory
    os.chdir(olddir)
    return(faileddownloads)


def download_matches(MatchesFilename, SLSTR_target_directory, creds_path='credentials.txt'):
    failed_CEDA_downloads = CEDA_download_matches(
        MatchesFilename, SLSTR_target_directory, creds_path)
    if len(failed_CEDA_downloads) > 0:
        failed_ESA_downloads = ESA_download_matches(
            MatchesFilename, SLSTR_target_directory)

        failed_downloads = [
            i for i in failed_ESA_downloads if i in failed_CEDA_downloads]
    else:
        failed_downloads = []
    return(failed_downloads)
