import base64
import hmac
import json
import time
import uuid
from hashlib import sha256

import requests

key = 'yXMxPa2bFrGXj3fZJZdTpxLwpIE89kp9'.encode('utf-8')
url = 'https://partner.api.xdrnd.com'


def post(path, body):
    body = json.dumps(body)
    headers = get_headers('POST', path, body)
    ret = requests.post(url=url + path, data=body, headers=headers)
    return ret


def get(path):
    headers = get_headers('GET', path, '')
    ret = requests.get(url=url + path, headers=headers)
    return ret


def get_headers(method, path, body):
    timestamp = round(time.time())
    headers = {'X-Tap-App-Id': '201162', 'X-Tap-Client-Id': '5uk4xyrzhotypyeb7e', 'X-Tap-Nonce': str(uuid.uuid4())[0:8],
               'X-Tap-Ts': str(timestamp)}
    headers['X-Tap-Sign'] = get_sign(method, path, headers, body)
    headers['Content-Type'] = 'application/json'
    return headers


def get_sign(method, path, headers, body):
    data = method + '\n' + path + '\n'
    for header in headers:
        data = data + header + ':' + headers[header] + '\n'
    data = data + body + '\n'
    data = data.encode()
    sign = hmac.new(key, data, digestmod=sha256).digest()
    sign = base64.b64encode(sign).decode()
    return sign