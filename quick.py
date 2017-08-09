#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

get_response = requests.get(url="http://www.google.it")
print(get_response.text)
