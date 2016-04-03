#encoding:utf8

import requests

#b2fcd49fb6c643f7ca2bde149119ac73

def get_token(appid, appsecret):
    params = dict(
        grant_type="client_credential",
        appid=appid,
        secret=appsecret
    )
    resp = requests.get("https://api.weixin.qq.com/cgi-bin/token", params=params)
    if resp.status_code == requests.codes.ok:
        resp = resp.json()
        return resp["access_token"], resp["expires_in"]
    return None, None