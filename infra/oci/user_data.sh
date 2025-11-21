
#!/bin/bash
set -euxo pipefail
apt-get update -y || true
apt-get install -y docker.io docker-compose-plugin || (yum install -y docker && systemctl enable --now docker)
systemctl enable --now docker || true
mkdir -p /opt/mimir
if [ -f /opt/mimir.tar.gz ]; then tar -xzf /opt/mimir.tar.gz -C /opt/mimir --strip-components=1; fi
cd /opt/mimir
docker compose -f docker/compose.yml up -d

# TLS: place certs at /opt/mimir/certs before compose up to enable mTLS.
