#!/bin/bash
clear

curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/ott_sam.sh" >/usr/bin/ott_sam.sh
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
    run.sh
fi
