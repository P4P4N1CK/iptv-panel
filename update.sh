#!/bin/bash
clear

curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/ott_sam.sh" >/usr/bin/ott_sam.sh
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/template.txt" >/root/iptv-panel/template.txt
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/__init__.py" >/root/iptv-panel/__init__.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/_pytransform.so" >/root/iptv-panel/_pytransform.so

chmod +x /usr/bin/ott_sam.sh
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

run.sh
