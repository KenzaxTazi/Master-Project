#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  6 17:29:23 2019

@author: kenzatazi
"""

import numpy as np
import DataLoader as DL


def prep_data(pixel_info):

    """
    Prepares data for matched SLSTR and CALIOP pixels into training data,
    validation data, training truth data, validation truth data.

    """

    conv_pixels = pixel_info.astype(float)
    pix = np.nan_to_num(conv_pixels)

    data = pix[:, :-2]
    truth_flags = pix[:, -2]

    truth_oh = []

    for d in truth_flags:
        i = DL.vfm_feature_flags(int(d))
        if i == 2:
            truth_oh.append([1., 0.])    # cloud
        if i != 2:
            truth_oh.append([0., 1.])    # not cloud

    pct = int(len(data)*.15)
    training_data = np.array(data[:-pct])    # take all but the 15% last
    validation_data = np.array(data[-pct:])    # take the last 15% of pixels
    training_truth = np.array(truth_oh[:-pct])
    validation_truth = np.array(truth_oh[-pct:])

    np.save('training_data.npy', training_data)
    np.save('validation_data.npy', validation_data)
    np.save('training_truth.npy', training_truth)
    np.save('validation_truth.npy', validation_truth)

    return training_data, validation_data, training_truth, validation_truth


def surftype_class(array):
    """
    Bitwise processing of SLSTR surface data. The different surface types are :
    1: coastline
    2: ocean
    4: tidal
    8: land
    16: inland_water
    32: unfilled
    64: spare
    128: spare
    256: cosmetic
    512: duplicate
    1024: day
    2048: twilight
    4096: sun_glint
    8192: snow
    16384: summary_cloud
    32768: summary_pointing

    Input: array of matched pixel information
    Output: arrays of matched pixel information for each surface typ
    """

    coastline = []
    ocean = []
    tidal = []
    land = []
    inland_water = []
    unfilled = []
    spare1 = []
    spare2 = []
    cosmetic = []
    duplicate = []
    day = []
    twilight = []
    sun_glint = []
    snow = []
    summary_cloud = []
    summary_pointing = []

    # sorting data point into surface type categories using bitwise addition
    for d in array:
        if int(d[11]) & 1 > 0:
            coastline.append(d)
        if int(d[11]) & 2 > 0:
            ocean.append(d)
        if int(d[11]) & 4 > 0:
            tidal.append(d)
        if int(d[11]) & 8 > 0:
            land.append(d)
        if int(d[11]) & 16 > 0:
            inland_water.append(d)
        if int(d[11]) & 32 > 0:
            unfilled.append(d)
        if int(d[11]) & 64 > 0:
            spare1.append(d)
        if int(d[11]) & 128 > 0:
            spare2.append(d)
        if int(d[11]) & 256 > 0:
            cosmetic.append(d)
        if int(d[11]) & 512 > 0:
            duplicate.append(d)
        if int(d[11]) & 1024 > 0:
            day.append(d)
        if int(d[11]) & 2048 > 0:
            twilight.append(d)
        if int(d[11]) & 4096 > 0:
            sun_glint.append(d)
        if int(d[11]) & 8192 > 0:
            snow.append(d)
        if int(d[11]) & 16384 > 0:
            summary_cloud.append(d)
        if int(d[11]) & 32768 > 0:
            summary_pointing.append(d)

    coastline = np.array(coastline)
    ocean = np.array(ocean)
    tidal = np.array(tidal)
    land = np.array(land)
    inland_water = np.array(inland_water)
    unfilled = np.array(unfilled)
    spare1 = np.array(spare1)
    spare2 = np.array(spare2)
    cosmetic = np.array(cosmetic)
    duplicate = np.array(duplicate)
    day = np.array(day)
    twilight = np.array(twilight)
    sun_glint = np.array(sun_glint)
    snow = np.array(snow)
    summary_cloud = np.array(summary_cloud)
    summary_pointing = np.array(summary_pointing)

    return [coastline, ocean, tidal, land, inland_water, unfilled, spare1,
            spare2, cosmetic, duplicate, day, twilight, sun_glint, snow,
            summary_cloud, summary_pointing]


def surftype_processing(array):
    """
    Bitwise processing of SLSTR surface data. The different surface types are :
    1: coastline
    2: ocean
    4: tidal
    8: land
    16: inland_water
    32: unfilled
    64: spare
    128: spare
    256: cosmetic
    512: duplicate
    1024: day
    2048: twilight
    4096: sun_glint
    8192: snow
    16384: summary_cloud
    32768: summary_pointing

    Input: array of matched pixel information
    Output: array of matched pixel information with processed surface type
    """
    # FIXME
