import random
import re
import os

from funcy import retry
from funcy.py3 import cat
from pydrive2.files import ApiRequestError
from shutil import copyfile

newline_pattern = re.compile(r"[\r\n]")

GDRIVE_USER_CREDENTIALS_DATA = "GDRIVE_USER_CREDENTIALS_DATA"
DEFAULT_USER_CREDENTIALS_FILE = "credentials/default.dat"

SETTINGS_PATH = "pydrive2/test/settings/"
LOCAL_PATH = "pydrive2/test/settings/local/"


def setup_credentials(credentials_path=DEFAULT_USER_CREDENTIALS_FILE):
    if os.getenv(GDRIVE_USER_CREDENTIALS_DATA):
        if not os.path.exists(os.path.dirname(credentials_path)):
            os.makedirs(os.path.dirname(credentials_path), exist_ok=True)
        with open(credentials_path, "w") as credentials_file:
            credentials_file.write(os.getenv(GDRIVE_USER_CREDENTIALS_DATA))


def settings_file_path(settings_file):
    template_path = SETTINGS_PATH + settings_file
    local_path = LOCAL_PATH + settings_file
    assert os.path.exists(template_path)
    if not os.path.exists(LOCAL_PATH):
        os.makedirs(LOCAL_PATH, exist_ok=True)
    if not os.path.exists(local_path):
        copyfile(template_path, local_path)
    return local_path


class PyDriveRetriableError(Exception):
    pass


# 15 tries, start at 0.5s, multiply by golden ratio, cap at 20s
@retry(15, PyDriveRetriableError, timeout=lambda a: min(0.5 * 1.618 ** a, 20))
def pydrive_retry(call):
    try:
        result = call()
    except ApiRequestError as exception:
        retry_codes = ["403", "500", "502", "503", "504"]
        if any(
            "HttpError {}".format(code) in str(exception)
            for code in retry_codes
        ):
            raise PyDriveRetriableError("Google API request failed")
        raise
    return result


def pydrive_list_item(drive, query, max_results=1000):
    param = {"q": query, "maxResults": max_results}

    file_list = drive.ListFile(param)

    # Isolate and decorate fetching of remote drive items in pages
    get_list = lambda: pydrive_retry(  # noqa: E731
        lambda: next(file_list, None)
    )

    # Fetch pages until None is received, lazily flatten the thing
    return cat(iter(get_list, None))


def CreateRandomFileName():
    hash = random.getrandbits(128)
    return "%032x" % hash


def StripNewlines(string):
    return newline_pattern.sub("", string)


def create_file(path, content):
    with open(path, "w") as f:
        f.write(content)


def delete_file(path):
    if os.path.exists(path):
        os.remove(path)
