import requests
import json
import base64
import sys
import os
import socket
import time
import subprocess

# Cloudflare config
ZoneID          = os.environ.get('ZoneID')
AimDNSRecoreID  = os.environ.get('AimDNSRecoreID')
AimDNSName      = os.environ.get('AimDNSName')
CloudFlareToken = os.environ.get('CloudFlareToken')

# Vultr config
VultrToken      = os.environ.get('VultrToken')
DefaultRegion   = os.environ.get('DefaultRegion')
DefaultPlan     = os.environ.get('DefaultPlan')
StartUpScriptID = os.environ.get('StartUpScriptID')
UserData        = b""

# PingServer
PingServerPort  = int(os.environ.get('PingServerPort'))
PingServerToken = os.environ.get('PingServerToken')
PingAim         = os.environ.get('PingAim')

MaxCreateInstanceCount = 8
TimeSleepAfterCreateInstance = 210

# record instant id
ValidInstantList   = []
InvalidInstantList = []

def getTime():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def CheckOSEnvParam():
    print(f'ZoneID          {ZoneID}')
    print(f'AimDNSRecoreID  {AimDNSRecoreID}')
    print(f'AimDNSName      {AimDNSName}')
    print(f'CloudFlareToken {CloudFlareToken}')
    print(f'VultrToken      {VultrToken}')
    print(f'DefaultRegion   {DefaultRegion}')
    print(f'DefaultPlan     {DefaultPlan}')
    print(f'StartUpScriptID {StartUpScriptID}')
    print(f'PingServerPort  {PingServerPort}')
    print(f'PingServerToken {PingServerToken}')
    print(f'PingAim         {PingAim}')

def SelfPingCheck():
    try:
        pingResult = (subprocess.check_output(['ping', PingAim, '-c', '5'])).decode('utf-8')
    except:
        pingResult = "5 packets transmitted, 0 received, 100% packet loss, time 4000ms"
    print(f"selfPingRes {pingResult}")
    pingResult = pingResult[pingResult.find('transmitted') + 13:]
    pingResult = pingResult[:pingResult.find('received') - 1]
    return int(pingResult)

def GetPublicIP():
    response = requests.get('https://api.ipify.org?format=json')
    data = response.json()
    return data['ip']

