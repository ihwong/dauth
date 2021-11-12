#!/usr/bin/env python3

import requests

# User Configurations ###################################################
# Server's IP address and port number
addr = "https://127.0.0.1:4443"
#########################################################################

cert = ("browser-cert.pem", "browser-key.pem")
user_code = input("Enter user_code: ") # For example, ABCD-EFGH
resp = requests.get(
    addr + "/device?user_code=" + user_code,
    cert = cert
)