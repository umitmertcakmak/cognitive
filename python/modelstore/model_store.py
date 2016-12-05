# coding: utf-8

from .api_client import ApiClient
from .utils.utils import Utils
from .modelstore.conf import config
import logging
import os
import requests
import json

import getpass
import pickle
import tarfile
import base64
import sys


logger = logging.getLogger(__name__)

class ModelStore(object):
    """
    This class is for saving and loading scikit-learn models to and from git respectively
    """
    def __init__(self, host=None):

        env = os.environ.get('APP_ENV_ENVIRONMENT')
        domain = os.environ.get('APP_ENV_BM_DOMAIN')

        # Associating host based on environment

        if host is None:
            if env == "prod" and domain == 'ng.bluemix.net':
                self._host = config.git["host_prod"]
            elif env == "prod" and domain == 'stage1.ng.bluemix.net':
                self._host = self._host = config.git["host_fvt"]
            elif env == "dev" and domain == 'stage1.ng.bluemix.net':
                self._host = config.git["host_fvt"]
            else:
                self._host = config.git["host_fvt"]

        self._save_end_point = config.git["save"]
        self._load_end_point = config.git["load"]
        logger.info("target git host is %s, save end point is %s and load end point %s " % (self._host,
                                                                                            self._save_end_point,
                                                                                            self._load_end_point))

    def save(self, model, path, model_name):
        """Saves the model to git.
           :param model: scikit-learn model
           :param path: to git location, ex: default/bhmallel/models
            model_name: name of the model to be saved, ex: titanic_model
        Returns:
            Success message
        """
        if model is not None and path is not None and model_name is not None:

            response = self._save(model, path, model_name)

            if response.status_code == 200:
                Utils.remove_files(model_name)
                Utils.remove_files(model_name + ".tar.gz")
                return response.text
            else:
                return response.raise_for_status()
        else:
            raise ValueError('model or git path parameters cannot be None')

    def load(self, path, model_name):
        """Loads the model from git.
           :param path: path to git location, ex: default/bhmallel/models
           :param model_name: name of the model to be saved, ex: titanic_model
        Returns:
            model
        """
        if path is not None:

            response = self._load(path, model_name)

            if response.status_code == 200:
                decoded_data = self._get_model(response, model_name)
                Utils.remove_files(model_name)
                Utils.remove_files(model_name + ".tar.gz")
                return decoded_data
            else:
                return response.raise_for_status()
        else:
            raise ValueError('git path param cannot be None')

    def _save(self, model, path, model_name):

        try:
            token = Utils.get_token()
            logger.info("save: generated blue_id token %s " % token)

            Utils.create_pickle(model, model_name)
            logger.info("save: serialized model using pickle with name %s" % model_name)

            Utils.compress(model_name)
            logger.info("save: compressed %s model into tar and gz" % model_name)

            contents = Utils.read_file_as_binary(model_name)
            logger.info("save: read contents of tar.gz of %s model" % model_name)

            serialized = Utils.serialize(contents)
            logger.info("save: serialized contents of tar.bz to base64encode")

            repo_name = self._get_repo_name(path)
            git_path = self._get_git_path(path)
            logger.info("save: git repo name is %s and git path is %s" % (repo_name, git_path))

            save_object = dict()
            save_object["repoName"] = repo_name
            save_object["fileContent"] = serialized
            save_object["branchName"] = "master"
            save_object["gitPath"] = git_path + "/" + model_name
            save_object["userCommitMessage"] = "save pickle model"
            logger.info("save: created input json for saving artifact to git")

            url = self._host + self._save_end_point
            logger.info("save: git end point for saving artifact from git")

            headers = {'content-type': 'application/json', 'authorization': token}
            response = ApiClient().request(method='POST', url=url, body=save_object, headers=headers)
        except Exception as e:
            raise Exception(e.message)
        return response

    def _load(self, path, model_name):

        try:
            token = Utils.get_token()
            logger.info("load: generated blue_id token %s " % token)

            repo_name = self._get_repo_name(path)
            git_path = self._get_git_path(path)
            logger.info("load: git repo name is %s and git path is %s" % (repo_name, git_path))

            load_object = dict()
            load_object["repoName"] = repo_name
            load_object["branchName"] = "master"
            load_object["gitPath"] = git_path + "/" + model_name
            load_object["revisionSpec"] = "HEAD"

            url = self._host + self._load_end_point
            logger.info("load: git end point for loading artifact from git")

            headers = {'content-type': 'application/json', 'authorization': token}
            response = ApiClient().request(method='POST', url=url, body=load_object, headers=headers)

        except Exception as e:
            raise Exception(e.message)
        return response

    def _get_model(self, response, model_name):
        try:
            contents = Utils.deserialize(response.text)
            tar_file = Utils.write_tar(model_name, contents)
            Utils.extract_tar(tar_file)
            decoded_data = Utils.unpickle(model_name)
        except IOError as e:
            raise("file operations failed %s" % e.message)
        except Exception as e:
            raise Exception(e.message)
        return decoded_data

    def _get_repo_name(self, path):
        if path is not None:
            return path.split("/")[0]
        else:
            return None

    def _get_git_path(self, path):
        if path is not None:
            sep = "/"
            return sep.join(path.split("/")[1:])
        else:
            return None


