#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:37:26 2018

@author: kenzatazi
"""

import pandas as pd
import ModelEvaluation as me
import matplotlib.pyplot as plt
import sklearn.utils
import DataPreparation as dp
import tflearn
from ffn2 import FFN
import numpy as np
from tensorflow import reset_default_graph
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression
import datetime
'''
training_data, validation_data, training_truth, validation_truth, bayes_values, emp_values = dp.pkl_prep_data(
    '/home/hep/trz15/Matched_Pixels2/Calipso', bayesian=False, empirical=False)
'''

# prepares data for ffn
training_data, validation_data, training_truth, validation_truth, _ , _, times = dp.pkl_prep_data(
    '/Users/kenzatazi/Desktop/SatelliteData/SLSTR/Pixels2', TimeDiff=True)


# If dataset already created :
'''
training_data = np.load('training_data.npy')
validation_data = np.load('validation_data.npy')
training_truth = np.load('training_truth.npy')
validation_truth =np.load('validation_truth.npy')
'''

# Creating network and setting hypermarameters for model

# MACHINE LEARNING MODEL
LR = 1e-3  # learning rate
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
MODEL_NAME = 'Models/ffn_withancillarydata_' + timestamp
para_num = 24

# reshape data to pit into network
training_data = training_data.reshape(-1, para_num)
validation_data = validation_data.reshape(-1, para_num)

model = FFN('Net1_S_FFN', 'Network1')
model.networkSetup()
model.Setup()
model.Train(training_data, training_truth, validation_data,
            validation_truth)


time_slices = np.linspace(0, 1401, 15)
accuracies = []
N = []

for t in time_slices:
    new_validation_data = []
    new_validation_truth = []

    # slices
    for i in range(len(validation_data)):
        if abs(times[i]) > t:
            if abs(times[i]) < t+100:
                new_validation_data.append(validation_data[i])
                new_validation_truth.append(validation_truth[i])

    new_validation_data = np.array(new_validation_data)
    new_validation_truth = np.array(new_validation_truth)

    if len(new_validation_data) > 0:

        new_validation_data = new_validation_data.reshape(-1, para_num)
        # Print accuracy
        acc = me.get_accuracy(
            model.model, new_validation_data, new_validation_truth)
        accuracies.append(acc)

        # apply model to test images to generate masks
        '''
        for scn in scenes:
            app.apply_mask(model, scn)
            plt.show()
        '''
        N.append(len(new_validation_data))

    else:
        accuracies.append(0)
        N.append(0)


plt.figure('Accuracy vs time difference')
plt.title('Accuracy as a function of time difference')
plt.xlabel('Absolute time difference (s)')
plt.ylabel('Accuracy')
plt.bar(time_slices, accuracies, width=100, align='edge',
        color='lightcyan',  edgecolor='lightseagreen', yerr=(np.array(accuracies)/np.array(N))**(0.5))
plt.show()

# resets the tensorflow environment
reset_default_graph()
