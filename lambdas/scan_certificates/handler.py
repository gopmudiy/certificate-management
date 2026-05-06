"""
CertAgent - Scan Certificates
Queries DigiCert CertCentral API for all issued certificates,
identifies those expiring within the configured threshold,
and updates the inventory in DynamoDB.
"""

import json
import os
import boto3
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

secrets_client = boto3.client("secretsmanager")
dynamodb = boto3.resource("dynamodb")
sns_client = boto3.client("sns")


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


def list_expiring_certificates(api_key, threshold_days):
    """Fetch all issued orders and filter for expiring certs."""
    threshold_date = datetime.now(timezone.utc) + timedelta(days=threshold_days)
    expiring = []
    offset = 0
    limit = 100

    while True:
        response = digicert_request(
            f"/order/certificate?filters[status]=issued&limit={limit}&offset={offset}",
            api_key,
        )

        orders = response.get("orders", [])
        if not orders:
            break

        for order in orders:
            cert = order.get("certificate", {})
            valid_till = cert.get("valid_till")
            if not valid_till:
                continue

            # DigiCert returns dates as "2026-06-15"
            expiry_date = datetime.strptime(valid_till, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days_remaining = (expiry_date - datetime.now(timezone.utc)).days

            if days_remaining <= threshold_days:
                expiring.append({
                    "order_id": str(order["id"]),
                    "certificate_id": str(cert.get("id", "")),
                    "common_name": cert.get("common_name", "unknown"),
                    "sans": cert.get("dns_names", []),
                    "valid_from": cert.get("valid_from", ""),
                    "valid_till": valid_till,
                    "days_remaining": days_remaining,
                    "product_name": order.get("product", {}).get("name", ""),
                    "product_type": order.get("product", {}).get("type", ""),
                    "organization": order.get("organization", {}).get("name", ""),
                    "status": order.get("status", ""),
                    "priority": classify_priority(days_remaining),
                })

        if len(orders) < limit:
            break
        offset += limit

    return sorted(expiring, key=lambda x: x["days_remaining"])


def classify_priority(days_remaining):
    if days_remaining <= 0:
        return "EXPIRED"
    elif days_remaining <= 7:
        return "CRITICAL"
    elif days_remaining <= 14:
        return "HIGH"
    elif days_remaining <= 30:
        return "MEDIUM"
    return "LOW"


def update_inventory(expiring_certs):
    """Upsert expiring certs into DynamoDB inventory."""
    table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])

    for cert in expiring_certs:
        table.put_item(
            Item={
                "domain": cert["common_name"],
                "order_id": cert["order_id"],
                "certificate_id": cert["certificate_id"],
                "sans": cert["sans"],
                "valid_till": cert["valid_till"],
                "days_remaining": cert["days_remaining"],
                "product_name": cert["product_name"],
                "organization": cert["organization"],
                "priority": cert["priority"],
                "last_scanned": datetime.now(timezone.utc).isoformat(),
                "renewal_status": "pending",
            }
        )


def send_notification(expiring_certs):
    """Send SNS notification with summary of expiring certs."""
    if not expiring_certs:
        return

    topic_arn = os.environ.get("NOTIFICATION_TOPIC_ARN")
    if not topic_arn:
        return

    critical = [c for c in expiring_certs if c["priority"] in ("EXPIRED", "CRITICAL")]
    high = [c for c in expiring_certs if c["priority"] == "HIGH"]
    medium = [c for c in expiring_certs if c["priority"] == "MEDIUM"]

    subject = f"CertAgent: {len(expiring_certs)} certificate(s) expiring soon"

    lines = [
        f"CertAgent Scan Results — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"",
        f"Total expiring: {len(expiring_certs)}",
        f"  🔴 Critical/Expired: {len(critical)}",
        f"  🟠 High: {len(high)}",
        f"  🟡 Medium: {len(medium)}",
        f"",
        "Details:",
    ]

    for cert in expiring_certs:
        emoji = {"EXPIRED": "💀", "CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}.get(
            cert["priority"], "🟢"
        )
        lines.append(
            f"  {emoji} {cert['common_name']} — {cert['days_remaining']}d remaining "
            f"(expires {cert['valid_till']}) [{cert['product_name']}]"
        )

    sns_client.publish(
        TopicArn=topic_arn,
        Subject=subject[:100],
        Message="\n".join(lines),
    )


def lambda_handler(event, context):
    """
    Main handler. Can be invoked by:
    - EventBridge (daily scan)
    - Bedrock Agent action group (on-demand scan)
    """
    threshold_days = int(os.environ.get("EXPIRY_THRESHOLD_DAYS", "30"))

    # Bedrock Agent invocation format
    is_agent = "actionGroup" in event
    if is_agent:
        params = {}
        for p in event.get("parameters", []):
            params[p["name"]] = p["value"]
        threshold_days = int(params.get("threshold_days", threshold_days))
    elif "threshold_days" in event:
        threshold_days = int(event["threshold_days"])

    api_key = get_digicert_api_key()
    expiring_certs = list_expiring_certificates(api_key, threshold_days)

    # Update DynamoDB inventory
    update_inventory(expiring_certs)

    # Send notification if triggered by EventBridge (not agent)
    if not is_agent and "source" in event and event.get("source") == "aws.events":
        send_notification(expiring_certs)

    # Build response body
    if expiring_certs:
        body_text = f"Found {len(expiring_certs)} certificate(s) expiring within {threshold_days} days:\n"
        for cert in expiring_certs:
            body_text += f"- {cert['common_name']} (Order: {cert['order_id']}) — {cert['days_remaining']} days remaining, expires {cert['valid_till']}, priority: {cert['priority']}\n"
    else:
        body_text = f"No certificates found expiring within {threshold_days} days. All certificates are healthy."

    # Bedrock Agent response format
    if is_agent:
        return {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": event.get("actionGroup", ""),
                "function": event.get("function", ""),
                "functionResponse": {
                    "responseBody": {
                        "TEXT": {"body": body_text}
                    }
                },
            },
        }

    # Direct invocation response
    return {
        "statusCode": 200,
        "body": {
            "total_expiring": len(expiring_certs),
            "certificates": expiring_certs,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "threshold_days": threshold_days,
        },
    }
