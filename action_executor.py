#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urljoin
from typing import Callable
import requests
import key_reader

#urlparse.urljoin(*)

class ActionExecutor:

    def __init__(self,  get_executor=None, base_address:str="https://api.digitalocean.com/v2/", key=None):
        self._base_address = base_address
        self._get_executor = get_executor
        self._key = key
        if self._get_executor is None:
            self._get_executor = requests.get
        if self._key is None:
            self._key = key_reader.get_key()

    def list_actions(self):
        headers = { "Authorization": "Bearer {token}".format(token=self._key) }
        return self._get_executor(urljoin(self._base_address, "actions"), headers=headers )

def main():
    import json
    print(json.dumps(ActionExecutor().list_actions().json(), indent=4))

if __name__ == "__main__":
    main()
