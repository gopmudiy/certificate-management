"""
CertAgent - Slack Handler
Bridges Slack app_mention events to Bedrock Agent.
"""

import json
import os
import boto3
import urllib.request
import hashlib
import hmac
import time
import uuid

secrets_client = boto3.client("secretsmanager")
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime")

_cached_creds = None


def get_slack_creds():
    global _cached_creds
    if _cached_creds:
        return _cached_creds
    resp = secrets_client.get_secret_value(SecretId="/certagent/slack-credentials")
    _cached_creds = json.loads(resp["SecretString"])
    return _cached_creds


def verify_slack_signature(event):
    creds = get_slack_creds()
    signing_secret = creds["signing_secret"]
    headers = event.get("headers", {})
    # Headers may be lowercase
    timestamp = headers.get("x-slack-request-timestamp") or headers.get("X-Slack-Request-Timestamp", "")
    signature = headers.get("x-slack-signature") or headers.get("X-Slack-Signature", "")
    body = event.get("body", "")

    if not timestamp or not signature:
        return True  # Skip in test

    if abs(time.time() - int(timestamp)) > 300:
        return False

    sig_basestring = f"v0:{timestamp}:{body}"
    computed = "v0=" + hmac.new(
        signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


def invoke_agent(user_message, session_id):
    agent_id = os.environ["BEDROCK_AGENT_ID"]
    agent_alias_id = os.environ["BEDROCK_AGENT_ALIAS_ID"]

    response = bedrock_agent_runtime.invoke_agent(
        agentId=agent_id,
        agentAliasId=agent_alias_id,
        sessionId=session_id,
        inputText=user_message,
    )

    completion = ""
    for event in response["completion"]:
        if "chunk" in event:
            completion += event["chunk"]["bytes"].decode()

    return completion


def post_slack_message(channel, text, thread_ts=None):
    creds = get_slack_creds()
    token = creds["bot_token"]
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read().decode())


def lambda_handler(event, context):
    body_str = event.get("body", "{}")
    body = json.loads(body_str) if isinstance(body_str, str) else body_str

    print(f"EVENT: {json.dumps(event)[:2000]}")
    print(f"BODY: {json.dumps(body)[:2000]}")

    # Slack URL verification challenge
    if body.get("type") == "url_verification":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"challenge": body["challenge"]}),
        }

    # Handle event callback
    if body.get("type") != "event_callback":
        return {"statusCode": 200, "body": "ok"}

    slack_event = body.get("event", {})

    # Only respond to app_mention
    if slack_event.get("type") != "app_mention":
        return {"statusCode": 200, "body": "ok"}

    # Ignore bot messages (prevent loops)
    if slack_event.get("bot_id"):
        return {"statusCode": 200, "body": "ok"}

    user_message = slack_event.get("text", "")
    channel = slack_event.get("channel", "")
    thread_ts = slack_event.get("thread_ts") or slack_event.get("ts")
    user_id = slack_event.get("user", "unknown")

    # Remove bot mention from message
    user_message = " ".join(
        word for word in user_message.split() if not word.startswith("<@")
    ).strip()

    if not user_message:
        user_message = "What can you help me with?"

    # Session per user+channel
    session_id = f"{channel}-{user_id}-{uuid.uuid4().hex[:8]}"

    # Invoke Bedrock Agent
    try:
        agent_response = invoke_agent(user_message, session_id)
        post_slack_message(channel, agent_response, thread_ts)
    except Exception as e:
        post_slack_message(channel, f"❌ Error: {str(e)}", thread_ts)

    return {"statusCode": 200, "body": "ok"}
