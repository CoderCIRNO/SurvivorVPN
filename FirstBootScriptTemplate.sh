#!/bin/bash

echo "Script Version V0.08" >> ~/autorun.log

# survivor
cd ~/
success = 0
git clone https://github.com/CoderCIRNO/SurvivorVPN.git >> ~/autorun.log
success = `ls | grep -c SurvivorVPN`
while (($success == 0))
do
    echo "cloning again" >> ~/autorun.log
    git clone https://github.com/CoderCIRNO/SurvivorVPN.git >> ~/autorun.log
    success = `ls | grep -c SurvivorVPN`
    if (($success == 0))
    then
        echo "git clone failed, retry in 3 sec" >> ~/autorun.log
        sleep 3
    else
        echo "git clone succeed" >> ~/autorun.log
    fi
done
cd ~/SurvivorVPN

cat > envParams<<-EOF
# Cloudflareconfig
ZoneID=""
AimDNSRecoreID=""
AimDNSName=""
CloudFlareToken=""

# Vultrconfig
VultrToken=""
DefaultRegion="sgp"
DefaultPlan="vc2-1c-1gb"
StartUpScriptID=""

# PingServer
PingServerPort=
PingServerToken=""
PingAim=""

export ZoneID
export AimDNSRecoreID
export AimDNSName
export CloudFlareToken
export VultrToken
export DefaultRegion
export DefaultPlan
export StartUpScriptID
export PingServerPort
export PingServerToken
export PingAim

shadowsocksport=
shadowsockspwd=""
shadowsockscipher="aes-256-cfb"
shadowsockprotocol="origin"
shadowsockobfs="plain"

export shadowsocksport
export shadowsockspwd
export shadowsockscipher
export shadowsockprotocol
export shadowsockobfs

EOF

cp envParams regularRun.sh
chmod +x regularRun.sh
cat >> regularRun.sh<<-EOF
cd ~/SurvivorVPN
python3 pingCheckUpdate.py regularcheck >> ~/autorun.log
EOF

# deploy VPN
cd ~/SurvivorVPN

cp envParams deployVPN.sh
chmod +x deployVPN.sh

cat shadowsocksR.sh >> deployVPN.sh
rm shadowsocksR.sh

nohup ./deployVPN.sh >> ~/deployVPNOutput.log 2>&1 &

./regularRun.sh
