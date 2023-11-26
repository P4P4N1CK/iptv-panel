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

mv /root/iptv-panel/menu.sh /usr/bin/menu.sh
mv /root/iptv-panel/run.sh /usr/bin/run.sh

chmod +x /usr/bin/menu.sh
chmod +x /usr/bin/run.sh
(crontab -l ; echo "0 0 * * * reboot") | crontab -
(crontab -l ; echo "10 0 * * * run.sh") | crontab -

echo "Script completed successfully!"