def ListDNSRecords():
    print('Try get DNS records list...')
    headers = {
        "Authorization" : f"Bearer {CloudFlareToken}",
        "Content-Type" : "application/json"
    }
    url = f'https://api.cloudflare.com/client/v4/zones/{ZoneID}/dns_records'
    res = requests.get(url=url, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')
    return data

def GetAimDNSRecordDetail():
    print('Try get Aim DNS records Detail...')
    headers = {
        "Authorization" : f"Bearer {CloudFlareToken}",
        "Content-Type" : "application/json"
    }
    url = f'https://api.cloudflare.com/client/v4/zones/{ZoneID}/dns_records/{AimDNSRecoreID}'
    res = requests.get(url=url, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')
    return data

def UpdateAimDNSRecord(newContent):
    print(f'try update DNS Record to {newContent}')
    headers = {
        "Authorization" : f"Bearer {CloudFlareToken}",
        "Content-Type" : "application/json"
    }
    payload = {
        "content": f"{newContent}",
        "name": f'{AimDNSName}',
        "proxied": False,
        "type": "A",
        "comment": "AUTO_DEPLOYER",
        "tags": [],
        "ttl": 1
    }
    url = f'https://api.cloudflare.com/client/v4/zones/{ZoneID}/dns_records/{AimDNSRecoreID}'
    res = requests.put(url=url, json=payload, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')

def GetInstanceList():
    print('try get instance list...')
    headers = {
        "Authorization" : f"Bearer {VultrToken}",
        "Content-Type" : "application/json"
    }
    url = 'https://api.vultr.com/v2/instances'
    res = requests.get(url=url, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')
    return data

def GetInstantStatus(instanceID):
    print('try get instance...')
    headers = {
        "Authorization" : f"Bearer {VultrToken}",
        "Content-Type" : "application/json"
    }
    url = f'https://api.vultr.com/v2/instances/{instanceID}'
    res = requests.get(url=url, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')
    return data

def CreateInstance():
    print('Creating instance...')
    headers = {
        "Authorization" : f"Bearer {VultrToken}",
        "Content-Type" : "application/json"
    }
    payload = {
        "region": f"{DefaultRegion}",
        "plan": f"{DefaultPlan}",
        "label": "",
        "os_id": 167,
        "script_id" : f"{StartUpScriptID}",
        "user_data": base64.b64encode(UserData).decode('utf-8'),
        "backups": "disabled",
        "hostname": "vultr.guest",
        "tags": []
    }
    url = 'https://api.vultr.com/v2/instances'
    res = requests.post(url=url, json=payload, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')
    return data

def DestroyInstance(instanceID):
    print(f'try delete instance {instanceID}...')

    headers = {
        "Authorization" : f"Bearer {VultrToken}",
        "Content-Type" : "application/json"
    }
    url = f'https://api.vultr.com/v2/instances/{instanceID}'
    res = requests.delete(url=url, headers=headers)
    # data = json.loads(res.text)
    # print(f'{json.dumps(data, indent=4)}\n')

def ListStartUpScripts():
    headers = {
        "Authorization" : f"Bearer {VultrToken}",
        "Content-Type" : "application/json"
    }
    url = 'https://api.vultr.com/v2/startup-scripts'
    res = requests.get(url=url, headers=headers)
    data = json.loads(res.text)
    print(f'{json.dumps(data, indent=4)}\n')

def GetPingResult(AimIP):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((AimIP, PingServerPort))
    client.send(PingServerToken.encode('utf-8'))
    pingResult = client.recv(1024).decode('utf-8')
    print(pingResult)
    pingResult = pingResult[pingResult.find('transmitted') + 13:]
    pingResult = pingResult[:pingResult.find('received') - 1]
    return int(pingResult)

def RegularCheck():
    print(f"{getTime()} Start RegularCheck...")
    aimDNSRecordDatail = GetAimDNSRecordDetail()
    currentDNSRecordIP = aimDNSRecordDatail["result"]["content"]
    currentIP = GetPublicIP()
    print(f'Current DNS record ip is {currentDNSRecordIP}')
    pingResult = SelfPingCheck()
    print(f'Ping success count = {pingResult}')
    if pingResult > 0:
        if currentIP != currentDNSRecordIP:
            UpdateAimDNSRecord(currentIP)
            print("Current IP is valid, but DNS using other IP, so change it")
        else:
            print("Current IP is valid, exit.")
        return
    else:
        print("Current IP is banned possiably, creat new one")
        instantList = GetInstanceList()
        for instant in instantList["instances"]:
            instantIP = instant["main_ip"]
            if instantIP == currentIP:
                selfInstanceID = instant["id"]
        createCount    = 0
        respawnSuccess = False
        while createCount < MaxCreateInstanceCount:
            createCount += 1
            newInstance = CreateInstance()
            # Wait for instance deploying done
            time.sleep(TimeSleepAfterCreateInstance)
            newInstanceStats = GetInstantStatus(newInstance["instance"]["id"])
            newInstanceIP = newInstanceStats["instance"]["main_ip"]
            print(f'Testing New Created Instance {newInstanceIP}...')
            pingResult = int(GetPingResult(newInstanceIP))
            print(f'Ping success count = {pingResult}')
            if pingResult > 0:
                print(f'Change aim DNS record to {newInstanceIP}, tried count {createCount}')
                UpdateAimDNSRecord(newInstanceIP)
                respawnSuccess = True
                break
            else:
                # We should keep this invalid instance alive by now, in case of getting this banned ip again & again...
                InvalidInstantList.append(newInstance["instance"]["id"])
                continue
        print("Destroy invalid instances...")
        for instance in InvalidInstantList:
            DestroyInstance(instance)
        if True == respawnSuccess:
            print(f"{getTime()} RegularCheck End! Self Destroying, good bye...")
            DestroyInstance(selfInstanceID)
        else:
            print(f"{getTime()} Created max instance count but failed, maybe next time...")

# debugZone

# CheckOSEnvParam()
# res = SelfPingCheck()
# print(res)

# debugZoneEnd

if __name__ == '__main__':
    if len(sys.argv) > 1:
        type = sys.argv[1]
    else:
        type = 'default'

    if type == 'listdns':
        ListDNSRecords()
    elif type == 'listinstance':
        GetInstanceList()
    elif type == 'listscripts':
        ListStartUpScripts()
    elif type == 'getaimdnsrecorddetail':
        GetAimDNSRecordDetail()
    elif type == 'regularcheck':
        RegularCheck()
    elif type == 'selfpingcheck':
        SelfPingCheck()
    elif type == 'checkenvparams':
        CheckOSEnvParam()
    else:
        print('VALID COMMANDS:\nlistdns\nlistinstance\nlistscripts\nregularcheck\ngetaimdnsrecorddetail\ncheckenvparams\n')
