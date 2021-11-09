from flask import Flask, request, jsonify
from secrets import token_hex, choice
from time import time
from datetime import datetime
import hashlib

import requests
import json

# static data of registered 16-byte client_id
registered_cid = [
    'd31044d4e46c0825fcbd6bc7f14325da',
    'ab6288de26e1f7f2e4aab4e4562ff72b',
    '8827fead674febc86c67c63fc9a2a537'
]

# dynamic data of client_id and device_code
# data structure:
# device_code
# user_code
# verification_uri
# expires_in
# interval
# verified
dvc_list = []

# data structure: token string, valid until
token_list = []

# utoken: token for untrusted devices
uclient_list = ['d31044d4e46c0825fcbd6bc7f14325da']
utoken_list = []

malicious_file = ['83eb262ea41e7158817d6f87b7cd3764']

# Real Google Photos token
tk = "ya29.a0ARrdaM88xvhxWhfc8n_s3GAt574KcNpy03gdO7h3udEOM61V0L4af60wSM4EXyLv6JCceKpOo7SzJrKIl1aKNMOH-L6ALJKzRobcMJUn5rzGAtsp5sJCmNbrUQgc4Eu9KtYb21zgpJ43hFUgWQUpQA0h68Patg"

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world!"

@app.route('/device_authorization', methods = ['POST'])
def device_authorization():
    # Parse request
    cid = request.form.get('client_id')
    scope = request.form.get('scope')
    # Check client_id
    if cid not in registered_cid:
        return jsonify({"error":"example_error_message"})
    # Generate response
    device_code = token_hex(16) ## Generate 16-byte random hexstring
    user_code = ''.join(choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(4)) + '-' + ''.join(choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(4)) ## Generate 10-digit random decimal
    verification_uri = 'https://127.0.0.1:4443/device'
    expires_in = time() + 300
    interval = 5
    verified = False
    data = {
        'client_id': cid,
        'device_code': device_code,
        'user_code': user_code,
        'verification_uri': verification_uri,
        'expires_in': expires_in,
        'interval': interval,
        'verified': verified
    }
    # Store response data
    dvc_list.append(data)

    response_data = {
        'device_code': device_code,
        'user_code': user_code,
        'verification_uri': verification_uri,
        'verification_uri_complete': verification_uri + '?user_code=' + user_code,
        'expires_in': 300,
        'interval': interval
    }
    # Return response data
    return jsonify(response_data)

@app.route('/device', methods = ['GET'])
def device():
    cuc = request.args.get('user_code')
    for e in dvc_list:
        if e['user_code'] == cuc and time() < e['expires_in'] and e['verified'] == False:
            e['verified'] = True
            return "ok"
    return "not ok"

@app.route('/token', methods = ['POST'])
def access_token():
    gtype = request.form.get('grant_type')
    cid = request.form.get('client_id')
    dvc = request.form.get('device_code')
    if not gtype == 'urn:ietf:params:oauth:grant-type:device_code':
        return 'gtype error'
    for e in dvc_list:
        if e['client_id'] == cid and e['device_code'] == dvc and time() < e['expires_in'] and e['verified'] == True:
            tok = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._~+/') for i in range(40)) # rfc6750
            token_list.append([tok, time() + 7200, 'partial-scope'])
            if cid in uclient_list:
                utoken_list.append(tok)
            return jsonify({
                'access_token': tok,
                'token_type': "Bearer",
                'expires_in': 7200,
                'scpoe': 'partial-scope'
            })
    return jsonify({"error":"example_error_message"})

# This API is for Out-Of-Scope Testing
@app.route('/api1', methods = ['POST'])
def api1():
    # phase 1/3: basic correctness check
    flag = False
    ctype = request.headers.get('Content-Type')
    token = request.headers.get('Authorization')[7:]
    for idx in token_list:
        if ctype == "application/x-www-form-urlencoded" and token == idx[0] and time() < idx[1] and idx[2] == 'partial-scope':
            flag = True
            break
    if flag == False:
        return "not ok"
    else:
        # phase 2/3: policy check
        if token in utoken_list:
            return "not ok (accessing this API from untrusted device is not allowed)"
        # phase 3/3: Real API starts here
        resp = requests.get(
            "https://photoslibrary.googleapis.com/v1/mediaItems",
            headers = {
                "Authorization": "Bearer " + tk
            }
        )
        return resp.json()

