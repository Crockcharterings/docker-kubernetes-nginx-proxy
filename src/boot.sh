#!/bin/bash

# Fail hard and fast
set -eo pipefail

# Generate nginx config
python3.5 /opt/generator.py

# Start nginx
echo "[nginx] starting nginx service..."
service nginx start

if [ -f "/var/log/nginx/error.log" ]; then
  cat /etc/nginx/nginx.conf
  cat /var/log/nginx/error.log
fi
