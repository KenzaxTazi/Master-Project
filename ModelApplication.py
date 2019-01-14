#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  2 12:54:58 2018

@author: kenzatazi
"""

import numpy as np
from DataLoader import scene_loader, upscale_repeat
import DataPreparation as dp


def apply_mask(model, Sfile):
    """
    Function to produce predicted mask for given model and SLSTR file.

    Produces plot of the output mask overlayed on S1 channel data by default.
    Can also produce plots of SLSTR's included masks.

    Parameters
    ----------
    model: tflearn.DNN model object
        A trained tflearn model object which produces masks for N pixels given
        an (N, 1, model_inputs, 1) shaped tensor as input. Such models are
        produced by ffn.py and can be loaded from a local file using
        ModelApplication.py

    Sfile: str
        A path to an SLSTR file folder.

    Returns
    -------
    mask: array
        Mask predicted by model for Sfile
    """
    scn = scene_loader(Sfile)

    scn.load(['S1_an', 'S2_an', 'S3_an', 'S4_an', 'S5_an', 'S6_an', 'S7_in',
              'S8_in', 'S9_in', 'bayes_an', 'bayes_in', 'cloud_an',
              'latitude_an', 'longitude_an', 'satellite_zenith_angle',
              'solar_zenith_angle', 'confidence_an'])

    S1 = np.nan_to_num(scn['S1_an'].values)
    S2 = np.nan_to_num(scn['S2_an'].values)
    S3 = np.nan_to_num(scn['S3_an'].values)
    S4 = np.nan_to_num(scn['S4_an'].values)
    S5 = np.nan_to_num(scn['S5_an'].values)
    S6 = np.nan_to_num(scn['S6_an'].values)
    S7 = upscale_repeat(np.nan_to_num(scn['S7_in'].values))
    S8 = upscale_repeat(np.nan_to_num(scn['S8_in'].values))
    S9 = upscale_repeat(np.nan_to_num(scn['S9_in'].values))
    salza = upscale_repeat(np.nan_to_num(
        scn['satellite_zenith_angle'].values))
    solza = upscale_repeat(np.nan_to_num(scn['solar_zenith_angle'].values))
    lat = np.nan_to_num(scn['latitude_an'].values)
    lon = np.nan_to_num(scn['longitude_an'].values)
    confidence = np.nan_to_num(scn['confidence_an'].values)

    inputs = np.array([S1, S2, S3, S4, S5, S6, S7,
                       S8, S9, salza, solza, lat, lon, confidence])
    inputs = dp.surftype_processing(inputs)
    inputs = np.swapaxes(inputs, 0, 2)
    inputs = inputs.reshape((-1, 1, len(inputs), 1), order='F')

    label = model.predict_label(inputs)

    mask = np.array(label)
    mask = mask[:, 0].reshape(2400, 3000)

    return(mask)
