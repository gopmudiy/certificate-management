# CertAgent 🤖🔐

AI-powered DigiCert certificate auto-renewal agent built on Amazon Bedrock.

## Overview

CertAgent automates TLS/SSL certificate lifecycle management for organizations using DigiCert CertCentral. It uses an Amazon Bedrock Agent (Claude) to provide conversational certificate management — scan for expiring certs, renew them, and store the results securely.

## Architecture

```
User (Slack/CLI) → Bedrock Agent (Claude) → Action Groups (Lambda) → DigiCert API
                                                    ↓
                                          Secrets Manager (keys/certs)
                                          DynamoDB (inventory)
                                          SNS (notifications)
```

## Features

- 🔍 **Scan** — Discover all certificates expiring within N days
- 🔄 **Renew** — Auto-generate CSR and submit renewal to DigiCert
- 📥 **Download** — Retrieve issued certs and store in Secrets Manager
- 📊 **Inventory** — Track all certs, renewal history, and status
- ⏰ **Proactive** — Daily EventBridge scan with SNS/Slack alerts
- 🤖 **Conversational** — Natural language interaction via Bedrock Agent

## Prerequisites

- AWS SAM CLI
- DigiCert CertCentral account with API access
- Python 3.12+

## Deployment

```bash
# Build
sam build

# Deploy (guided first time)
sam deploy --guided

# Update DigiCert API key in Secrets Manager
aws secretsmanager put-secret-value \
  --secret-id /certagent/digicert-api-key \
  --secret-string '{"api_key": "YOUR_DIGICERT_API_KEY"}'
```

## Usage

### Via Bedrock Agent (conversational)
```
"What certs are expiring in the next 14 days?"
"Renew the cert for *.ccs.fico.com"
"Show me the renewal history for api.dmp.fico.com"
```

### Via EventBridge (automated)
Daily scan runs at 8 AM UTC. Sends SNS notification if any certs are expiring within the configured threshold (default: 30 days).

### Via Lambda (direct)
```bash
aws lambda invoke --function-name certagent-scan-certificates \
  --payload '{"threshold_days": 14}' output.json
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| ExpiryThresholdDays | 30 | Alert when certs expire within this many days |
| DigiCertBaseUrl | https://www.digicert.com/services/v2 | DigiCert API endpoint |

## Security

- DigiCert API key stored in Secrets Manager (encrypted at rest)
- Private keys generated in Lambda, immediately stored in Secrets Manager
- Private keys never logged or returned in API responses
- IAM least-privilege policies per Lambda function
- DynamoDB encryption at rest enabled by default

## Priority Levels

| Priority | Days Remaining | Action |
|----------|---------------|--------|
| 💀 EXPIRED | ≤ 0 | Immediate manual intervention |
| 🔴 CRITICAL | 1-7 | Auto-renew immediately |
| 🟠 HIGH | 8-14 | Auto-renew with notification |
| 🟡 MEDIUM | 15-30 | Notify, schedule renewal |
| 🟢 LOW | 31+ | Monitor only |

## Author

Shreyas Adhiya — AWS Technical Account Manager
