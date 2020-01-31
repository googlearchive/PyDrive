from setuptools import setup

setup(
    name='PyDrive2',
    version='1.4.2',
    author='JunYoung Gwak',
    author_email='jgwak@dreamylab.com',
    maintainer='DVC team',
    maintainer_email='support@dvc.org',
    packages=['pydrive2', 'pydrive2.test'],
    url='https://github.com/iterative/PyDrive2',
    license='Apache License 2.0',
    description='Google Drive API made easy. Maintained fork of PyDrive.',
    long_description=open('README.rst').read(),
    install_requires=[
        "google-api-python-client >= 1.2",
        "oauth2client >= 4.0.0",
        "PyYAML >= 3.0",
        "httplib2 <= 0.15.0",
        "pyOpenSSL >= 19.1.0"
    ],
    extras_require={
        "tests": ["timeout-decorator"],
    },
)
