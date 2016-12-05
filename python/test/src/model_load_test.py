import unittest
from mock import patch
import os.path

from library.python.modelstore.api_client import ApiClient
from library.python.modelstore.model_store import loadFromGit

def _mock_model_load(self, method=None, url=None, query_params=None, headers=None, body=None, post_params=None):
    """
    This method imitates model loading from git repo.

    :param method: GET or POST
    :param url: HOST/ENDPOINT/ARTIFACT_ID
    :param headers: Includes 'content-type', 'Batch-Secret', 'UserId'
    :return: Returns <class 'str'> object which contains model information loaded from git repo.

    """
    resource_file = '../resources/response_text.txt'
    with open(resource_file, mode='r') as resouce:
        resource_text = resouce.readline()
    rTuple = (resource_text, "200")
    return rTuple


class ClientTestCase(unittest.TestCase):
    """Test case for client methods."""

    def setUp(self):
        self.patcher = patch('library.python.modelstore.api_client.ApiClient.request', _mock_model_load)
        self.patcher.start()
        self.client = ApiClient()

    def tearDown(self):
        self.patcher.stop()

    def test_model_load(self):
        """ Testing model load"""
        responseT = loadFromGit()
        self.assertIsInstance(responseT[0], str)
        self.assertEqual(responseT[1], "200")
        # verify what's inside


if __name__ == "__main__":
    unittest.main()