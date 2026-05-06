"""
CertAgent - Store Certificate
Stores a manually provided certificate + key in Secrets Manager.
Used when certs are obtained outside the automated flow.
"""

import json
import os
import boto3
from datetime import datetime, timezone

secrets_client = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    Store a certificate bundle manually.
    Event: {
        "domain": "*.example.com",
        "certificate": "-----BEGIN CERTIFICATE-----...",
        "private_key": "-----BEGIN PRIVATE KEY-----...",
        "chain": "-----BEGIN CERTIFICATE-----...",
        "order_id": "optional"
    }
    """
    domain = event["domain"]
    certificate = event["certificate"]
    private_key = event.get("private_key", "")
    chain = event.get("chain", "")
    order_id = event.get("order_id", "manual")

    prefix = os.environ.get("CERT_SECRETS_PREFIX", "/certagent/certs")
    now = datetime.now(timezone.utc).isoformat()

    # Store certificate
    cert_secret_name = f"{prefix}/{domain}/certificate"
    cert_value = json.dumps({
        "certificate": certificate,
        "chain": chain,
        "stored_at": now,
    })
    _upsert_secret(cert_secret_name, cert_value, f"CertAgent cert for {domain}")

    # Store private key if provided
    if private_key:
        key_secret_name = f"{prefix}/{domain}/private-key"
        key_value = json.dumps({
            "private_key": private_key,
            "stored_at": now,
        })
        _upsert_secret(key_secret_name, key_value, f"CertAgent key for {domain}")

    # Update inventory
    table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])
    table.put_item(
        Item={
            "domain": domain,
            "order_id": order_id,
            "renewal_status": "manually_stored",
            "last_scanned": now,
            "stored_at": now,
        }
    )

    return {
        "statusCode": 200,
        "body": {
            "success": True,
            "domain": domain,
            "message": f"Certificate for {domain} stored in Secrets Manager.",
        },
    }


def _upsert_secret(name, value, description):
    try:
        secrets_client.put_secret_value(SecretId=name, SecretString=value)
    except secrets_client.exceptions.ResourceNotFoundException:
        secrets_client.create_secret(Name=name, Description=description, SecretString=value)
