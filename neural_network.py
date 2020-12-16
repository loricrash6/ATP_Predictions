from keras.layers import BatchNormalization, Dense, Input, Dropout
from keras.models import Model
from keras import backend as K
import tensorflow as tf
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
from keras.optimizers import SGD

def odds_loss(y_true, y_pred):
  """
  The function implements the custom loss function
    
  Inputs
  true : a vector of dimension batch_size, 7. A label encoded version of the output and the backp1_a and backp1_b
  pred : a vector of probabilities of dimension batch_size , 5.
    
  Returns 
  the loss value
  """
  win_p1 = y_true[:, 0:1]
  win_p2 = y_true[:, 1:2]
  no_bet = y_true[:, 2:3]
  odds_p1 = y_true[:, 3:4]
  odds_p2 = y_true[:, 4:5]

  #tf.print("Bets on p1",K.sum(y_pred[:, 0:1]))
  #tf.print("Bets on p2",K.sum(y_pred[:, 1:2]))
    
  gain_loss_vector = K.concatenate([win_p1 * (odds_p1 - 1) + (1 - win_p1) * -1,
    win_p2 * (odds_p2 - 1) + (1 - win_p2) * -1,
    K.zeros_like(odds_p1)], axis=1)
    
  #gain_loss_vector = K.concatenate([win_p1 * (odds_p1 - 1) + (1 - win_p1) * -1,
  #  win_p2 * (odds_p2 - 1) + (1 - win_p2) * -1,
  #  -K.ones_like(odds_p1)*0.1], axis=1) #penalize not betting a bit
  return -1 * K.mean(K.sum(gain_loss_vector * y_pred, axis=1))



def accuracy_metric(y_pred, y_true):
  winning_bets = tf.math.reduce_sum(tf.cast(y_true[:, 0:3]==y_pred[:, 0:3], tf.float32))
  #winning_bets = tf.reduce_sum(tf.cast(tf.reduce_all(tf.math.equal(y_true[:, 0:3], y_pred[:, 0:3]), 0), tf.float32))

  return winning_bets/tf.cast(tf.shape(y_pred)[0], tf.float32)

def get_model(input_dim, output_dim, base=100, multiplier=0.25, p=0.2):
    #check dimensions of tensors
    inputs = Input(shape=(input_dim,))
    l = BatchNormalization()(inputs)
    l = Dropout(p)(l)
    n = base
    l = Dense(n, activation='relu')(l)
    l = BatchNormalization()(l)
    l = Dropout(p)(l)
    n = int(n * multiplier)
    l = Dense(n, activation='relu')(l)
    l = BatchNormalization()(l)
    l = Dropout(p)(l)
    n = int(n * multiplier)
    l = Dense(n, activation='relu')(l)
    
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)


    outputs = Dense(output_dim, activation='softmax')(l)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=sgd, loss=odds_loss)
    #model.compile(optimizer='Nadam', loss='binary_crossentropy', metrics=['accuracy']) #add ROI to metrics
    return model