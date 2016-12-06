from pyspark import SparkContext
from py4j.java_collections import MapConverter
import inspect

class Sink (object):

    """
    Class for creating a Sink object to sink data to an external DataSource like AmazonS3, Swift, DashDB etc.
    A Sink object can be the last stage of a :class:`pipeline.DAG.DAG`

    :param symbolicconst: Connection string to access the external DataSource.
    :param optionsmap: A dictionary specifying the options to be passed to the DataSource.
    """
    _sc = SparkContext._active_spark_context
    _logSrcLang = "Py:"

    def __init__(self, symbolicconst, optionsmap):

        self._jPipeline = self._sc._jvm.com.ibm.analytics.ngp.pipeline.pythonbinding.Pipelines
        self._jLogger = self._sc._jvm.org.apache.log4j.Logger
        self._to_map = self._jPipeline.toScalaMap
        self.logger = self._jLogger.getLogger(self.__class__.__name__)
        methodname = str(inspect.stack()[0][3])

        joptionsmap = MapConverter().convert(optionsmap, self._sc._gateway._gateway_client)
        sca_map = self._to_map(joptionsmap)
        logMsg = self._logSrcLang + self.__class__.__name__ + ":" + methodname + ": [Params: symbolicconst => " + str(
            symbolicconst) + " | optionsmap => " + str(optionsmap) + "]"
        self.logger.info(logMsg)
        self._jSink = self._jPipeline.getSink().apply(symbolicconst,sca_map)

    def run(self, dataframe):
        """
        Used to execute a :class:`Sink` object referring to an external DataSource, passing a dataframe.

        :param dataframe: A DataFrame
        :return: None
        """
        methodname = str(inspect.stack()[0][3])
        logMsg = self._logSrcLang + self.__class__.__name__ + ":" + methodname + ": [Params: dataframe => " + str(
            dataframe) + "]"
        self.logger.info(logMsg)

        self._jSink.run (dataframe._jdf)

    def _to_java(self):
        return self._jSink
        
        
#####################################################

import requests
import json


class ApiClient(object):

    def request(self, method, url, query_params=None, headers=None, body=None, post_params=None):

        """
            :param method: http request method
            :param url: http request url
            :param query_params: query parameters in the url
            :param headers: http request headers
            :param body: request json body, for `application/json`
            :param post_params: request post parameters,
                                `application/x-www-form-urlencode`
                                and `multipart/form-data`
            """

        method = method.upper()
        post_params = post_params or {}
        headers = headers or {}

        if post_params and body:
            raise ValueError(
                "body parameter cannot be used with post_params parameter."
            )

        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        try:
            if method == "POST":
                response = requests.post(url, data=json.dumps(body), headers=headers)
                return response

            if method == "GET":
                response = requests.get(url=url, params=query_params, headers=headers)
                return response

            if method == "PUT":
                response = requests.put(url=url, data=json.dumps(body), params=query_params, headers=headers)
                return response

            if method == "DELETE":
                response = requests.delete(url=url, params=query_params, headers=headers)
                return response

        except requests.exceptions.RequestException as e:
            msg = "{0}\n{1}".format(type(e).__name__, str(e))
            raise ApiException(status=0, reason=msg)


class ApiException(Exception):

    def __init__(self, status=None, reason=None, http_resp=None):
        if http_resp:
            self.status = http_resp.status
            self.reason = http_resp.reason
            self.body = http_resp.data
            self.headers = http_resp.getheaders()
        else:
            self.status = status
            self.reason = reason
            self.body = None
            self.headers = None

    def __str__(self):
        """
        Custom error messages for exception
        """
        error_message = "({0})\n"\
                        "Reason: {1}\n".format(self.status, self.reason)
        if self.headers:
            error_message += "HTTP response headers: {0}\n".format(self.headers)

        if self.body:
            error_message += "HTTP response body: {0}\n".format(self.body)

        return error_message


git = dict(
    host_fvt="https://ibm-watson-ml-dev.stage1.mybluemix.net",
    host_dev="http://nginx-prim-dev.spark.bluemix.net:12501",
    host_prod="http://nginx-prim-prod.spark.bluemix.net:12501",
    save="/v1/repos/artifacts",
    load="/v1/repos/artifacts",
    branch="master",
    message="saving model to git",
    revisionSpec="HEAD"
)



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






