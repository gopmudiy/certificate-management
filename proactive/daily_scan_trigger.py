"""
CertAgent - Proactive Daily Scan Trigger
Invoked by EventBridge. Optionally invokes Bedrock Agent for intelligent alerting,
or falls back to direct Lambda scan + SNS notification.
"""

import json
import os
import boto3

lambda_client = boto3.client("lambda")
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")


def lambda_handler(event, context):
    """
    Daily proactive scan. Two modes:
    1. Direct mode (default): Invoke scan Lambda directly
    2. Agent mode: Invoke Bedrock Agent for intelligent analysis
    """
    mode = os.environ.get("PROACTIVE_MODE", "direct")

    if mode == "agent":
        return invoke_agent_scan()
    else:
        return invoke_direct_scan()


def invoke_direct_scan():
    """Invoke the scan Lambda directly."""
    response = lambda_client.invoke(
        FunctionName="certagent-scan-certificates",
        InvocationType="Event",  # async
        Payload=json.dumps({"source": "aws.events"}),
    )
    return {"statusCode": 200, "body": "Direct scan triggered"}


def invoke_agent_scan():
    """Invoke Bedrock Agent for intelligent scan + analysis."""
    agent_id = os.environ.get("BEDROCK_AGENT_ID", "")
    agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "")

    if not agent_id or not agent_alias_id:
        return invoke_direct_scan()

    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId="daily-proactive-scan",
        inputText="Scan all certificates expiring in the next 14 days. "
                  "For any CRITICAL or EXPIRED certs, provide renewal recommendations. "
                  "Send a summary notification.",
    )

    # Collect agent response
    completion = ""
    for event in response["completion"]:
        if "chunk" in event:
            completion += event["chunk"]["bytes"].decode()

    return {"statusCode": 200, "body": completion}
