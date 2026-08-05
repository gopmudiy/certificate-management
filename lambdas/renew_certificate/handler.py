"""
CertAgent - Renew Certificate
Generates a new CSR, submits a renewal request to DigiCert,
and stores the private key in Secrets Manager.
"""

import json
import os
import boto3
import urllib.request
import urllib.error
from datetime import datetime, timezone
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

secrets_client = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")


def get_digicert_api_key():
    secret_arn = os.environ["DIGICERT_API_SECRET_ARN"]
    response = secrets_client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])["api_key"]


def digicert_request(path, api_key, method="GET", body=None):
    base_url = os.environ.get("DIGICERT_BASE_URL", "https://www.digicert.com/services/v2")
    url = f"{base_url}{path}"
    headers = {
        "X-DC-DEVKEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        raise Exception(f"DigiCert API error {e.code}: {error_body}")


def generate_csr_and_key(common_name, sans=None):
    """Generate RSA 2048 key pair and CSR."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])

    builder = x509.CertificateSigningRequestBuilder().subject_name(subject)

    # Add SANs if provided
    if sans:
        san_list = [x509.DNSName(name) for name in sans]
        builder = builder.add_extension(
            x509.SubjectAlternativeName(san_list), critical=False
        )

    csr = builder.sign(private_key, hashes.SHA256())

    # Serialize
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode()

    return private_key_pem, csr_pem


def store_private_key(domain, private_key_pem, order_id):
    """Store private key in Secrets Manager."""
    prefix = os.environ.get("CERT_SECRETS_PREFIX", "/certagent/certs")
    secret_name = f"{prefix}/{domain}/private-key"

    try:
        secrets_client.put_secret_value(
            SecretId=secret_name,
            SecretString=json.dumps({
                "private_key": private_key_pem,
                "order_id": order_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }),
        )
    except secrets_client.exceptions.ResourceNotFoundException:
        secrets_client.create_secret(
            Name=secret_name,
            Description=f"CertAgent private key for {domain}",
            SecretString=json.dumps({
                "private_key": private_key_pem,
                "order_id": order_id,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }),
        )


def submit_renewal(api_key, order_id, csr_pem, common_name):
    """Submit renewal request to DigiCert."""
    body = {
        "certificate": {
            "common_name": common_name,
            "csr": csr_pem,
        },
    }

    response = digicert_request(
        f"/order/certificate/{order_id}/renew",
        api_key,
        method="POST",
        body=body,
    )

    return response


def update_inventory(domain, order_id, new_order_id, status):
    """Update DynamoDB with renewal status."""
    table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])
    table.update_item(
        Key={"domain": domain, "order_id": order_id},
        UpdateExpression="SET renewal_status = :s, new_order_id = :nid, renewed_at = :t",
        ExpressionAttributeValues={
            ":s": status,
            ":nid": str(new_order_id),
            ":t": datetime.now(timezone.utc).isoformat(),
        },
    )


MOCK_ORDER_IDS = {"12345678", "12345679", "12345680", "12345681", "12345682"}


def is_mock_order(order_id: str) -> bool:
    """Detect if an order ID is from mock data."""
    return order_id in MOCK_ORDER_IDS or order_id.startswith("1234")


def mock_renewal(order_id, common_name):
    """Simulate a successful DigiCert renewal for testing."""
    import random
    new_order_id = str(random.randint(90000000, 99999999))
    return {
        "new_order_id": new_order_id,
        "status": "submitted",
        "message": (
            f"[MOCK] Renewal submitted for {common_name}. "
            f"New order {new_order_id} is pending validation. "
            f"DV certificates typically issue within 5 minutes. "
            f"OV/EV certificates may take 1-24 hours."
        ),
    }


def lambda_handler(event, context):
    """
    Renew a certificate.

    Expected event (direct invocation):
    {
        "order_id": "12345678",
        "common_name": "api.example.com",
        "sans": ["api.example.com", "api-v2.example.com"],
        "use_mock": true
    }

    Also supports Bedrock Agent invocation format.
    """
    # Handle Bedrock Agent invocation format
    is_agent = "actionGroup" in event
    if is_agent:
        params = {}
        for p in event.get("parameters", []):
            params[p["name"]] = p["value"]
        order_id = params["order_id"]
        common_name = params["common_name"]
        sans = params.get("sans", "").split(",") if params.get("sans") else []
        use_mock = params.get("use_mock", "false").lower() == "true"
    else:
        order_id = event["order_id"]
        common_name = event["common_name"]
        sans = event.get("sans", [])
        use_mock = event.get("use_mock", False)

    # Ensure common_name is in SANs
    if common_name not in sans:
        sans.insert(0, common_name)

    # Generate new key pair and CSR
    private_key_pem, csr_pem = generate_csr_and_key(common_name, sans)

    # Store private key immediately (before renewal, so we don't lose it)
    store_private_key(common_name, private_key_pem, order_id)

    # Auto-detect mock mode from order ID or explicit flag
    if use_mock or is_mock_order(order_id):
        # Simulate renewal without calling DigiCert
        mock_result = mock_renewal(order_id, common_name)
        new_order_id = mock_result["new_order_id"]
        status = mock_result["status"]
        update_inventory(common_name, order_id, new_order_id, status)

        body = {
            "success": True,
            "domain": common_name,
            "original_order_id": order_id,
            "new_order_id": new_order_id,
            "status": status,
            "message": mock_result["message"],
            "private_key_stored": True,
            "csr_generated": True,
        }
    else:
        # Real DigiCert renewal
        api_key = get_digicert_api_key()
        try:
            response = submit_renewal(api_key, order_id, csr_pem, common_name)
            new_order_id = response.get("id", response.get("order_id", "unknown"))
            status = "submitted"
        except Exception as e:
            new_order_id = "failed"
            status = f"failed: {str(e)}"
            update_inventory(common_name, order_id, new_order_id, status)
            return {
                "statusCode": 500,
                "body": {
                    "success": False,
                    "error": str(e),
                    "domain": common_name,
                    "order_id": order_id,
                },
            }

        body = {
            "success": True,
            "domain": common_name,
            "original_order_id": order_id,
            "new_order_id": str(new_order_id),
            "status": status,
            "message": f"Renewal submitted for {common_name}. Private key stored in Secrets Manager.",
        }

    update_inventory(common_name, order_id, str(new_order_id), status)

    # Bedrock Agent response format
    if is_agent:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "function": event.get("function", ""),
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {"body": json.dumps(body)}
                    }
                },
            },
        }

    return {"statusCode": 200, "body": body}
