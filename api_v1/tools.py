import base64
from hashlib import sha256 as hash_algo
from base64 import urlsafe_b64encode
import requests

ENCRYPT_FS = 'http://10.104.4.50:12029'
URL = ENCRYPT_FS + '/'
formatter = '%(asctime)s %(levelname)4s [%(filename)8s:%(lineno)04d]: %(message)s'


def gen_file_id(bytes):
    val = hash_algo()
    val.update(bytes)
    # print(val.digest())
    return urlsafe_b64encode(val.digest()[:16])


def send_to_aliCloud(content, src_id):
    print('try to update')
    print('   src_id = ', src_id)
    resp = requests.head('{}/{}'.format(ENCRYPT_FS, src_id))
    if resp.status_code / 100 == 2:
        print('pic already in server')
        return src_id
    resp = requests.put('{}/{}'.format(ENCRYPT_FS, src_id), data=content)


def upload_file(b64str):
    index = b64str.find(',')
    if index >= 0:
        b64 = b64str[index:]
        content = base64.b64decode(b64)
        src_id = gen_file_id(content).decode('utf-8')
        send_to_aliCloud(content, src_id)
        return '{}/{}'.format(ENCRYPT_FS, src_id)
