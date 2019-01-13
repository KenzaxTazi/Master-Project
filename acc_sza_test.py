#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 16:27:14 2018

@author: kenzatazi
"""

import pandas as pd
import numpy as np
import ModelEvaluation as me
import matplotlib.pyplot as plt
import sklearn.utils
import DataPreparation as dp
import tflearn
from tensorflow import reset_default_graph
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression


# Training data files on HEP server
'''
pixel_info1 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Apr18P3.pkl")
pixel_info2 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             May18P3.pkl")
pixel_info3 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Feb18P3.pkl")
pixel_info4 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Mar18P3.pkl")
pixel_info5 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Jun18P3.pkl")
pixel_info6 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Jul18P3.pkl")
pixel_info7 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Aug18P3.pkl")
pixel_info8 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/\
                             Jan18P3.pkl")
pixel_info9 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/CATS/\
                             Aug17P3.pkl")
pixel_info10 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/CATS/\
                              May17P3.pkl")
'''

# Training data files on users local laptop
pixel_info1 = pd.read_pickle("/Users/kenzatazi/Desktop/Apr18P3.pkl")
pixel_info2 = pd.read_pickle("/Users/kenzatazi/Desktop/May18P3.pkl")
pixel_info3 = pd.read_pickle("/Users/kenzatazi/Desktop/Feb18P3.pkl")
pixel_info4 = pd.read_pickle("/Users/kenzatazi/Desktop/Mar18P3.pkl")
pixel_info5 = pd.read_pickle("/Users/kenzatazi/Desktop/Jun18P3.pkl")
# pixel_info6 = pd.read_pickle("/Users/kenzatazi/Desktop/Jul18P3.pkl")
pixel_info7 = pd.read_pickle("/Users/kenzatazi/Desktop/Aug18P3.pkl")
pixel_info8 = pd.read_pickle("/Users/kenzatazi/Desktop/Jan18P3.pkl")


pixel_info = pd.concat([pixel_info1, pixel_info2, pixel_info3, pixel_info4,
                        pixel_info5, pixel_info7, pixel_info8], sort=False)

pixels = sklearn.utils.shuffle(pixel_info)

pixel_values = (pixels[['S1_an', 'S2_an', 'S3_an', 'S4_an', 'S5_an', 'S6_an',
                        'S7_in', 'S8_in', 'S9_in',
                        'satellite_zenith_angle', 'solar_zenith_angle',
                        'latitude_an', 'longitude_an',
                        'confidence_an',
                        'Feature_Classification_Flags',
                        'TimeDiff']]).values

pixel_values = dp.surftype_processing(pixel_values)


# FEED FORWARD NETWORK

# If dataset is not created:

# prepares data for ffn
training_data, validation_data, training_truth, \
    validation_truth = dp.prep_data(pixel_values)

# If dataset already created :
'''
training_data = np.load('training_data.npy')
validation_data = np.load('validation_data.npy')
training_truth = np.load('training_truth.npy')
validation_truth =np.load('validation_truth.npy')
'''

# Creating network and setting hypermarameters for model

LR = 1e-3  # learning rate
MODEL_NAME = 'ffn_withancillarydata'.format(LR, 'feedforward')
para_num = len(pixel_values[0, :-2])

# reshape data to pit into network
training_data = training_data.reshape(-1, 1, para_num, 1)

# Networks layers

# layer 0: generates a 4D tensor
layer0 = input_data(shape=[None, 1, para_num, 1], name='input')

# layer 1
layer1 = fully_connected(layer0, 32, activation='relu')
dropout1 = dropout(layer1, 0.8)

# layer 2
layer2 = fully_connected(dropout1, 32, activation='relu')
dropout2 = dropout(layer2, 0.8)

# layer 3
layer3 = fully_connected(dropout2, 32, activation='relu')
dropout3 = dropout(layer3, 0.8)

# layer 4
layer4 = fully_connected(dropout3, 32, activation='relu')
dropout4 = dropout(layer4, 0.8)

# layer 5 this layer needs to spit out the number of categories
# we are looking for.
softmax = fully_connected(dropout4, 2, activation='softmax')

# gives the paramaters to optimise the network
network = regression(softmax, optimizer='Adam', learning_rate=LR,
                     loss='categorical_crossentropy', name='targets')
# creates the model
model = tflearn.DNN(network, tensorboard_verbose=0)
model.save(MODEL_NAME)


# If model is already created
"""
### UNPACK SAVED DATA
if os.path.exists('/Users/kenzatazi/Documents/University/\
Year 4/Msci Project/{}.meta'.format(MODEL_NAME)):
    model.load(MODEL_NAME)
    print('model loaded!')
"""


# TRAINING

angle_slices = np.linspace(6, 54, 9)
accuracies = []
N = []

for a in angle_slices:

    new_validation_data = []
    new_validation_truth = []

    # slices
    for i in range(len(validation_data)):
        if abs(int(validation_data[i, 9])) > a:
            if abs(int(validation_data[i, 9])) < a+6:
                new_validation_data.append(validation_data[i])
                new_validation_truth.append(validation_truth[i])

    new_validation_data = np.array(new_validation_data)
    new_validation_truth = np.array(new_validation_truth)

    if len(new_validation_data) > 0:

        new_validation_data = new_validation_data.reshape(-1, 1, para_num, 1)

        # Model training
        model.fit(training_data, training_truth, n_epoch=2,
                  validation_set=(new_validation_data, new_validation_truth),
                  snapshot_step=10000, show_metric=True, run_id=MODEL_NAME)

        # Print accuracy
        acc = me.get_accuracy(model, new_validation_data, new_validation_truth)
        accuracies.append(acc)

        # resets the tensorflow environment
        reset_default_graph()

        N.append(len(new_validation_data))

    else:
        accuracies.append(0)
        N.append(0)


plt.figure('Accuracy vs satellite zenith angle')
plt.title('Accuracy as a function of satellite zenith angle')
plt.xlabel('Satellite zenith angle (deg)')
plt.ylabel('Accuracy')
plt.bar(angle_slices, accuracies, width=6, align='edge', color='lavenderblush',
        edgecolor='thistle')
plt.errorbar(angle_slices, accuracies,
             yerr=(np.array(accuracies)/np.array(N))**(0.5), ls='none')
plt.show()
