# -*- coding: utf-8 -*-
# filename : central_device_command.py
# pip install requests
import requests, getpass, json, optparse, os.path
from requests.packages.urllib3.exceptions import InsecureRequestWarning 
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#============================
#Setup VARIABLE
#============================
customerid = "INPUT_YOUR_CUSTOMERID"
clientid = "INPUT_YOUR_CLIENTID"
clientsecret = "INPUT_YOUR_CLIENTSECRET"
apiurl = "INPUT_YOUR_APIURL"
#============================

url_oauth = apiurl + "oauth2/authorize/central/api"
url_login = apiurl + "oauth2/authorize/central/api/login"
url_token = apiurl + "oauth2/token"
url_auth = apiurl + "oauth2/authorize/central/api"
url_unassign = apiurl + "licensing/v2/subscriptions/unassign"

username = ""
password = ""
csrf = ""
ses = ""
authcode = ""
accesstoken = ""
refreshtoken = ""
expires_in = ""

def login():
    global csrf,ses
    print("===> 1. Login Authentication")
    headers = {"Content-Type":"application/json"}
    params = {"client_id":clientid}
    data = {"username": username, "password": password}
    s = requests.Session()
    result = s.post(url_login, headers=headers, params=params, 
                    data=json.dumps(data), verify=False, timeout=10)
    if result.status_code == 200 :
        for c in result.cookies:
            if c.name == "csrftoken":
                csrf = c.value
            if c.name == "session":
                ses = c.value
    else :
        print("status code : " + str(result.status_code)) 
        print("text : " + str(result.text)) 
        exit(0)

    print("csrf: %s" % csrf)
    print("ses: %s" % ses)



def get_authcode():
    global authcode
    print("===> 2. Getting the authorization code")
    headers = {"Content-Type":"application/json",
                "X-CSRF-TOKEN":csrf, 
                "Cookie":"session="+ses}
    params = {"client_id":clientid,"response_type":"code","scope":"all"}
    data = {"customer_id" : customerid}
    s = requests.Session()
    result = s.post(url_oauth, headers=headers, params=params, 
                    data=json.dumps(data), verify=False, timeout=10)
    if result.status_code == 200 :
        tmp = json.loads(result.text)
        authcode = tmp['auth_code']
    else :
        print("status code : " + str(result.status_code)) 
        print("text : " + str(result.text)) 
        exit(0)
        
    print("authcode: %s" % authcode)



def get_accesstoken():
    global refreshtoken,accesstoken,expires_in
    print("===> 3. Auth Code to Access Token")
    headers = {}
    params = {"client_id":clientid,"client_secret":clientsecret,
                "grant_type":"authorization_code", "code":authcode}
    data = {}
    s = requests.Session()
    result = s.post(url_token, headers=headers, params=params, 
                    data=json.dumps(data), verify=False, timeout=10)
    if result.status_code == 200 :
        tmp = json.loads(result.text)
        refreshtoken = tmp['refresh_token']
        #token_type = tmp['token_type']
        accesstoken = tmp['access_token']
        expires_in = tmp['expires_in']
    else :
        print("status code : " + str(result.status_code)) 
        print("text : " + str(result.text)) 
        exit(0)

    print("refreshtoken: %s" % refreshtoken)
    print("accesstoken: %s" % accesstoken)
    print("expires_in: %s" % expires_in)



def device_action(serial,cmd):
    headers = {}
    params = {"access_token":accesstoken}
    data = {}
    s = requests.Session()
    url = apiurl+"device_management/v1/device/"+serial+"/action/"+cmd
    result = s.post(url, headers=headers, params=params, 
                    data=json.dumps(data), verify=False, timeout=10)

    if result.status_code == 200 :
        print(device_serial +" device action successfully") 
    else :
        print("status code : " + str(result.status_code)) 
        print("text : " + str(result.text)) 
        exit(0)
    

def main():
    global username,password
    parser = optparse.OptionParser("ex) python central_device_command.py -f device_list_file ")
    parser.add_option('-f', dest='device_list_file', type='string', help='device_list_file')
    (options, args) = parser.parse_args()
    device_list_file = options.device_list_file
    if device_list_file == None :
        print(parser.usage)
        exit(0)

    username = str(input("Username:"))
    password = getpass.getpass()

    login()
    get_authcode()
    get_accesstoken()

    f = open(device_list_file, 'r')
    device_list = f.readlines()
    f.close()

    for device in device_list :
        tmp=device.strip().split(',')
        print('serial : {0}, cmd : {1}'.format(tmp[0], tmp[1]))
        device_action(tmp[0],tmp[1])



if __name__ == '__main__':
    main()







