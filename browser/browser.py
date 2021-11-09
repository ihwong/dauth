#!/usr/bin/env python3

import requests

cert = ("browser-cert.pem", "browser-key.pem")
user_code = input("Enter user_code: ")
r = requests.get(
    'https://127.0.0.1:4443/device?user_code=' + user_code,
    cert = cert
)