from setuptools import setup

setup(
    name='PyDrive',
    version='1.2.1',
    author='JunYoung Gwak',
    author_email='jgwak@dreamylab.com',
    packages=['pydrive', 'pydrive.test'],
    url='http://pypi.python.org/pypi/PyDrive/',
    license='LICENSE',
    description='Google Drive API made easy.',
    long_description=open('README.rst').read(),
    install_requires=[
        "google-api-python-client >= 1.2",
        "PyYAML >= 3.0",
    ],
)
