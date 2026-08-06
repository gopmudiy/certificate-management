#!/bin/bash
# upload_templates.sh — Upload CF templates to S3 for nested stack deployment
#
# Usage:
#   ./scripts/upload_templates.sh <S3_BUCKET> [S3_KEY_PREFIX]
#
# Example:
#   ./scripts/upload_templates.sh my-workshop-bucket certagent/cfn

set -euo pipefail

BUCKET="${1:?Usage: $0 <S3_BUCKET> [S3_KEY_PREFIX]}"
PREFIX="${2:-certagent/cfn}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INFRA_DIR="$(dirname "$SCRIPT_DIR")/infra"

echo "=== Uploading CF Templates ==="
echo "Source : $INFRA_DIR"
echo "Target : s3://$BUCKET/$PREFIX/"
echo ""

for tmpl in workshop-infra.yaml sagemaker-domain.yaml; do
    if [ -f "$INFRA_DIR/$tmpl" ]; then
        aws s3 cp "$INFRA_DIR/$tmpl" "s3://$BUCKET/$PREFIX/$tmpl"
        echo "  Uploaded: $tmpl"
    else
        echo "  MISSING: $tmpl"
    fi
done

echo ""
echo "=== Done ==="
echo ""
echo "Use these CF parameters for workshop-master.yaml:"
echo "  TemplatesBucket = $BUCKET"
echo "  TemplatesPrefix = $PREFIX"
