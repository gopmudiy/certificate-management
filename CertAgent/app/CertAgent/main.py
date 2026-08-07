"""
CertAgent — AgentCore Runtime Entry Point

This agent uses Strands Agent SDK to provide conversational certificate
lifecycle management. It connects to the Lambda functions deployed by
the workshop CloudFormation stack via the AgentCore Gateway.
"""

import os
import json
import boto3
from strands import Agent
from strands.models.bedrock import BedrockModel

# Load Lambda function names from environment
LAMBDA_SCAN      = os.environ.get('LAMBDA_SCAN', 'certagent-scan-certificates')
LAMBDA_RENEW     = os.environ.get('LAMBDA_RENEW', 'certagent-renew-certificate')
LAMBDA_STATUS    = os.environ.get('LAMBDA_STATUS', 'certagent-check-status')
LAMBDA_DOWNLOAD  = os.environ.get('LAMBDA_DOWNLOAD', 'certagent-download-certificate')
LAMBDA_STORE     = os.environ.get('LAMBDA_STORE', 'certagent-store-certificate')
LAMBDA_INVENTORY = os.environ.get('LAMBDA_INVENTORY', 'certagent-list-inventory')
AWS_REGION       = os.environ.get('AWS_REGION', 'us-east-1')

lambda_client = boto3.client('lambda', region_name=AWS_REGION)

SYSTEM_PROMPT = """You are CertAgent, an AI operations agent that manages TLS/SSL certificate lifecycle through DigiCert CertCentral.

Your capabilities:
1. SCAN - List all certificates and identify those expiring soon
2. RENEW - Generate a new CSR and submit renewal requests to DigiCert
3. CHECK STATUS - Monitor the status of pending renewals
4. DOWNLOAD - Retrieve issued certificates from DigiCert
5. STORE - Save certificates and private keys securely in AWS Secrets Manager
6. INVENTORY - View the full certificate inventory and renewal history

Rules:
- Always confirm with the user before renewing PRODUCTION certificates
- When scanning, always report: domain, days remaining, priority level, and cert type
- When a renewal fails, explain the likely cause and suggest remediation
- Never expose private keys in responses — only confirm they are stored
- Prioritize certificates by urgency: EXPIRED > CRITICAL (<7d) > HIGH (<14d) > MEDIUM (<30d)
- Use mock mode (use_mock=true) unless the user explicitly requests production mode

Response format:
- Be concise and operational
- Use tables for listing multiple certificates
- Use emoji for priority: 💀 Expired, 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- After any action, state what was done and what happens next
"""


def invoke_lambda(function_name: str, payload: dict) -> dict:
    """Invoke a Lambda function and return the response body."""
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )
    result = json.loads(response['Payload'].read())
    if 'FunctionError' in response:
        return {'error': result.get('errorMessage', str(result))}
    return result.get('body', result)


# ── Tool definitions ─────────────────────────────────────────────────────────

def scan_certificates(threshold_days: int = 30, use_mock: bool = True) -> str:
    """Scan for certificates expiring within the given threshold days.
    
    Args:
        threshold_days: Number of days to look ahead for expiring certs
        use_mock: If True, use mock data instead of calling DigiCert API
    """
    result = invoke_lambda(LAMBDA_SCAN, {
        'threshold_days': threshold_days,
        'use_mock': use_mock
    })
    return json.dumps(result, indent=2, default=str)


def renew_certificate(order_id: str, common_name: str, sans: str = "", use_mock: bool = True) -> str:
    """Renew a specific certificate by order ID.
    
    Args:
        order_id: The DigiCert order ID to renew
        common_name: The domain name of the certificate
        sans: Comma-separated Subject Alternative Names
        use_mock: If True, simulate the renewal without calling DigiCert
    """
    sans_list = [s.strip() for s in sans.split(',') if s.strip()] if sans else [common_name]
    result = invoke_lambda(LAMBDA_RENEW, {
        'order_id': order_id,
        'common_name': common_name,
        'sans': sans_list,
        'use_mock': use_mock
    })
    return json.dumps(result, indent=2, default=str)


def check_status(order_id: str) -> str:
    """Check the renewal status of a certificate order.
    
    Args:
        order_id: The DigiCert order ID to check
    """
    result = invoke_lambda(LAMBDA_STATUS, {'order_id': order_id})
    return json.dumps(result, indent=2, default=str)


def list_inventory(status: str = "all") -> str:
    """List the certificate inventory with optional status filter.
    
    Args:
        status: Filter by status: all, pending, submitted, issued, completed
    """
    result = invoke_lambda(LAMBDA_INVENTORY, {'status': status})
    return json.dumps(result, indent=2, default=str)


# ── Agent setup ──────────────────────────────────────────────────────────────

model = BedrockModel(
    model_id="anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name=AWS_REGION
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[scan_certificates, renew_certificate, check_status, list_inventory]
)


def handler(event, context=None):
    """AgentCore runtime handler — receives invocation events."""
    input_text = event.get('inputText', event.get('prompt', ''))
    if not input_text:
        return {'output': 'Please provide a message.'}
    
    response = agent(input_text)
    return {'output': str(response)}


if __name__ == '__main__':
    # Local testing
    import sys
    prompt = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else 'What certs are expiring soon?'
    result = handler({'inputText': prompt})
    print(result['output'])
