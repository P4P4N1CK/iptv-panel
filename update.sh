#!/bin/bash
clear

curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/ott_sam.sh" >/usr/bin/ott_sam.sh
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/menu.sh" >/usr/bin/menu
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/template.txt" >/root/iptv-panel/template.txt
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/main.py" >/root/iptv-panel/main.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/__init__.py" >/root/iptv-panel/pytransform/__init__.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/_pytransform.so" >/root/iptv-panel/pytransform/_pytransform.so

chmod +x /usr/bin/ott_sam.sh
chmod +x /usr/bin/menu
ipvps=$(curl -s "https://ipv4.icanhazip.com")
if [ "$(curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv/main/panel_bot.sh" | grep -wc "${ipvps}")" != '0' ]; then
    if ! crontab -l | grep -q "ott_sam.sh -a"; then
        (
            crontab -l
            echo "0 12 * * * ott_sam.sh -a > /root/t1.log 2>&1"
        ) | crontab -
    fi
    if ! crontab -l | grep -q "ott_sam.sh -b"; then
        (
            crontab -l
            echo "0 13 * * * ott_sam.sh -b > /root/t1.log 2>&1"
        ) | crontab -
    fi
fi

run.sh
