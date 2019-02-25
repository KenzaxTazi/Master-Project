
##############################################
# (c) Copyright 2018-2019 Kenza Tazi and Thomas Zhu
# This software is distributed under the terms of the GNU General Public
# Licence version 3 (GPLv3)
##############################################

import datetime
import pandas
import numpy as np
import tflearn
from tflearn.layers.core import dropout, fully_connected, input_data
from tflearn.layers.estimator import regression

import DataPreparation as dp


class FFN():
    """Object for handling TFLearn DNN models with added support for saving / loading different network configurations"""

    def __init__(self, name, networkConfig=None, para_num=24, LR=1e-3):
        self.name = name
        self.networkConfig = networkConfig
        self.para_num = para_num
        self.LR = LR
        self.isLoaded = False
        self._model = None
        self._network = None
        self.run_id = None

    def __str__(self):
        out = ('Model: ' + self.name + '\n'
               + 'Network type: ' + str(self.networkConfig) + '\n'
               + 'Number of inputs: ' + str(self.para_num))
        return(out)

    def Network0(self):
        # Networks layers

        # layer 0: generates a 4D tensor
        layer0 = input_data(shape=[None, self.para_num], name='input')

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
        softmax = fully_connected(dropout4, 1, activation='softmax')

        # gives the paramaters to optimise the network
        self._network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                   loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'Network0'

    def Network1(self):
        # Network layers

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
        self._network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                   loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'Network1'

    def Network2(self):
        # Network layers

        # layer 0: generates a 4D tensor
        layer0 = input_data(shape=[None, self.para_num], name='input')

        # layer 1
        layer1 = fully_connected(layer0, 32, activation='linear')
        # dropout1 = dropout(layer1, 0.8)

        # layer 2
        layer2 = fully_connected(layer1, 32, activation='relu')
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
        self._network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                   loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'Network2'

    def Network3(self):
        # Network layers

        # layer 0: generates a 4D tensor
        layer0 = input_data(shape=[None, self.para_num], name='input')
        dropout0 = dropout(layer0, 0.8)

        # layer 1
        layer1 = fully_connected(dropout0, 32, activation='leakyrelu')
        dropout1 = dropout(layer1, 0.8)

        # layer 2
        layer2 = fully_connected(dropout1, 32, activation='leakyrelu')
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
        self._network = regression(softmax, optimizer='Adam', learning_rate=self.LR,
                                   loss='categorical_crossentropy', name='targets')
        self.networkConfig = 'Network1'

    @property
    def network(self):
        if self._network is not None:
            return self._network

        if self.networkConfig is None:
            print('Using default network configuration, Network0')
            self.Network0()
        else:
            # Use network function specified by networkConfig
            networkFunc = getattr(self, self.networkConfig)
            networkFunc()
        return self._network

    @property
    def model(self):
        if self._model:
            return self._model

        self._model = tflearn.DNN(
            self.network, tensorboard_verbose=0, tensorboard_dir='./Temp/tflearn_logs')

        return self._model

    def Train(self, training_data, training_truth, validation_data, validation_truth, n_epoch=16):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.run_id = 'Models/' + str(self.name) + '_' + timestamp
        self.model.fit(training_data, training_truth, n_epoch=n_epoch,
                       validation_set=(validation_data, validation_truth),
                       snapshot_step=10000, show_metric=True, run_id=self.run_id)
        self.isLoaded = True

    def Save(self, path=None):
        if path:
            self.model.save(path)
            with open(path + '.txt', 'w') as file:
                file.write(self.networkConfig + '\n')
                file.write(str(self.para_num) + '\n')
                file.write(str(self.run_id))
        else:
            self.model.save("Models/" + self.name)
            with open("Models/" + self.name + '.txt', 'w') as file:
                file.write(self.networkConfig + '\n')
                file.write(str(self.para_num) + '\n')
                file.write(str(self.run_id))

    def Load(self, path=None, verbose=True):
        if self.isLoaded:
            raise AssertionError(
                'Graph already loaded. Consider loading into new object.')

        if path:
            with open(path + '.txt', 'r') as file:
                settings = file.readlines()
                if len(settings) == 1:
                    self.networkConfig = settings[0]

                elif len(settings) >= 2:
                    self.networkConfig = settings[0].strip()
                    self.para_num = int(settings[1].strip())

            self.model.load(path)

        else:
            with open('Models/' + self.name + '.txt', 'r') as file:
                settings = file.readlines()
                if len(settings) == 1:
                    self.networkConfig = settings[0]

                elif len(settings) >= 2:
                    self.networkConfig = settings[0].strip()
                    self.para_num = int(settings[1].strip())

            self.model.load('Models/' + self.name)

        self.isLoaded = True
        if verbose:
            print('##############################################')
            print('Loading successful')
            print('Model: ' + self.name)
            print('Network type: ' + self.networkConfig)
            print('Number of inputs: ' + str(self.para_num))
            print('##############################################')

    def Predict(self, X):
        return(self.model.predict(X))

    def Predict_label(self, X):
        return(self.model.predict_label(X))

    def apply_mask(self, Sreference):
        if self.isLoaded is False:
            raise AssertionError(
                'Model is neither loaded nor trained, cannot make predictions')

        inputs = dp.getinputsFFN(Sreference, input_type=self.para_num)

        returnlist = []

        label = self.model.predict_label(inputs)
        lmask = np.array(label)
        lmask = lmask[:, 0].reshape(2400, 3000)
        returnlist.append(lmask)

        prob = self.model.predict(inputs)
        pmask = np.array(prob)
        pmask = pmask[:, 0].reshape(2400, 3000)
        returnlist.append(pmask)

        return returnlist


if __name__ == '__main__':
    # Pixel Loading
    df = dp.PixelLoader('./SatelliteData/SLSTR/Pixels3')

    tdata, vdata, ttruth, vtruth = df.dp.get_ffn_training_data(22)

    model = FFN('Test', 'Network1', 22)
    model.Train(tdata, ttruth, vdata, vtruth)
    model.Save()
