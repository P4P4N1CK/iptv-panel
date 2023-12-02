#!/bin/bash
clear

curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/ott_sam.sh" >/usr/bin/ott_sam.sh
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/menu.sh" >/usr/bin/menu
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/main.py" >/root/iptv-panel/main.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/system_ott.py" >/root/iptv-panel/system_ott.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/__init__.py" >/root/iptv-panel/pytransform/__init__.py
curl -s "https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/pytransform/_pytransform.so" >/root/iptv-panel/pytransform/_pytransform.so

chmod +x /usr/bin/ott_sam.sh
chmod +x /usr/bin/menu

echo "EXPIRED_DATA = \"expired.json\"" >/root/iptv-panel/data.txt

run.sh
