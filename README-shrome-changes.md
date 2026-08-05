# Changes Made — CertAgent Workshop Setup

## Summary

Set up the CertAgent project with mock data support, deployed Lambda infrastructure via SAM, and deployed the conversational agent on Amazon Bedrock AgentCore.

## Files Added

| File | Purpose |
|------|---------|
| `CertAgent/` | AgentCore project (created via `agentcore create`) |
| `CertAgent/app/CertAgent/main.py` | Agent code with Lambda tools (scan, renew, status, download, inventory) |
| `CertAgent/app/CertAgent/pyproject.toml` | Python dependencies for the agent |
| `CertAgent/agentcore/agentcore.json` | AgentCore project config |
| `CertAgent/agentcore/aws-targets.json` | Deployment target (account + region) |
| `CertAgent/agentcore/.env.local` | Local environment variables (gitignored) |
| `agentcore/agentcore.json` | Initial config attempt (can be removed — superseded by CertAgent/) |
| `agentcore/aws-targets.json` | Initial config attempt (can be removed — superseded by CertAgent/) |
| `agentcore/.env.local` | Initial config attempt (can be removed — superseded by CertAgent/) |
| `app/CertAgent/main.py` | Initial agent code attempt (can be removed — superseded by CertAgent/) |
| `app/CertAgent/pyproject.toml` | Initial dependencies attempt (can be removed — superseded by CertAgent/) |
| `README.md` | Full project documentation with setup instructions |
| `README-shrome-changes.md` | This file |

## Files Modified

| File | Change |
|------|--------|
| `lambdas/scan_certificates/handler.py` | Added `generate_mock_certificates()` function and `use_mock` flag support |
| `lambdas/renew_certificate/handler.py` | Added `mock_renewal()`, `is_mock_order()` auto-detection, and `use_mock` flag support |
| `.gitignore` | Added `agentcore/.env.local` |

## Files That Can Be Cleaned Up

The following were created before we used `agentcore create` and are now superseded by the `CertAgent/` directory:

- `agentcore/` (top-level)
- `app/` (top-level)

## Deployment Steps Performed

1. `sam build && sam deploy --guided` — Deployed Lambda functions, DynamoDB, SNS, EventBridge
2. `aws secretsmanager put-secret-value` — Stored DigiCert API key
3. `agentcore create` — Scaffolded AgentCore project
4. `agentcore deploy` — Deployed agent to AgentCore Runtime
5. `aws iam put-role-policy` — Granted agent Lambda invoke permissions

## Key Configuration

- **AWS Region**: us-east-1
- **SAM Stack Name**: sam-app
- **AgentCore Agent**: CertAgent
- **Mock mode**: Enabled by default (set `use_mock=False` for production)
- **DigiCert API key**: Stored in `/certagent/digicert-api-key` (Secrets Manager)
