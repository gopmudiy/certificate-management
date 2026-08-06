#!/bin/bash
# CertAgent Workshop - SageMaker Setup Script
# Run this once when the notebook instance starts

set -e
echo "=== CertAgent Workshop Setup ==="

# Install Python dependencies
pip install -q boto3>=1.35.0 cryptography>=42.0.0 aws-lambda-powertools>=3.0.0 \
    pydantic>=2.0.0 pyyaml>=6.0.0 tabulate>=0.9.0 aws-sam-cli

# Clone workshop repo if not present
REPO_DIR="$HOME/SageMaker/certificate-management"
if [ ! -d "$REPO_DIR" ]; then
    echo "Cloning workshop repository..."
    git clone https://github.com/gopmudiy/certificate-management.git "$REPO_DIR"
fi

echo "=== Setup complete ==="
echo "Open notebooks/00_environment_setup.ipynb to start"
