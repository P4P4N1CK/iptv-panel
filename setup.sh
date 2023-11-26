#!/bin/bash
clear

read -p "Input Domain : " domain

sudo apt update
sudo apt upgrade -y

sudo apt install -y python3-pip
sudo apt install git -y
sudo certbot certonly --standalone -d ${domain}
git clone https://github.com/syfqsamvpn/iptv-panel.git
echo "$domain" >/root/iptv-panel/domain.txt
cd /root/iptv-panel
pip3 install -r requirements.txt

echo "Script completed successfully!"
