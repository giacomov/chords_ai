"""
Implement a generator of a waveform for a sequence of chords. The generator can also play it in a Jupyter notebook
"""

import numpy as np
from IPython.display import Audio, display

import fluidsynth
from audiolazy import lazy_midi
import yaml
from chords_ai.package_data import get_path_of_data_file


class ChordSequencePlayer(object):

    def __init__(self, rate=44100):

        # Read dictionary containing chord components
        with open(get_path_of_data_file("chords_components.yml")) as f:

            self._components = yaml.load(f)

        self._rate = rate

    def play(self, seq):
        """
        Play sequence of chords

        :param seq: a string containing a space-separated sequence of chords
        :return: None
        """

        seq = str(seq)

        audio = []

        for chord in seq.split(" "):
            audio = np.append(audio, self._make_chord(chord))

        display(Audio(audio, rate=self._rate, autoplay=False))

    def _make_chord(self, chord):
        """
        Make a waveform with the notes of the given chord

        :param chord: name of the chord
        :return: np.array containing the waveform
        """

        # Get notes making up the chord
        components = self._components[chord]

        # Get the equivalent MIDI integer number
        midi_notes = map(lambda x: lazy_midi.str2midi("%s4" % x), components)

        # Open synthetizer and load instrument (sound font)
        fl = fluidsynth.Synth(self._rate)
        sfid = fl.sfload("/home/giacomov/data_science/guitar_chords/pyfluidsynth/soundfonts/GrandPiano.sf2")
        fl.program_select(0, sfid, 0, 0)

        # Play each note of the chord
        for note in midi_notes[::-1]:
            fl.noteon(0, note, 60)

        # Record what the synth is playing into a numpy array
        s = np.array(fl.get_samples(self._rate))

        # Stop all notes and close synthetizer
        for note in midi_notes:
            fl.noteoff(0, note)

        fl.delete()

        # Return numpy array
        return s