# -*- coding: utf-8 -*-

""" Cisco DNA Center """

import requests
import sys
import json
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()


class DNAC(object):
    def __init__(self, config):
        self.config_protocol = config['protocol']
        self.config_host = config['host']
        self.config_port = config['port']
        self.config_username = config['username']
        self.config_password = config['password']
        self.config_proxy = config['proxy']

    def get_auth_token(self):
        login_url = "{}://{}:{}/dna/system/api/v1/auth/token".format(self.config_protocol, self.config_host,
                                                                     self.config_port)
        # Cisco DNA Center设备上有自签名证书，不是由CA颁发的，所以参数verify置False
        result = requests.post(url=login_url, auth=HTTPBasicAuth(self.config_username, self.config_password),
                               verify=False)
        # 如果请求有任何问题，并且有任何响应代码不同于200 OK，则raise_for_status()将退出脚本并显示一条Traceback消息，指示请求的问题
        result.raise_for_status()

        # token只有10分钟有效期
        return result.json()["Token"]

    def get_url(self, path):
        url = "{}://{}:{}/dna/intent/api/v1/{}".format(self.config_protocol, self.config_host, self.config_port, path)
        token = self.get_auth_token()
        headers = {
            'X-auth-token': token
        }
        try:
            response = requests.get(url, headers=headers, verify=False)
        except requests.exceptions.RequestException as cerror:
            print("Error processing request", cerror)
            sys.exit(1)

        return response.json()

    # 请求接收事件的代理地址
    def execution_status_url(self, url):
        token = self.get_auth_token() # 这里的tocken到底是dnac的还是代理的？？？
        headers = {
            'X-auth-token': token
        }
        try:
            response = requests.get(url, headers=headers, verify=False)
        except requests.exceptions.RequestException as cerror:
            print("Error processing request", cerror)
            sys.exit(1)

        return response.json()

    # 代理，用来接收事件，比如调用某些接口（比如 get_url('network-health')）会返回一个网址，由该网址接收事件的详细，需要自行请求该网址来获取信息
    # 设置代理，https://developer.cisco.com/docs/dna-center/#!getting-started-with-webhooks-on-the-cisco-dna-center-platform/configure-cisco-dna-center-proxy-settings
    def setup_proxy(self):
        token = self.get_auth_token()
        proxy_settings = self.config_proxy['proxy_settings']
        try:
            proxy_object = {
                "enableProxy": "true",
                "httpProxyHost": proxy_settings['httpProxyHost'],
                "httpsProxyHost": proxy_settings['httpsProxyHost'],
                "httpProxyPort": proxy_settings['httpProxyPort'],
                "httpsProxyPort": proxy_settings['httpsProxyPort'],
                "httpNonProxyHosts": "*.svc.cluster.local|{}".format(proxy_settings['httpNonProxyHosts'])
            }

            header_object = {
                "X-Auth-Token": token,
                "Content-type": "application/json",
            }

            response = requests.post(
                "{}://{}/api/dnacaap/v1/dnacaap/management/proxysettings".format(self.config_protocol, self.config_host),
                data=json.dumps(proxy_object),
                headers=header_object,
                verify=False,
            )
            print('Response HTTP Status Code: {status_code}'.format(status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(content=response.content))
        except requests.exceptions.RequestException:
            print('HTTP Request failed')
