"""
Implements a custom metric for Keras, which considers a prediction a success if the true value is within the first 3
most probable values according to the network
"""

from keras.metrics import sparse_top_k_categorical_accuracy


def sparse_top_k_categorical_accuracy_3(*args):

    return sparse_top_k_categorical_accuracy(*args, k=3)