import os
import time
from pathlib import Path

import requests

from .update_status import UpdateStatus


def download_file_if_newer(remote_url: str, local_filepath: str) -> UpdateStatus:
    if os.path.exists(local_filepath):
        local_mtime = os.path.getmtime(local_filepath)
    else:
        local_mtime = 0

    response = requests.head(remote_url, allow_redirects=True)
    print("Response status code:", response.status_code)
    if response.status_code == 200 and "Last-Modified" in response.headers:
        remote_last_modified = response.headers["Last-Modified"]
        remote_timestamp = time.mktime(
            time.strptime(remote_last_modified, "%a, %d %b %Y %H:%M:%S %Z")
        )
        if remote_timestamp > local_mtime:
            download_file(remote_url, local_filepath)
            return UpdateStatus.UPDATED
        else:
            return UpdateStatus.NOT_UPDATED
    return UpdateStatus.ERROR


def download_file(url, local_filepath):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        Path(local_filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(local_filepath, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
