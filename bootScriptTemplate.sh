#!/bin/sh

# survivor
cd ~/
git clone https://github.com/CoderCIRNO/SurvivorVPN.git
cd ~/SurvivorVPN
touch pingServer.sh
chmod +x pingServer.sh
# 此处 3 项配置
cat > pingServer.sh<<-EOF
PingServerPort=
PingServerToken=""
PingAim=""
systemctl stop firewalld
export PingServerPort
export PingServerToken
export PingAim
cd ~/SurvivorVPN
python3 pingServer.py >> ~/pingServer.log
systemctl start firewalld
EOF

./pingServer.sh

cd ~/SurvivorVPN
touch regularRun.sh
chmod +x regularRun.sh
# 此处 11 项配置（与上面的 3 项存在重复）
cat > regularRun.sh<<-EOF
# Cloudflareconfig
ZoneID=""
AimDNSRecoreID=""
AimDNSName=""
CloudFlareToken=""

# Vultrconfig
VultrToken=""
DefaultRegion=""
DefaultPlan=""
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
cd ~/SurvivorVPN
python3 pingCheckUpdate.py regularcheck >> ~/autorun.log
EOF

# deploy VPN
cd ~/SurvivorVPN
chmod +x shadowsocksR.sh

# 此处 5 项配置
shadowsocksport=
shadowsockspwd=""
shadowsockscipher=""
shadowsockprotocol=""
shadowsockobfs=""

export shadowsocksport
export shadowsockspwd
export shadowsockscipher
export shadowsockprotocol
export shadowsockobfs

./shadowsocksR.sh

# add regular check crontab
cd ~/SurvivorVPN
touch regular.crontab
cat > regular.crontab<<-EOF
0 0,3,6,9,12,15,18,21 * * * cd ~/SurvivorVPN; ./regularRun.sh
EOF
crontab regular.crontab
