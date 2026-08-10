#!/bin/bash
# deploy.sh — One-command deploy for AI Operations Workshop
#
# Usage:
#   ./scripts/deploy.sh              # Deploy to your current AWS account
#   ./scripts/deploy.sh --delete     # Delete the stack and all resources
#
# Prerequisites:
#   - AWS SAM CLI installed (pip install aws-sam-cli)
#   - AWS CLI configured with credentials

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE="infra/workshop-account-setup.yaml"
STACK_NAME="ai-ops-workshop"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Parse args
DELETE=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --delete) DELETE=true; shift;;
    --stack-name) STACK_NAME="$2"; shift 2;;
    --region) REGION="$2"; shift 2;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

cd "$PROJECT_DIR"

# ── Delete flow ──────────────────────────────────────────────────────────────
if [ "$DELETE" = true ]; then
  echo "Deleting stack: $STACK_NAME"
  aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
  echo "Waiting for delete to complete..."
  aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"
  echo "Stack deleted."
  exit 0
fi

# ── Deploy flow ──────────────────────────────────────────────────────────────
echo "=============================================="
echo "  AI Operations Workshop — Deploy"
echo "=============================================="
echo ""
echo "Stack name : $STACK_NAME"
echo "Region     : $REGION"
echo "Template   : $TEMPLATE"
echo ""

echo "=== Building Lambda packages ==="
sam build --template-file "$TEMPLATE"
echo ""

echo "=== Deploying stack ==="
sam deploy \
  --template-file .aws-sam/build/template.yaml \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --region "$REGION" \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset \
  --resolve-s3

echo ""
echo "=============================================="
echo "  DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""

# Print outputs
echo "Stack outputs:"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --region "$REGION" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table 2>/dev/null || true

echo ""
echo "Next steps:"
echo "  1. Open SageMaker Studio from the AWS Console"
echo "  2. Start the 'certagent-lab' JupyterLab space"
echo "  3. Notebooks are auto-populated — start with Module-1-CertManagement"
echo ""
