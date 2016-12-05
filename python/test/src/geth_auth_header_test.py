import unittest
import os

def get_authorization_header(header_dictionary):
   """
   :param header_dictionary: from header data extracts authorization header
   :return: authorization header
   """
   if ('Authorization' in header_dictionary):
       auth_header = header_dictionary['Authorization']
       if auth_header is None or len(str(auth_header)) == 0:
           return None
       else:
           return {'Authorization': auth_header}
   elif ('Batch-Secret' in header_dictionary):
       auth_user = header_dictionary['Userid']
       auth_token = header_dictionary['Batch-Secret']
       if auth_user is None or len(str(auth_user)) == 0 or auth_token is None or len(str(auth_token)) == 0:
           return None
       else:
           return {'Userid': auth_user, 'Batch-Secret': auth_token}

class BasicTest(unittest.TestCase):
    def test_headers(self):
        dict_a = {'Batch-Secret': 'cbb87389b7997775ff', 'Userid': 'ngpuser'}
        auth_header = get_authorization_header(dict_a)
        self.assertEqual(auth_header, dict_a)



if __name__ == '__main__':
    unittest.main()