# This API is for Out-Of-Allowed-Time Testing
@app.route('/api2', methods = ['POST'])
def api2():
    # phase 1/3: basic correctness check
    flag = False
    ctype = request.headers.get('Content-Type')
    token = request.headers.get('Authorization')[7:]
    for idx in token_list:
        if ctype == "application/x-www-form-urlencoded" and token == idx[0] and time() < idx[1] and idx[2] == 'partial-scope':
            flag = True
            break
    if flag == False:
        return "not ok"
    else:
        # phase 2/3: policy check
        curr_h = int(datetime.now().strftime("%H"))
        if curr_h < 9 or curr_h >= 17:
            return "not ok (only allowed within office hours)"
        # phase 3/3: Real API starts here
        resp = requests.post(
            "https://photoslibrary.googleapis.com/v1/albums",
            headers = {
                "Authorization": "Bearer " + tk
            },
            json = {
                "album":{
                    'title':'testalbum1102'
                }
            }
        )
        return resp.json()

# This API is for Out-Of-Allowed-Parameter Testing
@app.route('/api3', methods = ['POST'])
def api3():
    # phase 1/3: basic correctness check
    flag = False
    ctype = request.headers.get('Content-Type')
    token = request.headers.get('Authorization')[7:]
    for idx in token_list:
        if ctype == "application/x-www-form-urlencoded" and token == idx[0] and time() < idx[1] and idx[2] == 'partial-scope':
            flag = True
            break
    if flag == False:
        return "not ok"
    else:
        # phase 2/3: policy check
        if hashlib.md5(request.get_data()).hexdigest() in malicious_file:
            return "not ok (suspicious file detected)"
        # phase 3/3: Real API starts here
        resp = requests.post(
            "https://photoslibrary.googleapis.com/v1/uploads",
            headers = {
                "Content-type": "application/octet-stream",
                "X-Goog-Upload-Protocol": "raw",
                "Authorization": "Bearer " + tk,
                "X-Goog-Upload-Content-Type": "image/png"
            },
            data = request.get_data()
        )

        utk = resp.text

        resp = requests.post(
            "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
            headers = {
                "Content-type": "application/octet-stream",
                "Authorization": "Bearer " + tk
            },
            json = {
                "albumId": "AI3d0xwnNxU3to2s2CNO6wgKK9vzMqGLNt_O06U4aZCZZ6iez1_Dc2Gp8lN3keenC99PYBPfXs21",
                "newMediaItems": {
                    "description": "asdasdasd",
                    "simpleMediaItem": {
                        "fileName": "asdasdasdasd",
                        "uploadToken": utk
                    }
                }
            }
        )

        parsed = json.dumps(resp.json(), indent = 4)
        return resp.json()

# This API is for Out-Of-Allowed-Response Testing
@app.route('/api4', methods = ['POST'])
def api4():
    # phase 1/3: basic correctness check
    flag = False
    ctype = request.headers.get('Content-Type')
    token = request.headers.get('Authorization')[7:]
    for idx in token_list:
        if ctype == "application/x-www-form-urlencoded" and token == idx[0] and time() < idx[1] and idx[2] == 'partial-scope':
            flag = True
            break
    if flag == False:
        return "not ok"
    else:
        # phase 2/3: policy check
        if token in utoken_list:
            data_filter = True
        else:
            data_filter = False
        # phase 3/3: Real API starts here
        resp = requests.get(
            "https://photoslibrary.googleapis.com/v1/albums",
            headers = {
                "Authorization": "Bearer " + tk
            }
        )
        if data_filter:
            arr = []
            for obj in resp.json()["albums"]:
                if "isWriteable" in obj and obj["isWriteable"]:
                    elem = {"id": obj["id"], "title": obj["title"]}
                    arr.append(elem)
            ret = {"albums": arr}
            return json.dumps(ret)
        else:
            return resp.json()

if __name__ == "__main__":
    app.run(ssl_context=('mycert.pem', 'mykey.pem'), port=4443)