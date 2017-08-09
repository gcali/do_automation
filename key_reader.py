#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


_DEFAULT_FILE_PATH = 'digitalocean.key'

def get_key(path=None):
    if path is None:
        path = _DEFAULT_FILE_PATH
    with open(path, "r") as f:
        json_data = json.loads(f.read())
        return json_data["key"]


def main():
    import sys

    args = sys.argv[1:]
    if args:
        print(get_key(args[0]))
    else:
        print(get_key())


if __name__ == "__main__":
    main()
