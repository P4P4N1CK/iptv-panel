#!/bin/bash
clear
domain=$(sed -n '1p' /root/iptv-panel/domain.txt)
cd /root
pkill -f "gunicorn.*main:app" >/dev/null 2>&1
bash -c "cd '/root/iptv-panel' && gunicorn -w 1 -b 0.0.0.0:443 --keyfile /etc/letsencrypt/live/${domain}/privkey.pem --certfile /etc/letsencrypt/live/${domain}/fullchain.pem --preload main:app --daemon"