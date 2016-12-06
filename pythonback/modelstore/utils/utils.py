import getpass
import pickle
import tarfile
import base64
import os
import sys


class Utils(object):

    @staticmethod
    def get_token():
        blueid_token = getpass.getpass('ibm.ax.token')
        token = "Bearer " + blueid_token
        return token

    @staticmethod
    def create_pickle(model, model_name):

        with open(model_name, 'wb') as handle:
            pickle.dump(model, handle, protocol=2)

        return model_name

    @staticmethod
    def compress(model_name):

        out = tarfile.open(model_name + '.tar.gz', mode='w:gz')
        try:
            out.add(model_name)
        finally:
            out.close()

        return

    @staticmethod
    def write_tar(filename, contents):
        filename += ".tar.gz"
        with open(filename, 'wb') as handle:
            handle.write(contents)
        return filename

    @staticmethod
    def read_file_as_binary(model_name):

        with open(model_name + '.tar.gz', 'rb') as handle:
            content = handle.read()

        return content

    @staticmethod
    def serialize(content):
        ENCODING = 'utf-8'
        serialized = base64.b64encode(content)
        base64_string = serialized.decode(ENCODING)
        return base64_string

    @staticmethod
    def deserialize(content):
        deserialized = base64.b64decode(content)
        return deserialized

    @staticmethod
    def extract_tar(tar_file):

        tar = tarfile.open(tar_file, "r|gz")
        try:
            tar.extractall()
        finally:
            tar.close()

    @staticmethod
    def unpickle(model_name):
        with open(model_name, 'rb') as handle:
            if sys.version_info.major >= 3:
                model = pickle.load(handle, encoding='latin-1')
            else:
                model = pickle.load(handle)
        return model

    @staticmethod
    def remove_files(file_name):
        os.remove(file_name)



