from setuptools import setup

import glob

# Add all ROI data files
data_files = glob.glob('data/best_artists_chords_anonymous.json')

setup(
    name='chords_ai',
    version='1.0',
    packages=['chords_ai',],
    author='giacomov',
    author_email='giacomov@stanford.edu',
    description='An Artificial Intelligence algorithm (a LSTM network) to generate sequences of chords',
    include_package_data=True,
    install_requires=[
            'numpy >= 1.6',
            'pyyaml',
            'pandas',
            'matplotlib',
            'keras',
            'scikit-learn',
            'ipython'
        ]
)
