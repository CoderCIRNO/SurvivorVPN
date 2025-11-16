#!/bin/bash

echo "Script Version V0.09" >> ~/autorun.log

# survivor
cd ~/
wget https://github.com/CoderCIRNO/SurvivorVPN/archive/refs/heads/main.zip
unzip main.zip
mv SurvivorVPN-main SurvivorVPN
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

# Run deploy loop in background; re-check shadowsocks status each iteration
(
    success=0
    success=$(shadowsocks status | grep -c running)
    while [ "$success" -eq 0 ]; do
        ./deployVPN.sh >> ~/deployVPNOutput.log
        success=$(shadowsocks status | grep -c running)
        sleep 1
    done
) &

./regularRun.sh
