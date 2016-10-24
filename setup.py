from setuptools import setup

setup(
    name='PyDrive',
    version='1.3.1',
    author='JunYoung Gwak',
    author_email='jgwak@dreamylab.com',
    maintainer='Robin Nabel',
    maintainer_email='rnabel@ucdavis.edu',
    packages=['pydrive', 'pydrive.test'],
    url='https://github.com/googledrive/PyDrive',
    license='LICENSE',
    description='Google Drive API made easy.',
    long_description=open('README.rst').read(),
    install_requires=[
        "google-api-python-client >= 1.2",
        "oauth2client >= 4.0.0",
        "PyYAML >= 3.0",
    ],
)