def saveToGit():

    modelStore = ModelStore()

    print("Host ", modelStore._host)


    # repoId 4090cbfd-b21a-42d5-a89e-73d94eb910c8

    model = Utils.unpickle("iris_model.pkl")
    model_name = "iris_model.pkl"

    print("Scikit-learn model ", type(model))

    path = "4090cbfd-b21a-42d5-a89e-73d94eb910c8"

    token = "Bearer " + "bLo40HpLL6R4F9YGldfV6178hOItjmiI1l1fkbhP"


    print("save: generated blue_id token %s " % token)

    Utils.create_pickle(model, model_name)
    print("save: serialized model using pickle with name %s" % model_name)

    Utils.compress(model_name)
    print("save: compressed %s model into tar and gz" % model_name)

    contents = Utils.read_file_as_binary(model_name)
    print("save: read contents of tar.gz of %s model" % model_name)

    print("Contents: ", type(contents), contents)

    serialized = Utils.serialize(contents)
    print("save: serialized contents of tar.bz to base64encode")

    print("Serialized: ", type(serialized), serialized)

    repo_name = modelStore._get_repo_name(path)
    git_path = modelStore._get_git_path(path)
    print("save: git repo name is %s and git path is %s" % (repo_name, git_path))



    save_object = dict()
    save_object["repoName"] = repo_name
    save_object["fileContent"] = serialized
    save_object["branchName"] = "master"
    save_object["gitPath"] = path + "/" + model_name
    save_object["userCommitMessage"] = "save pickle model"
    save_object["inputSchema"] = "schema"
    save_object["size"] = 1234
    save_object["runtime"] = "python"
    save_object["project"] = "schema"
    save_object["stages"] = 1
    save_object["artifactType"] = "model"
    print("save: created input json for saving artifact to git")

    url = modelStore._host + modelStore._save_end_point
    print("save: git end point for saving artifact from git")

    headers = {'content-type': 'application/json', 'authorization': token}
    response = ApiClient().request(method = 'POST', url = url, body = save_object, headers = headers)
    print(url)
    print(response.text, response.status_code, response.ok, response.url)

def loadFromGit():

    modelStore = ModelStore()
    model_name = "iris_model.pkl"

    url = modelStore._host + modelStore._load_end_point + "/918"
    print("load: git end point for loading artifact from git")

    token = "Bearer " + "OPhRNu5l9en7XZgCMopX3ymbC5jjFVm68IDr8G1v"
    headers = {'content-type': 'application/json', 'authorization': token}

    #headers = {'content-type': 'application/json','Batch-Secret': "59cbb87389b7997775ff",'UserId': 'ngpuser'}
    response = ApiClient().request(method = 'GET', url = url, headers = headers)
    #print(url)
    #print("Response text: ", type(response.text), response.text)
    #print("Others: ", response.status_code, " - ", response.ok, " - ", response.url)
    #print("Type of Contents and Tar_file: ", type(contents), " - ", type(tar_file))
    #print("Type of Decoded_data: ", type(decoded_data), decoded_data)
    return response



def loadFromGitPath():
    modelStore = ModelStore()
    model_name = "iris_model.pkl"

    token = "Bearer " + "bLo40HpLL6R4F9YGldfV6178hOItjmiI1l1fkbhP"

    url = modelStore._host + modelStore._load_end_point + "?gitPath=4090cbfd-b21a-42d5-a89e-73d94eb910c8/iris_model.pkl"
    print("load: git end point for loading artifact from git")

    headers = {'content-type': 'application/json', 'authorization': token}
    response = ApiClient().request(method = 'GET', url = url, headers = headers)

    print(url)
    print(response.text, response.status_code, response.ok, response.url)

    return response

def unpackModelFromResponse(response, model_name):

    contents = Utils.deserialize(response.text)
    tar_file = Utils.write_tar(model_name, contents)
    Utils.extract_tar(tar_file)
    decoded_data = Utils.unpickle(model_name)

    # print(type(decoded_data), decoded_data)

    return decoded_data



#if __name__ == "__main__":
#    loadFromGit()




