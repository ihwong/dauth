from flask import Flask, request, jsonify
from secrets import token_hex, choice
from time import time
from time import perf_counter_ns
from datetime import datetime
import hashlib

import requests
import subprocess

enable_mdauth_policy = True

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
token_metadata = {}

# utoken: token for untrusted devices
uclient_list = ['d31044d4e46c0825fcbd6bc7f14325da']
utoken_list = []

# Real Google Photos token
tk = "ya29.a0ARrdaM8i_g_rZbFjCejcezrinAl1-l0qzjAcY5BodZtN83WjsD6Ci8x6RGn50niQmPkAruG8jBQim3rI1DJ4wbm9OArJOwJFL2HxTbgual9Lg59V-PRUVyyWWNlNjheTZTVBs-ztOOJJLFVfpaT2Zs2yBY-cfw"

# list of malicious hashes
mhashes = []

app = Flask(__name__)

@app.route('/')
def hello():
    for i in range(0, 395):
        filepath = "./hashfiles/VirusShare_%05d.md5" % i
        with open(filepath, 'r') as f:
            for line in f.readlines():
                if line[0] == '#':
                    continue
                else:
                    mhashes.append(line[:-1]) # remove '\n'

    print(mhashes[444])
    return jsonify({"message":"Hello, world!"})

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
            return jsonify({"message":"not ok"})
    return jsonify({"error":"not ok"})

@app.route('/token', methods = ['POST'])
def access_token():
    gtype = request.form.get('grant_type')
    cid = request.form.get('client_id')
    dvc = request.form.get('device_code')
    if not gtype == 'urn:ietf:params:oauth:grant-type:device_code':
        return jsonify({"error":'gtype error'})
    for e in dvc_list:
        if e['client_id'] == cid and e['device_code'] == dvc and time() < e['expires_in'] and e['verified'] == True:
            tok = ''.join(choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._~+/') for i in range(40)) # rfc6750
            token_list.append(tok)
            token_metadata[tok] = {"valid":time() + 7200, "scope":'partial-scope'}
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
    # phase 1/5: oauth correctness check
    rcvctype = request.headers.get('Content-Type')
    rcvtok = request.headers.get('Authorization')[7:]
    if rcvctype != "application/x-www-form-urlencoded" or rcvtok not in token_list:
        return jsonify({"error":"not ok"})
    elif token_metadata[rcvtok]["valid"] < time() or token_metadata[rcvtok]["scope"] != 'partial-scope':
        return jsonify({"error":"not ok"})
    # phase 2/5: mdauth pre policy check
    if enable_mdauth_policy:
        if rcvtok in utoken_list:
            return jsonify({"error":"not ok (accessing this API from untrusted device is not allowed)"})
    # phase 3/5: API logic
    resp = requests.get(
        "https://photoslibrary.googleapis.com/v1/mediaItems",
        headers = {
            "Authorization": "Bearer " + tk
        }
    )
    # phase 4/5: mdauth post policy check
    pass # nothing to do
    # phase 5/5: return
    return resp.json()

# This API is for Out-Of-Allowed-Time Testing
@app.route('/api2', methods = ['POST'])
def api2():
    # phase 1/5: oauth correctness check
    rcvctype = request.headers.get('Content-Type')
    rcvtok = request.headers.get('Authorization')[7:]
    if rcvctype != "application/x-www-form-urlencoded" or rcvtok not in token_list:
        return jsonify({"error":"not ok"})
    elif token_metadata[rcvtok]["valid"] < time() or token_metadata[rcvtok]["scope"] != 'partial-scope':
        return jsonify({"error":"not ok"})
    # phase 2/5: mdauth pre policy check
    if enable_mdauth_policy:
        curr_h = int(datetime.now().strftime("%H"))
        if curr_h < 9 or curr_h >= 17:
            return jsonify({"error":"not ok (only allowed within office hours)"})
    # phase 3/5: API logic
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
    # phase 4/5: mdauth post policy check
    pass # nothing to do
    # phase 5/5: return
    return resp.json()

# This API is for Out-Of-Allowed-Parameter Testing
@app.route('/api3', methods = ['POST'])
def api3():
    print("api3 called")
    # phase 1/5: oauth correctness check
    rcvctype = request.headers.get('Content-Type')
    rcvtok = request.headers.get('Authorization')[7:]
    rcvdata = request.get_data()
    if rcvctype != "application/x-www-form-urlencoded" or rcvtok not in token_list:
        return jsonify({"error":"not ok"})
    elif token_metadata[rcvtok]["valid"] < time() or token_metadata[rcvtok]["scope"] != 'partial-scope':
        return jsonify({"error":"not ok"})
    # phase 2/5: mdauth pre policy check
    if enable_mdauth_policy:
        if hashlib.md5(rcvdata).hexdigest() in mhashes:
            return jsonify({"error":"not ok (suspicious file detected)"})
        print("hash check ok")
        f = open('./temp_file.png', 'wb')
        f.write(rcvdata)
        f.close()
        print("file write ok")
        res = subprocess.check_output("clamdscan --multiscan --fdpass ./temp_file.png", shell = True)
        print(res.decode("utf-8"))
        print("check clamd ok")
    # phase 3/5: API logic
    resp = requests.post(
        "https://photoslibrary.googleapis.com/v1/uploads",
        headers = {
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-Protocol": "raw",
            "Authorization": "Bearer " + tk,
            "X-Goog-Upload-Content-Type": "image/png"
        },
        data = rcvdata
    )

    utk = resp.text

    resp = requests.post(
        "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate",
        headers = {
            "Content-type": "application/octet-stream",
            "Authorization": "Bearer " + tk
        },
        json = {
            "albumId": "AI3d0xy8Ji9z0CGT3y86XmUGxviSabEtWA7HATl-3ARJon5X-WZqXXfJW_fZrTYRZ-FGyGLH3b9F",
            "newMediaItems": {
                "description": "asdasdasd",
                "simpleMediaItem": {
                    "fileName": "asdasdasdasd",
                    "uploadToken": utk
                }
            }
        }
    )
    # phase 4/5: mdauth post policy check
    pass # nothing to do
    # phase 5/5: return
    return resp.json()

# This API is for Out-Of-Allowed-Response Testing
@app.route('/api4', methods = ['POST'])
def api4():
    # phase 1/5: oauth correctness check
    rcvctype = request.headers.get('Content-Type')
    rcvtok = request.headers.get('Authorization')[7:]
    if rcvctype != "application/x-www-form-urlencoded" or rcvtok not in token_list:
        return jsonify({"error":"not ok"})
    elif token_metadata[rcvtok]["valid"] < time() or token_metadata[rcvtok]["scope"] != 'partial-scope':
        return jsonify({"error":"not ok"})
    # phase 2/5: mdauth pre policy check
    pass # nothing to do
    # phase 3/5: API logic
    resp = requests.get(
        "https://photoslibrary.googleapis.com/v1/albums",
        headers = {
            "Authorization": "Bearer " + tk
        }
    )
    # phase 4/5: mdauth post policy check
    if enable_mdauth_policy:
        if rcvtok in utoken_list:
            arr = []
            for obj in resp.json()["albums"]:
                if "isWriteable" in obj and obj["isWriteable"]:
                    elem = {"id": obj["id"], "title": obj["title"]}
                    arr.append(elem)
            return jsonify({"albums": arr})
    # phase 5/5: return
    return resp.json()

if __name__ == "__main__":
    app.run(ssl_context=('mycert.pem', 'mykey.pem'), port=4443)