from setuptools import setup

setup(name='ibm-modelstore',
      version='0.1',
      description='Modelstore library',
      url='https://github.ibm.com/NGP-TWC/platform-pipeline/',
      author='IBM',
      author_email='ibm@ibm.com',
      license='IBM',
      packages=['modelstore', 'modelstore.utils', 'modelstore.conf'],
      zip_safe=False)
