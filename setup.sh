#!/bin/bash
clear

ipvps=$(curl -s https://ipv4.icanhazip.com)

# Fetch the panel IP from the provided URL
panel_ips=$(curl -s https://raw.githubusercontent.com/syfqsamvpn/iptv/main/panel_access.txt)

# Check if the current server's IP matches the panel IP
if [ "$(echo "${panel_ips}" | grep -wc "${ipvps}")" != '0' ]; then
    read -p "Input Domain: " domain

    sudo apt update
    sudo apt upgrade -y

    sudo apt install -y python3-pip
    sudo apt install git -y
    sudo apt install certbot -y
    sudo certbot certonly --standalone -d ${domain}
    git clone https://github.com/syfqsamvpn/iptv-panel.git
    echo "$domain" >/root/iptv-panel/domain.txt
    cd /root/iptv-panel
    pip3 install -r requirements.txt

    mv /root/iptv-panel/menu.sh /usr/bin/menu.sh
    mv /root/iptv-panel/run.sh /usr/bin/run.sh

    chmod +x /usr/bin/menu.sh
    chmod +x /usr/bin/run.sh
    echo "menu.sh" >>"/root/.profile"
    (
        crontab -l
        echo "0 0 * * * reboot"
    ) | crontab -
    (
        crontab -l
        echo "10 0 * * * run.sh"
    ) | crontab -
    run.sh
    sudo -i
else
    echo "Access denied. Panel IP matches server IP."
    exit 1
fi
