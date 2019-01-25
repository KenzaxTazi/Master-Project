#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 14:37:40 2018

@author: kenzatazi
"""

# Evaluating the model

import matplotlib.pyplot as plt
from sklearn import metrics
import tensorflow as tf
import numpy as np


def get_accuracy(model, validation_data, validation_truth, para_num=24):

    """ returns model accuracy """

    validation_data = np.concatenate(validation_data)
    validation_data = validation_data.reshape(-1, para_num)

    validation_truth = np.concatenate(validation_truth)
    validation_truth = validation_truth.reshape(-1, 2)

    accuracy = model.evaluate(validation_data, validation_truth)

    return accuracy[0]


def ROC_curve(model, validation_data, validation_truth, bayes_mask=None,
              name=None):

    """Plots Receiver Operating Characteristic (ROC) curve"""

    para_num = len(validation_data[0])
    validation_data = np.concatenate(validation_data)
    validation_data = validation_data.reshape(-1, para_num)
    validation_truth = np.concatenate(validation_truth)
    validation_truth = validation_truth.reshape(-1, 2)

    predictions = model.predict(validation_data)

    false_positive_rate, true_positive_rate, thresholds = metrics.roc_curve(
            validation_truth[:, 1], predictions[:, 1], pos_label=1)

    if name is None:
        plt.figure('ROC curve')
        plt.title('ROC curve')
    else:
        plt.figure(name + ' ' + 'ROC curve')
        plt.title(name + ' ' + 'ROC curve')
    plt.plot(false_positive_rate, true_positive_rate)
    plt.xlabel('False positive rate')
    plt.ylabel('True positive rate')
    plt.plot([0, 1], [0, 1], label="random classifier")

    if bayes_mask is not None:
        false_positive_rate2, true_positive_rate2, thresholds2\
            = metrics.roc_curve(validation_truth[:, 0],
                                bayes_mask, pos_label=1)
        plt.scatter(false_positive_rate2, true_positive_rate2)


def AUC(model, validation_data, validation_truth):

    """Returs area under Receiver Operating Characteristic (ROC) curve"""

    predictions = model.predict(validation_data)

    auc = metrics.roc_auc_score(validation_truth[:, 1], predictions[:, 1])
    return auc


def precision_vs_recall(model, validation_data, validation_truth):

    """Plots precision vs recall curve"""

    predictions = np.nan_to_num(model.predict(validation_data))

    precision, recall, thresholds = metrics.precision_recall_curve(
            validation_truth[:, 1], predictions[:, 1], pos_label=1)

    plt.figure('Precision vs recall curve')
    plt.title('Precision vs recall curve')
    plt.plot(precision, recall)
    plt.xlabel('Precision')
    plt.ylabel('Recall')


def confusion_matrix(model, validation_data, validation_truth):

    """ Returns a confusion matrix"""

    labels = model.predict_label(validation_data)
    matrix = tf.confusion_matrix(validation_truth[:, 1],
                                           labels[:, 1])
    with tf.Session().as_default() as sess:
        m = tf.Tensor.eval(matrix, feed_dict=None, session=sess)
    return m
