"""
Generate chords based on the LSTM model
"""

from chords_ai.package_data import get_path_of_data_file
from chords_ai.custom_metric import sparse_top_k_categorical_accuracy_3
from chords_ai.player import ChordSequencePlayer

import os
from keras import models
from keras.preprocessing.sequence import pad_sequences
import json
import numpy as np


class ChordsAI(object):

    def __init__(self, model_file=None):

        if model_file is None:

            # Load default model
            model_file = get_path_of_data_file("model_best_songs.h5")

        else:

            # Load user-provided model
            assert os.path.exists(model_file), "Provided model file %s does not exist" % model_file

        # Actually load the Keras model
        self._model = models.load_model(model_file,
                                  custom_objects={
                                      'sparse_top_k_categorical_accuracy_3': sparse_top_k_categorical_accuracy_3})

        # Get the length of the sequences from the first layer (the Embedding layer)
        self._seq_length = self._model.layers[0].input_shape[1]

        # Now read in the vocabulary
        with open(get_path_of_data_file("best_songs_vocabulary.json")) as f:

            self._vocabulary = json.load(f)

        # Sort alphabetically to make sure that the order is correct
        # (we did this before training the network)
        self._vocabulary = sorted(self._vocabulary)

        # Prepare the mapping from chord to integer, and the inverse mapping as well
        self._mapping = {k: v for k, v in zip(self._vocabulary, range(len(self._vocabulary)))}
        self._inverse_mapping = {v: k for k, v in zip(self._vocabulary, range(len(self._vocabulary)))}

    def model_summary(self):
        """
        Summarize the model

        :return: None
        """

        self._model.summary()

    @property
    def vocabulary(self):
        """
        List of all the chords used for the model
        """
        return self._vocabulary

    @property
    def mapping(self):
        """
        Dictionary with mapping between chords and integers
        """
        return self._mapping

    @property
    def inverse_mapping(self):
        """
        Dictionary with mapping between integers and chords, useful to translate the output of the network
        """
        return self._inverse_mapping

    @property
    def length_of_sequences(self):
        """
        Length of chord sequences used for the training (and needed for the generation)
        """
        return self._seq_length

    def generate_random_sequence(self, n_chords_to_generate, play=False):

        # Get n_chords_to_generate random integers between 0 and the length of the vocabulary
        idx = np.random.randint(0, len(self._vocabulary), n_chords_to_generate)

        final_sequence = " ".join(map(lambda x:self._inverse_mapping[x], idx))

        if play:

            audio = ChordSequencePlayer().play(final_sequence)

        else:

            audio = None

        # Return the corresponding chords
        return final_sequence, audio

    def generate_seq(self, seed_chord_sequence, n_chords_to_generate, probabilistic=True, play=False):

        # Split input sequence into a list
        chord_sequence = seed_chord_sequence.split()

        assert len(chord_sequence) == self.length_of_sequences, \
            "You need to provide an input sequence of chords of length %s" % self.length_of_sequences

        # generate a fixed number of characters
        for _ in range(n_chords_to_generate):

            # encode the characters as integers
            encoded = [self._mapping[ch] for ch in chord_sequence]

            # truncate sequence to the last "seq_length" chords
            pad_encoded = pad_sequences([encoded], maxlen=self.length_of_sequences, truncating='pre')

            # get predictions from network
            # Remember: this is a vector of probabilities (one probability for each element of the vocabulary)
            preds = self._model.predict(pad_encoded, verbose=0)[0]

            if probabilistic:

                # Pick one chord randomly, according to the probabilities
                yhat = np.random.choice(range(len(self.vocabulary)),
                                        p=preds)

            else:

                # Just get the most probable
                yhat = preds.argmax()

            # reverse map integer to character
            out_char = self._inverse_mapping[yhat]

            # append to input so that in the next iteration the memory of the previous chords
            # will be passed to the network
            chord_sequence.append(out_char)

        # Generate sequence with generated chords and input sequence (i.e., the "song")
        complete_sequence_str = " ".join(chord_sequence)

        if play:

            # We generate a player for this sequence
            p = ChordSequencePlayer()
            audio = p.play(complete_sequence_str)

        else:

            audio = None

        # Return the output sequence, which has been appended into in_sequence after the input,
        # and join the result in a space-separated string

        return complete_sequence_str, audio

