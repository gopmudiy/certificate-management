"""
CertAgent - List Inventory
Queries DynamoDB for the full certificate inventory with optional filtering.
"""

import json
import os
import boto3
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    """
    List certificate inventory.
    Event: {"status": "all|pending|renewed|expired|completed"}
    """
    status_filter = event.get("status", "all")
    table = dynamodb.Table(os.environ["CERT_TABLE_NAME"])

    # Scan with optional filter
    if status_filter and status_filter != "all":
        response = table.scan(
            FilterExpression=Attr("renewal_status").eq(status_filter)
        )
    else:
        response = table.scan()

    items = response.get("Items", [])

    # Handle pagination
    while "LastEvaluatedKey" in response:
        if status_filter and status_filter != "all":
            response = table.scan(
                FilterExpression=Attr("renewal_status").eq(status_filter),
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
        else:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    # Sort by days_remaining (most urgent first)
    items.sort(key=lambda x: x.get("days_remaining", 9999))

    # Summary stats
    summary = {
        "total": len(items),
        "pending": sum(1 for i in items if i.get("renewal_status") == "pending"),
        "submitted": sum(1 for i in items if i.get("renewal_status") == "submitted"),
        "issued": sum(1 for i in items if i.get("renewal_status") == "issued"),
        "completed": sum(1 for i in items if i.get("renewal_status") == "completed"),
        "failed": sum(1 for i in items if "failed" in i.get("renewal_status", "")),
    }

    return {
        "statusCode": 200,
        "body": {
            "summary": summary,
            "certificates": items,
        },
    }
