#!/bin/bash

# survivor
cd ~/
git clone https://github.com/CoderCIRNO/SurvivorVPN.git
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

EOF

cp envParams pingServer.sh
chmod +x pingServer.sh
cat >> pingServer.sh<<-EOF
systemctl stop firewalld
cd ~/SurvivorVPN
echo "#### Start Ping Server ####"
python3 pingServer.py
systemctl start firewalld
EOF

./pingServer.sh >> ~/pingServer.log


cp envParams regularRun.sh
chmod +x regularRun.sh
cat >> regularRun.sh<<-EOF
cd ~/SurvivorVPN
python3 pingCheckUpdate.py regularcheck >> ~/autorun.log
EOF

# deploy VPN
cd ~/SurvivorVPN
chmod +x shadowsocksR.sh

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

nohup ./shadowsocksR.sh > ~/autorun.log 2>&1 &

# add regular check crontab
cd ~/SurvivorVPN
cat > regular.crontab<<-EOF
0 0,3,6,9,12,15,18,21 * * * cd ~/SurvivorVPN; ./regularRun.sh
EOF
crontab regular.crontab
