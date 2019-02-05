#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 16:37:26 2018

@author: kenzatazi
"""

import datetime
import os

import matplotlib.pyplot as plt
import sklearn.utils
import tflearn
import tensorflow as tf
from tensorflow import reset_default_graph
from tflearn.layers.core import dropout, fully_connected, input_data
from tflearn.layers.estimator import regression
from tflearn.layers.conv import conv_2d, max_pool_2d

import DataPreparation as dp
import ModelApplication as app
import ModelEvaluation as me
import DataLoader as DL
import Visualisation as Vis
import numpy as np


class Supermodel():
    """Object for handling TFLearn DNN models with added support for saving / loading different network configurations"""

    def __init__(self, name, networkConfig=None, para_num=24, LR=1e-3, img_length=8, img_width=25):
        self.name = name
        self.networkConfig = networkConfig
        self.para_num = para_num
        self.LR = LR
        self.img_length = img_length
        self.img_width = img_width

    def ffn1(self):
        # Feed Forward Network layers

        # layer 0: generates a 4D tensor
        layer0 = input_data(shape=[None, self.para_num], name='input')

        # layer 1
        layer1 = fully_connected(layer0, 32, activation='leakyrelu')
        # dropout1 = dropout(layer1, 0.8)

        # layer 2
        layer2 = fully_connected(layer1, 32, activation='leakyrelu')
        dropout2 = dropout(layer2, 0.8)

        # layer 3
        layer3 = fully_connected(dropout2, 32, activation='leakyrelu')
        dropout3 = dropout(layer3, 0.8)

        # layer 4
        layer4 = fully_connected(dropout3, 32, activation='leakyrelu')
        dropout4 = dropout(layer4, 0.8)

        # layer 5 this layer needs to spit out the number of categories
        # we are looking for.
        softmax = fully_connected(dropout4, 2, activation='softmax')

        # gives the paramaters to optimise the network
        self.network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                  loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'ffn'

    def cnn(self):

        # Convolutional Network layers

        # Layer 0: generates a 4D tensor
        convnet = input_data(
            shape=[None, self.img_length, self.img_width], name='input')

        # Layer 1
        convnet = conv_2d(convnet, nb_filter=32,
                          filter_size=5, activation='relu')
        convnet = max_pool_2d(convnet, kernel_size=5)

        # Layer 2
        convnet = conv_2d(convnet, nb_filter=64,
                          filter_size=5, activation='relu')
        convnet = max_pool_2d(convnet, kernel_size=5)

        # Layer 3
        convnet = conv_2d(convnet, nb_filter=128,
                          filter_size=5, activation='relu')
        convnet = max_pool_2d(convnet, kernel_size=5)

        # Layer 4
        convnet = conv_2d(convnet, nb_filter=64,
                          filter_size=5, activation='relu')
        convnet = max_pool_2d(convnet, kernel_size=5)

        # Layer 5
        convnet = conv_2d(convnet, nb_filter=32,
                          filter_size=5, activation='relu')
        convnet = max_pool_2d(convnet, kernel_size=5)

        # Layer 6
        convnet = fully_connected(convnet, 1024, activation='relu')
        convnet = dropout(convnet, keep_prob=0.8)

        # Layer 7
        softmax = fully_connected(convnet, 2, activation='softmax')

        # gives the paramaters to optimise the network
        self.network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                  loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'cnn'

    def ffn2(self):

        # Merge outputs from CNN with FFN1

        # layer -1: generates a 4D tensor
        layer0 = input_data(shape=[None, 2], name='input')

        # Feed Forward Networks layers

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

        # layer 5
        layer5 = fully_connected(dropout4, 32, activation='relu')
        dropout5 = dropout(layer5, 0.8)

        # layer 6 this layer needs to spit out the number of categories
        # we are looking for.
        softmax = fully_connected(dropout5, 2, activation='softmax')

        self.network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                  loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'fnn2'

    def Setup(self):
        self.model = tflearn.DNN(
            self.network, tensorboard_verbose=0, tensorboard_dir='./Temp/tflearn_logs')

    def Train(self, training_data, training_truth, validation_data, validation_truth):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        MODEL_NAME = 'Models/ffn_withancillarydata_' + timestamp
        self.model.fit(training_data, training_truth, n_epoch=2,
                       validation_set=(validation_data, validation_truth),
                       snapshot_step=10000, show_metric=True, run_id=MODEL_NAME)

    def Save(self):
        self.model.save("Models/" + self.name)
        with open("Models/" + self.name + '.txt', 'w') as file:
            file.write(self.networkConfig)

    def trainffn1(self, training_data, validation_data, training_truth, validation_truth, LR=1e-3, modelname='Models/supermodelffn'):
        """ runs the first FFN model """

        para_num = training_data.shape[-1]

        # reshape data to pit into network
        training_data = training_data.reshape(-1, para_num)
        validation_data = validation_data.reshape(-1, para_num)

        model = Supermodel('SM_FFN1', 'ffn11')
        model.Setup()
        model.Train(training_data, training_truth,
                    validation_data, validation_truth)
        model.Save()

        return model

    def traincnn(self, training_data, validation_data, training_truth, validation_truth,
                 LR=1e-3, modelname='Models/supermodelcnn'):
        """ runs the CNN model """

        para_num = training_data.shape[-1]

        # reshape data to pit into network
        training_data = training_data.reshape(-1, para_num)
        validation_data = validation_data.reshape(-1, para_num)

        model = Supermodel('SM_CNN', 'cnn')
        model.Setup()
        model.Train(training_data, training_truth,
                    validation_data, validation_truth)
        model.Save()

        return model

    def trainffn2(self, training_data, validation_data, training_truth, validation_truth,
                  LR=1e-3, modelname='Models/supermodelffn'):
        """ runs the two models together """

        para_num = training_data.shape[-1]

        # reshape data to pit into network
        training_data = training_data.reshape(-1, para_num)
        validation_data = validation_data.reshape(-1, para_num)

        model = Supermodel('SM_FFN2', 'ffn2')
        model.Setup()
        model.Train(training_data, training_truth,
                    validation_data, validation_truth)
        model.Save()

        return model

    def SM_train(self, data):
        ftd, fvd, ctd, cvd, tt, vt, _, _ = dp.SM_prep_data(
            data)  # TODO write function

        FFN1 = self.trainffn1(ftd, fvd, tt, vt)
        CNN = self.traincnn(ctd, cvd, tt, vt)

        f_training_predictions = FFN1.predict(ftd)
        c_training_predictions = CNN.predict(ctd)
        f_validation_predictions = FFN1.predict(fvd)
        c_validation_predictions = CNN.predict(cvd)

        training_data = np.column_stack(
            (f_training_predictions, c_training_predictions))
        validation_data = np.column_stack(
            (f_validation_predictions, c_validation_predictions))

        FFN2 = self.trainffn2(training_data, tt, validation_data, vt)

        return FFN1, CNN, FFN2

    def SM_predict(self, FFN1, CNN, FFN2, testdata, Sreference):

        scene = DL.scene_loader(Sreference)

        ftestdata = dp.getinputs(scene, num_inputs=24, indices=True) #include indices
        indices = ftestdata[-1]

        predictions1 = FFN1.predict(ftestdata[:-1]) #exclude indices when predicting 
        augm_data = np.column_stack((predictions1, indices)) # merge with indices

        gooddata = [x for x in augm_data if not(0.4 <=x[0] <0.6)]
        poordata = augm_data[0.4 <= augm_data[:, 0] < 0.6]
        
        ctestdata = dp.context_getinputs(scene, poordata)  
        predictions2 = CNN.predict(ctestdata[0])

        predictions3 = FFN2.predict(
            np.column_stack((augm_data[:,0], predictions2)))

        fixeddata= np.column_stack((predictions3, poordata[:,-1]))

        final_predictions_with_indices = np.concatenate(gooddata, fixeddata)
        final_predictions = (np.sort(final_predictions_with_indices))[:,0]

        return final_predictions


'''
if __name__ == '__main__':
    # Pixel Loading

    if os.path.exists('/vols/lhcb/egede/cloud'):
        # Script is running on lx02
        scenes = ['/vols/lhcb/egede/cloud/SLSTR/pacific_day/S3A_SL_1_RBT____20171120T190102_20171120T190402_20171122T003854_0179_024_341_2880_LN2_O_NT_002.SEN3',
                  '/vols/lhcb/egede/cloud/SLSTR/pacific_day/S3A_SL_1_RBT____20171217T190102_20171217T190402_20171218T223735_0179_025_341_2879_LN2_O_NT_002.SEN3',
                  '/vols/lhcb/egede/cloud/SLSTR/pacific_day/S3A_SL_1_RBT____20180113T190102_20180113T190402_20180114T230219_0179_026_341_2880_LN2_O_NT_002.SEN3',
                  '/vols/lhcb/egede/cloud/SLSTR/pacific_day/S3A_SL_1_RBT____20180209T190102_20180209T190402_20180210T234449_0179_027_341_2880_LN2_O_NT_002.SEN3']
        pixel_info = dp.PixelLoader("/home/hep/trz15/Matched_Pixels2/Calipso")

    if os.path.exists('/Users/kenzatazi'):
        # Script is running on Kenza's laptop
        scenes = ['/Users/kenzatazi/Desktop/S3A_SL_1_RBT____20180529T113003_20180529T113303_20180530T154711_0179_031_351_1620_LN2_O_NT_003.SEN3']
        pixel_info = dp.PixelLoader("/Users/kenzatazi/Desktop")

    if os.path.exists('D:'):
        scenes = []
        pixel_info = dp.PixelLoader(r"D:\SatelliteData\SLSTR\Pixels2")

    pixels = sklearn.utils.shuffle(pixel_info)

    pixel_values = (pixels[['S1_an', 'S2_an', 'S3_an', 'S4_an', 'S5_an', 'S6_an',
                            'S7_in', 'S8_in', 'S9_in', 'satellite_zenith_angle',
                            'solar_zenith_angle', 'latitude_an', 'longitude_an',
                            'confidence_an', 'bayes_in',
                            'Feature_Classification_Flags', 'TimeDiff']]).values

    # If dataset is not created:

    # prepares data for ffn
    training_data, validation_data, training_truth, validation_truth, _ = dp.SM_prep_data(
        pixel_values)

    # If dataset already created :
    
    training_data = np.load('training_data.npy')
    validation_data = np.load('validation_data.npy')
    training_truth = np.load('training_truth.npy')
    validation_truth =np.load('validation_truth.npy')
    

    # MACHINE LEARNING MODEL

    # Creating network and setting hypermarameters for model

    LR = 1e-3  # learning rate

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    MODEL_NAME = 'Models/ffn_withancillarydata_' + timestamp

    para_num = training_data.shape[-1]

    # reshape data to pit into network
    training_data = training_data.reshape(-1, para_num)
    validation_data = validation_data.reshape(-1, para_num)

    model = FFN('test1', 'Network2')
    model.networkSetup()
    model.Setup()
    model.Train(training_data, training_truth,
                validation_data, validation_truth)
    model.Save()

    Sfile = r"D:\SatelliteData\SLSTR\Dataset1\S3A_SL_1_RBT____20180822T000619_20180822T000919_20180822T015223_0179_035_016_3240_SVL_O_NR_003.SEN3"

    mask1 = app.apply_mask(model.model, Sfile)[0]

    # bmask = DL.extract_mask(Sfile, 'cloud_an', 64)
    bmask = DL.extract_mask(Sfile, 'bayes_in', 2)

    Vis.MaskComparison(Sfile, mask1, bmask, True, 1000)
'''
