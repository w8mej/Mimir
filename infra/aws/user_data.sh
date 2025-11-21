
#!/bin/bash
set -euxo pipefail
yum update -y
amazon-linux-extras install docker -y || yum install -y docker
systemctl enable --now docker
yum install -y aws-nitro-enclaves-cli aws-nitro-enclaves-cli-devel jq
systemctl enable --now nitro-enclaves-allocator.service
# Start KMS vsock proxy in background (port 8000)
bash /opt/mimir/enclave/parent_start_kms_proxy.sh &

usermod -aG docker ec2-user || true
usermod -aG ne ec2-user || true
cd /opt; mkdir -p /opt/mimir
if [ -f /opt/mimir.tar.gz ]; then tar -xzf /opt/mimir.tar.gz -C /opt/mimir --strip-components=1; fi
cd /opt/mimir
docker build -f docker/Dockerfile.coordinator -t ghcr.io/example/mimir-coordinator:enclave .
/opt/mimir/enclave/build_eif.sh ghcr.io/example/mimir-coordinator:enclave /opt/coordinator.eif || true
/opt/mimir/enclave/run_enclave.sh /opt/coordinator.eif || true
