"""
CertAgent - Download Certificate
Downloads issued certificate + chain from DigiCert and stores in Secrets Manager.
"""

import json
import os
import boto3
import urllib.request
import urllib.error
from datetime import datetime, timezone

secrets_client = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")


def get_digicert_api_key():
    secret_arn = os.environ["DIGICERT_API_SECRET_ARN"]
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])["api_key"]


def download_cert_pem(certificate_id, api_key):
    """Download cert in PEM format (cert + intermediate + root)."""
    base_url = os.environ.get("DIGICERT_BASE_URL", "https://www.digicert.com/services/v2")
    url = f"{base_url}/certificate/{certificate_id}/download/format/pem_all"
    headers = {"X-DC-DEVKEY": api_key, "Accept": "application/x-pem-file"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()


def store_certificate(domain, cert_pem, certificate_id):
    """Store certificate chain in Secrets Manager."""
    prefix = os.environ.get("CERT_SECRETS_PREFIX", "/certagent/certs")
    secret_name = f"{prefix}/{domain}/certificate"

    secret_value = json.dumps({
        "certificate_chain": cert_pem,
        "certificate_id": certificate_id,
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        secrets_client.put_secret_value(SecretId=secret_name, SecretString=secret_value)
    except secrets_client.exceptions.ResourceNotFoundException:
        secrets_client.create_secret(
            Name=secret_name,
            Description=f"CertAgent certificate chain for {domain}",
            SecretString=secret_value,
        )


def lambda_handler(event, context):
    """
    Download an issued certificate.
    Event: {"certificate_id": "12345", "common_name": "*.example.com", "order_id": "67890"}
    """
    certificate_id = event["certificate_id"]
    common_name = event.get("common_name", "unknown")
    order_id = event.get("order_id", "")

    api_key = get_digicert_api_key()

    # Download PEM bundle
    cert_pem = download_cert_pem(certificate_id, api_key)

    # Store in Secrets Manager
    store_certificate(common_name, cert_pem, certificate_id)

    # Update DynamoDB
    if order_id and common_name != "unknown":
        table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])
        table.update_item(
            Key={"domain": common_name, "order_id": order_id},
            UpdateExpression="SET renewal_status = :s, downloaded_at = :t",
            ExpressionAttributeValues={
                ":s": "completed",
                ":t": datetime.now(timezone.utc).isoformat(),
            },
        )

    return {
        "statusCode": 200,
        "body": {
            "success": True,
            "domain": common_name,
            "certificate_id": certificate_id,
            "stored_at": f"/certagent/certs/{common_name}/certificate",
            "message": f"Certificate for {common_name} downloaded and stored in Secrets Manager.",
        },
    }
