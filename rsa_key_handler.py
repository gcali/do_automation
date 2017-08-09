#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from os import path

_DEFAULT_PATH = path.join(str(Path.home()), ".ssh/id_rsa.pub")

def get_rsa_key(path=None):
    if path is None:
        path = _DEFAULT_PATH
    with open(path, "r") as f:
        return f.read().strip()

def main():
    print(get_rsa_key())

if __name__ == "__main__":
    main()
