"""
CertAgent - Check Renewal Status
Polls DigiCert for the current status of a certificate order.
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


def digicert_request(path, api_key):
    base_url = os.environ.get("DIGICERT_BASE_URL", "https://www.digicert.com/services/v2")
    url = f"{base_url}{path}"
    headers = {"X-DC-DEVKEY": api_key, "Accept": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def lambda_handler(event, context):
    """
    Check status of a DigiCert order.
    Event: {"order_id": "12345678"}
    """
    order_id = event["order_id"]
    api_key = get_digicert_api_key()

    response = digicert_request(f"/order/certificate/{order_id}", api_key)

    cert = response.get("certificate", {})
    status = response.get("status", "unknown")

    result = {
        "order_id": order_id,
        "status": status,
        "common_name": cert.get("common_name", ""),
        "valid_from": cert.get("valid_from", ""),
        "valid_till": cert.get("valid_till", ""),
        "certificate_id": str(cert.get("id", "")),
        "product": response.get("product", {}).get("name", ""),
        "organization": response.get("organization", {}).get("name", ""),
    }

    # Update DynamoDB if issued
    if status == "issued" and cert.get("common_name"):
        table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])
        table.update_item(
            Key={"domain": cert["common_name"], "order_id": order_id},
            UpdateExpression="SET renewal_status = :s, certificate_id = :cid, checked_at = :t",
            ExpressionAttributeValues={
                ":s": "issued",
                ":cid": str(cert.get("id", "")),
                ":t": datetime.now(timezone.utc).isoformat(),
            },
        )

    return {"statusCode": 200, "body": result}
