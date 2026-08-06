#!/bin/bash
# deploy.sh — One-step build, package, and deploy for CertAgent Workshop
#
# Usage:
#   ./scripts/deploy.sh                  # Deploy to your current AWS account
#   ./scripts/deploy.sh --package-only   # Package only (for Workshop Studio upload)
#
# Prerequisites:
#   - AWS SAM CLI installed (pip install aws-sam-cli)
#   - AWS CLI configured with credentials
#   - Docker running (optional, for --use-container builds)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE="infra/workshop-account-setup.yaml"
STACK_NAME="certagent-workshop"
PACKAGED_TEMPLATE="infra/workshop-account-setup-packaged.yaml"

# Parse args
PACKAGE_ONLY=false
S3_BUCKET=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --package-only) PACKAGE_ONLY=true; shift;;
    --bucket) S3_BUCKET="$2"; shift 2;;
    --stack-name) STACK_NAME="$2"; shift 2;;
    *) echo "Unknown option: $1"; exit 1;;
  esac
done

cd "$PROJECT_DIR"

echo "=============================================="
echo "  CertAgent Workshop — Deploy"
echo "=============================================="
echo ""
echo "Project dir : $PROJECT_DIR"
echo "Template    : $TEMPLATE"
echo "Stack name  : $STACK_NAME"
echo ""

# ── Step 1: SAM Build ────────────────────────────────────────────────────────
echo "=== Step 1: sam build ==="
sam build --template-file "$TEMPLATE"
echo ""

# ── Step 2: Determine S3 bucket ──────────────────────────────────────────────
if [ -z "$S3_BUCKET" ]; then
  ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
  REGION=$(aws configure get region || echo "us-east-1")
  S3_BUCKET="certagent-deploy-${ACCOUNT_ID}-${REGION}"

  # Create if not exists
  if ! aws s3 ls "s3://$S3_BUCKET" 2>/dev/null; then
    echo "Creating S3 bucket: $S3_BUCKET"
    if [ "$REGION" = "us-east-1" ]; then
      aws s3 mb "s3://$S3_BUCKET"
    else
      aws s3 mb "s3://$S3_BUCKET" --region "$REGION"
    fi
  fi
fi
echo "S3 bucket   : $S3_BUCKET"
echo ""

# ── Step 3: SAM Package ─────────────────────────────────────────────────────
echo "=== Step 2: sam package ==="
sam package \
  --template-file .aws-sam/build/template.yaml \
  --output-template-file "$PACKAGED_TEMPLATE" \
  --s3-bucket "$S3_BUCKET" \
  --s3-prefix certagent-lambda

echo ""
echo "Packaged template: $PACKAGED_TEMPLATE"
echo "(Lambda code uploaded to s3://$S3_BUCKET/certagent-lambda/)"
echo ""

# ── If package-only, stop here ───────────────────────────────────────────────
if [ "$PACKAGE_ONLY" = true ]; then
  echo "=============================================="
  echo "  PACKAGE COMPLETE (--package-only)"
  echo "=============================================="
  echo ""
  echo "For Workshop Studio:"
  echo "  1. Upload '$PACKAGED_TEMPLATE' as the account provisioning template"
  echo "  2. Capabilities: CAPABILITY_IAM, CAPABILITY_NAMED_IAM, CAPABILITY_AUTO_EXPAND"
  echo "  3. No parameters needed (all have defaults)"
  echo ""
  echo "For manual CloudFormation deploy:"
  echo "  aws cloudformation create-stack \\"
  echo "    --stack-name $STACK_NAME \\"
  echo "    --template-body file://$PACKAGED_TEMPLATE \\"
  echo "    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND"
  echo ""
  exit 0
fi

# ── Step 4: SAM Deploy ──────────────────────────────────────────────────────
echo "=== Step 3: sam deploy ==="
sam deploy \
  --template-file "$PACKAGED_TEMPLATE" \
  --stack-name "$STACK_NAME" \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
  --no-confirm-changeset \
  --no-fail-on-empty-changeset

echo ""
echo "=============================================="
echo "  DEPLOYMENT COMPLETE"
echo "=============================================="
echo ""

# Print outputs
echo "Stack outputs:"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
  --output table 2>/dev/null || true

echo ""
echo "Next steps:"
echo "  1. Open the SageMaker Studio URL from outputs above"
echo "  2. Launch the 'certagent-lab' JupyterLab space"
echo "  3. Open certagent-notebooks/01_explore_lambdas.ipynb"
