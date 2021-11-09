#!/usr/bin/env python3

import requests
import time
import json

client_id = 'd31044d4e46c0825fcbd6bc7f14325da'
cert = ("device-cert.pem", "device-key.pem")
url = "https://127.0.0.1:4443"
access_token = ""

### Phase 1 Start ##############################################################

print("Requesting for user_code...")
data = {
    'client_id': client_id,
    'scpoe': "partial-scope"
}

# "application/x-www-form-urlencoded" content-type을 보장하기 위해서 data 타입으로 보내야 함
# https://me2nuk.com/Python-requests-module-example/ 
r = requests.post(
    url + '/device_authorization',
    data = data,
    cert = cert
) 

device_code = r.json()['device_code']
interval = r.json()['interval']
v_uri = r.json()['verification_uri']
v_uri_complete = r.json()['verification_uri_complete']
user_code = r.json()['user_code']

print("Requesting for user_code... Done")
print("Visit " + v_uri_complete)

### Phase 1 End ################################################################

### Phase 2 Start ##############################################################

while True:
    time.sleep(interval)
    r = requests.post(
        'https://127.0.0.1:4443/token',
        data = { # must use 'data = ' not 'json = '
            'grant_type':'urn:ietf:params:oauth:grant-type:device_code',
            'device_code':device_code,
            'client_id':client_id
        },
        cert=cert
    )
    print(r)
    print(r.content.decode('ascii'))
    resp = r.content.decode('ascii')
    json_data = json.loads(resp)
    try:
        print(json_data["error"])
    except KeyError:
        access_token = json_data["access_token"]
        break
### Phase 2 End ################################################################

### Phase 3 Start ##############################################################
print(access_token)

while True:
    choice = input("Enter API number to call (1-4): ")
    if choice == "1":
        print("Calling API 1...")
        resp = requests.post(
            url + '/api1',
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': "Bearer " + access_token
            },
            cert = cert
        )
        parsed = json.dumps(resp.json(), indent = 4)
        print(parsed)
    elif choice == "2":
        print("Calling API 2...")
        resp = requests.post(
            url + "/api2",
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': "Bearer " + access_token
            },
            cert = cert
        )
        parsed = json.dumps(resp.json(), indent = 4)
        print(parsed)
    elif choice == "3":
        print("Callig API 3...")
        ### Not Implemented Yet ##################
        with open('./image.png', 'rb') as f:
            param_data = f.read()
        resp = requests.post(
            url + "/api3",
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': "Bearer " + access_token
            },
            cert = cert,
            data = param_data
        )
        parsed = json.dumps(resp.json(), indent = 4)
        print(parsed)
        ##########################################
    elif choice == "4":
        print("Calling API 4...")
        resp = requests.post(
            url + "/api4",
            headers = {
                'Content-Type': "application/x-www-form-urlencoded",
                'Authorization': "Bearer " + access_token
            },
            cert = cert
        )
        parsed = json.dumps(resp.json(), indent = 4)
        print(parsed)
    else:
        print("choice error")
### Phase 3 End ################################################################