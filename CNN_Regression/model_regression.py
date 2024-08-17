import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
from sklearn.model_selection import train_test_split

class CNN_REGRESSION(tf.keras.Model):
    def __init__(self):
        super(CNN_REGRESSION, self).__init__()
        # Define layers
        self.conv1 = layers.Conv1D(32, kernel_size=2, activation='relu')
        self.pool1 = layers.MaxPooling1D(pool_size=2)
        self.conv2 = layers.Conv1D(64, kernel_size=2, activation='relu')
        self.pool2 = layers.MaxPooling1D(pool_size=2)
        self.flatten = layers.Flatten()
        self.fc1 = layers.Dense(64, activation='relu')
        self.output_layer = layers.Dense(1)  # Single output for regression

    def call(self, inputs):
        # Define the forward pass
        x = self.conv1(inputs)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.pool2(x)
        x = self.flatten(x)
        x = self.fc1(x)
        return self.output_layer(x)