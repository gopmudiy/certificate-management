#!/bin/bash
# package_lambdas.sh — Build and upload Lambda deployment package to S3
#
# Usage:
#   ./scripts/package_lambdas.sh <S3_BUCKET> [S3_KEY_PREFIX]
#
# Example:
#   ./scripts/package_lambdas.sh my-workshop-bucket certagent/lambda-packages
#
# This creates a single zip containing all Lambda handlers, then uploads to S3.
# The CF template references this zip via LambdaCodeBucket and LambdaCodeKey params.

set -euo pipefail

BUCKET="${1:?Usage: $0 <S3_BUCKET> [S3_KEY_PREFIX]}"
PREFIX="${2:-certagent/lambda-packages}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="/tmp/certagent-lambda-build"
ZIP_FILE="/tmp/certagent.zip"

echo "=== CertAgent Lambda Packaging ==="
echo "Project : $PROJECT_DIR"
echo "Bucket  : s3://$BUCKET/$PREFIX/"
echo ""

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy all Lambda handlers into the build directory
# Each handler.py is placed at the root level (flat structure)
# In production, you might use separate zips per function.
for fn_dir in "$PROJECT_DIR"/lambdas/*/; do
    fn_name=$(basename "$fn_dir")
    echo "  Packaging: $fn_name"
    cp "$fn_dir"/*.py "$BUILD_DIR/" 2>/dev/null || true
done

# Copy slack handler
if [ -f "$PROJECT_DIR/slack/slack_handler.py" ]; then
    cp "$PROJECT_DIR/slack/slack_handler.py" "$BUILD_DIR/"
    echo "  Packaging: slack_handler"
fi

# Install dependencies into the build dir
echo ""
echo "Installing Python dependencies..."
pip install -q -t "$BUILD_DIR" \
    cryptography \
    pyyaml \
    2>/dev/null

# Remove unnecessary files to reduce zip size
find "$BUILD_DIR" -name "*.pyc" -delete
find "$BUILD_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$BUILD_DIR" -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true

# Create zip
echo ""
echo "Creating deployment package..."
cd "$BUILD_DIR"
rm -f "$ZIP_FILE"
zip -r9 "$ZIP_FILE" . -x "*.pyc" > /dev/null
ZIP_SIZE=$(du -h "$ZIP_FILE" | cut -f1)
echo "  Package: $ZIP_FILE ($ZIP_SIZE)"

# Upload to S3
echo ""
echo "Uploading to S3..."
S3_KEY="$PREFIX/certagent.zip"
aws s3 cp "$ZIP_FILE" "s3://$BUCKET/$S3_KEY"
echo "  Uploaded: s3://$BUCKET/$S3_KEY"

# Clean up
rm -rf "$BUILD_DIR" "$ZIP_FILE"

echo ""
echo "=== Done ==="
echo ""
echo "Use these CF parameters:"
echo "  LambdaCodeBucket = $BUCKET"
echo "  LambdaCodeKey    = $S3_KEY"
