import sys
from setuptools import setup

# Extra dependecies to run tests
tests_requirements = [
    "pytest>=4.6.0",
    "timeout-decorator",
    "funcy>=1.14",
    "flake8",
    "flake8-docstrings",
]

if sys.version_info >= (3, 6):
    tests_requirements.append("black==19.10b0")

setup(
    name="PyDrive2",
    version="1.6.2",
    author="JunYoung Gwak",
    author_email="jgwak@dreamylab.com",
    maintainer="DVC team",
    maintainer_email="support@dvc.org",
    packages=["pydrive2", "pydrive2.test"],
    url="https://github.com/iterative/PyDrive2",
    license="Apache License 2.0",
    description="Google Drive API made easy. Maintained fork of PyDrive.",
    long_description=open("README.rst").read(),
    install_requires=[
        "google-api-python-client >= 1.12.1",
        "six >= 1.13.0",
        "oauth2client >= 4.0.0",
        "PyYAML >= 3.0",
        "pyOpenSSL >= 19.1.0",
    ],
    extras_require={"tests": tests_requirements},
)
