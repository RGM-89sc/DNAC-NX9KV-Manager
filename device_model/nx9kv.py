# -*- coding: utf-8 -*-

""" nx9kv """

import requests
import json
import urllib3

# Disable Self-Signed Cert warning for demo
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Nx9kv(object):
    def __init__(self, config):
        self.config_protocol = config['protocol']
        self.config_host = config['host']
        self.config_aaa_attributes = config['aaa_attributes']

    # Cisco Nexus 9000 Series NX-API CLI
    def cli(self, cli_type, command):
        url = '{}://{}/ins'.format(self.config_protocol, self.config_host)
        switchuser = self.config_aaa_attributes['name']
        switchpassword = self.config_aaa_attributes['pwd']

        myheaders = {'content-type': 'application/json'}
        payload = {
            "ins_api": {
                "version": "1.0",
                "type": cli_type,
                "chunk": "0",
                "sid": "1",
                "input": command,
                "output_format": "json"
            }
        }

        response = requests.post(url,
                                 data=json.dumps(payload),
                                 headers=myheaders,
                                 auth=(switchuser, switchpassword),
                                 verify=False).json()
        output = json.dumps(response, indent=2, sort_keys=True)
        return output

    # get NX-OS info
    def print_sys_info(self, no_filter=False):
        # Assign requests.Session instance to session variable
        session = requests.Session()

        # Define URL and PAYLOAD variables
        url = "{}://{}/api/aaaLogin.json".format(self.config_protocol, self.config_host)
        payload = {
            "aaaUser": {
                "attributes": self.config_aaa_attributes
            }
        }

        # Obtain an authentication cookie
        session.post(url, json=payload, verify=False)

        # Define SYS_URL variable
        sys_url = "{}://{}/api/mo/sys.json".format(self.config_protocol, self.config_host)

        # Obtain system information by making session.get call
        # then convert it to JSON format then filter to system attributes
        sys_info = session.get(sys_url, verify=False).json()["imdata"][0]["topSystem"]["attributes"]

        if no_filter:
            # Print raw data
            print(sys_info)
        else:
            # Print hostname, serial nmber, uptime and current state information
            # obtained from the NXOSv9k
            print("HOSTNAME:", sys_info["name"])
            print("SERIAL NUMBER:", sys_info["serial"])
            print("UPTIME:", sys_info["systemUpTime"])
