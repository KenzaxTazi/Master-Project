#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:37:26 2018

@author: kenzatazi
"""

import pandas as pd
import numpy as np
from random import shuffle
import vfm_feature_flags2 as vfm 
import ModelEvaluation as me
import DataPreparation as dp
import matplotlib.pyplot as plt
import sklearn.utils 
import ModelApplication as app
from satpy import Scene
from glob import glob

LR = 1e-3 #learning rate 


# Scenes to test on the HEP server 
scn1= Scene(filenames=glob('/home/hep/kt2015/cloud/SLSTR/2018/08/S3A_SL_1_RBT____20180823T041605_20180823T041905_20180824T083800_0179_035_033_1620_LN2_O_NT_003.SEN3/*'), 
           reader='nc_slstr')
scn2= Scene(filenames=glob('/home/hep/kt2015/cloud/SLSTR/2018/08/S3A_SL_1_RBT____20180829T200950_20180829T201250_20180831T004228_0179_035_128_1620_LN2_O_NT_003.SEN3/*'), 
           reader='nc_slstr')
scn3= Scene(filenames=glob('/home/hep/kt2015/cloud/SLSTR/2018/08/S3A_SL_1_RBT____20180829T200950_20180829T201250_20180831T004228_0179_035_128_1620_LN2_O_NT_003.SEN3/*'), 
           reader='nc_slstr')
scn4= Scene(filenames=glob('/home/hep/kt2015/cloud/SLSTR/2018/08/S3A_SL_1_RBT____20180829T200950_20180829T201250_20180831T004228_0179_035_128_1620_LN2_O_NT_003.SEN3/*'), 
           reader='nc_slstr')
scn5= Scene(filenames=glob('/home/hep/kt2015/cloud/SLSTR/2018/08/S3A_SL_1_RBT____20180829T200950_20180829T201250_20180831T004228_0179_035_128_1620_LN2_O_NT_003.SEN3/*'), 
           reader='nc_slstr')

scenes= [scn1, scn2, scn3, scn4, scn5]
'''
# Scene to test on users local laptop
scenes=[Scene(filenames=glob('/Users/kenzatazi/Desktop/S3A_SL_1_RBT____20180823T055704_20180823T060004_20180824T105957_0179_035_034_1620_LN2_O_NT_003.SEN3/*'))] 
'''
MODEL_NAME = 'ffn_withancillarydata'.format(LR, 'feedforward') 


# Date files on HEP server
pixel_info1 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Apr18P3.pkl")
pixel_info2 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/May18P3.pkl")
pixel_info3 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Feb18P3.pkl") 
pixel_info4 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Mar18P3.pkl")
pixel_info5 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Jun18P3.pkl")
#pixel_info6 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Jul18P3.pkl") 
pixel_info7 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Aug18P3.pkl") 
pixel_info8 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/Calipso/Jan18P3.pkl") 
pixel_info9 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/CATS/Aug17P3.pkl") 
pixel_info10 = pd.read_pickle("/home/hep/trz15/Matched_Pixels2/CATS/May17P3.pkl") 

'''
#Data files on users local laptop
pixel_info1 = pd.read_pickle("/Users/kenzatazi/Desktop/Apr18P3.pkl")
pixel_info2 = pd.read_pickle("/Users/kenzatazi/Desktop/May18P3.pkl")
pixel_info3 = pd.read_pickle("/Users/kenzatazi/Desktop/Feb18P3.pkl") 
pixel_info4 = pd.read_pickle("/Users/kenzatazi/Desktop/Mar18P3.pkl")
pixel_info5 = pd.read_pickle("/Users/kenzatazi/Desktop/Jun18P3.pkl")
#pixel_info6 = pd.read_pickle("/Users/kenzatazi/Desktop/Jul18P3.pkl") 
pixel_info7 = pd.read_pickle("/Users/kenzatazi/Desktop/Aug18P3.pkl") 
pixel_info8 = pd.read_pickle("/Users/kenzatazi/Desktop/Jan18P3.pkl")
pixel_info9 = pd.read_pickle("/Users/kenzatazi/Desktop/Aug17P3.pkl") 
pixel_info10 = pd.read_pickle("/Users/kenzatazi/Desktop/May17P3.pkl") 
'''

pixel_info = pd.concat([pixel_info1,pixel_info2,pixel_info3,pixel_info4,
                        pixel_info5,pixel_info7,pixel_info8,
                        pixel_info9, pixel_info10],
                        sort=False)

pixels = sklearn.utils.shuffle(pixel_info)

pixel_values = (pixels[['S1_an','S2_an','S3_an','S4_an','S5_an','S6_an',
                        'S7_in','S8_in','S9_in',
                        'satellite_zenith_angle', 'solar_zenith_angle', 
                        'latitude_an', 'longitude_an', 
                        'confidence_an',
                        'Feature_Classification_Flags',
                        'TimeDiff']]).values

para_num = len(pixel_values[0,:-2])


# If dataset is not created:

# prepares data for cnn 
training_data, validation_data, training_truth, validation_truth = dp.prep_data(pixel_values)

"""
# If dataset already created :
training_data = np.load('training_data.npy')
validation_data = np.load('validation_data.npy')
training_truth = np.load('training_truth.npy')
validation_truth =np.load('validation_truth.npy')
"""


#### MACHINE LEARNING 

import tflearn 
from tensorflow import reset_default_graph
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.estimator import regression


training_data= training_data.reshape(-1,1,para_num,1)
validation_data= validation_data.reshape(-1,1,para_num,1)

# Layer 0: generates a 4D tensor
layer0 = input_data(shape=[None, 1, para_num, 1], name='input')

# Layer 1
layer1 = fully_connected(layer0, 32, activation='relu')
dropout1 = dropout(layer1,0.8) ## what is dropout?

# Layer 2
layer2 = fully_connected(dropout1, 32, activation='relu')
dropout2 = dropout(layer2,0.8)

# Layer 3
layer3 = fully_connected(dropout2, 32, activation='relu')
dropout3 = dropout(layer3,0.8)

# Layer 4
layer4 = fully_connected(dropout3, 32, activation='relu')
dropout4 = dropout(layer4,0.8)

#this layer needs to spit out the number of categories we are looking for.
softmax = fully_connected(dropout4, 2, activation='softmax') 


network = regression(softmax, optimizer='Adam', learning_rate=LR,
                     loss='categorical_crossentropy', name='targets')

model = tflearn.DNN(network, tensorboard_verbose=0)


"""

model.save(MODEL_NAME)

### UNPACK SAVED DATA
if os.path.exists('/Users/kenzatazi/Documents/University/Year 4/Msci Project/{}.meta'.format(MODEL_NAME)):
    model.load(MODEL_NAME)
    print('model loaded!')
    
"""

model.fit(training_data, training_truth, n_epoch=2, validation_set =
          (validation_data, validation_truth), snapshot_step=10000, 
          show_metric=True, run_id=MODEL_NAME)


acc= me.get_accuracy(model,validation_data,validation_truth)        

app.apply_mask(model, scenes)

#model.save('my_model.tflearn')

reset_default_graph()
    

plt.show()

    
        


    
    