import os
import socket
import sys
from time import sleep
from requests import get, post

current_ddns_ip = None

g_username = os.environ['USERNAME']
g_password = os.environ['PASSWORD']
g_domain = os.environ['DOMAIN']

UPDATE_INTERVAL = 900 # 15 mins

while True:
    DDNS_UPDATE_REQUIRED = False

    print("querying current DDNS IP")

    try:
        sock_host = socket.gethostbyaddr(g_domain)

        print("current DNS information")
        print("hostnames: {0}".format(sock_host[0]))
        print("aliaslist: {0}".format(sock_host[1]))
        print("iplist: {0}".format(sock_host[2]))

        if len(sock_host[2]) == 1:
            current_ddns_ip = sock_host[2][0]
        else:
            print("too may ips for: {0}".format(g_domain))
            print("terminating...")
            sys.exit(1)
    except socket.gaierror as ex:
        print("Exception occured")
        print(ex.strerror)    
    
    print("queryng current public IP")

    gapi_response = get('https://domains.google.com/checkip')

    print("api response: {0}:{1}".format(gapi_response.status_code, gapi_response.reason))
    if gapi_response.status_code == 200:
        if current_ddns_ip != gapi_response.text:
            print("new public ip address detected")
            current_ddns_ip = gapi_response.text
            DDNS_UPDATE_REQUIRED = True
            print('updated public IP address as: {0}'.format(current_ddns_ip))
        else:
            DDNS_UPDATE_REQUIRED = False
            print("DDNS up-to-date. no DDNS update required")
    
    if DDNS_UPDATE_REQUIRED:
        print("updating google DDNS records: {0}:{1}".format(g_domain, current_ddns_ip))
        gapi_response = post("https://{username}:{password}@domains.google.com/nic/update?hostname={domain}&myip={ip}".format(username=g_username, password=g_password, domain=g_domain, ip=current_ddns_ip))
        print("api response: {0}:{1}".format(gapi_response.status_code, gapi_response.reason))
        if gapi_response.status_code == 200:
            print("google DDNS records updated: {0}".format(gapi_response.text))
    
    sleep(UPDATE_INTERVAL)