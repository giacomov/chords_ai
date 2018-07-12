import pkg_resources
import os


def get_path_of_data_file(data_file):

    file_path = pkg_resources.resource_filename("chords_ai", 'data/%s' % data_file)

    assert os.path.exists(file_path), "Data file %s does not exist" % file_path

    return file_path
