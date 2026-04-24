# Certificate Management Agent

An intelligent Certificate Management Agent deployed on Amazon Bedrock AgentCore that automates end-to-end certificate lifecycle management across AWS (ACM, Private CA), external CAs, Kubernetes, EC2, on-premises PKI, IoT devices, and multi-cloud environments.

## Problem

AWS Certificate Manager (ACM) has significant limitations:
- No support for certificates on EC2 instances directly
- No export of private keys for public certificates
- No proactive alerting built in
- No centralized dashboard across accounts/regions
- Cannot issue short-lived certificates
- Imported certificates are not auto-renewed
- Regional scope requires per-region provisioning

This agent overcomes all of these limitations and extends certificate management beyond AWS.

## Features

- **Certificate Discovery** — Scan all accounts/regions, aggregate cert metadata (ACM + imported + external + K8s + EC2 + IoT)
- **Expiration Monitoring** — Proactive alerts with configurable thresholds (90/60/30/14/7 days)
- **Auto-Renewal** — Trigger renewal workflows for ACM, imported, Kubernetes, EC2, and external CA certificates
- **Rotation Management** — Handle frequent rotations for the shift to 47-day max cert lifetimes by March 2029
- **Compliance Reporting** — Generate audit-ready reports on cert authority, key strength, expiry status
- **Policy Enforcement** — Flag wildcards, weak key sizes, untrusted CAs, missing CT logs
- **Incident Triage** — Map expired certs to affected services/endpoints/load balancers
- **Cross-Cloud Support** — Kubernetes cert-manager, on-premises PKI, Azure, GCP
- **Cost Optimization** — Identify unused Private CAs, recommend cost savings
- **Conversational Chat** — Natural language interface powered by Amazon Bedrock
- **Health Dashboard** — Centralized web UI for real-time certificate posture

## Architecture

- **Runtime**: Amazon Bedrock AgentCore (auto-scaling, microVM isolation)
- **Data Store**: Amazon DynamoDB (Certificate Inventory)
- **Workflows**: AWS Step Functions + Lambda
- **Scheduling**: Amazon EventBridge
- **Chat Interface**: AgentCore + Amazon Bedrock foundation models
- **Dashboard**: Web UI via API Gateway + CloudFront
- **Auth**: AgentCore Identity (OAuth) + Cognito / IAM Identity Center
- **IaC**: AWS CDK

## Project Structure

```
certificate-management/
├── .kiro/                    # Shared Kiro configuration
│   ├── steering/             # Team conventions (auto-loaded)
│   ├── settings/             # Shared MCP tool configs
│   ├── hooks/                # Shared automation hooks
│   └── specs/                # Feature specs and requirements
├── src/                      # Application source code
│   ├── discovery/            # Certificate discovery scanners
│   ├── monitoring/           # Expiration monitoring and alerting
│   ├── renewal/              # Automated renewal workflows
│   ├── rotation/             # Certificate rotation management
│   ├── compliance/           # Compliance reporting
│   ├── policy/               # Policy enforcement engine
│   ├── triage/               # Incident triage engine
│   ├── dashboard/            # Health dashboard
│   ├── chat/                 # Conversational chat interface
│   ├── cost/                 # Cost optimization analyzer
│   └── common/               # Shared utilities and models
├── infra/                    # AWS CDK infrastructure code
├── tests/                    # Test suites
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── docs/                     # Additional documentation
└── scripts/                  # Utility scripts
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+ (for CDK)
- AWS CDK CLI (`npm install -g aws-cdk`)
- AWS CLI configured with appropriate credentials

### Setup

```bash
git clone https://github.com/gopmudiy/certificate-management.git
cd certificate-management

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Running Tests

```bash
pytest --cov=src --cov-report=html
```

### Deploying

```bash
cdk synth
cdk deploy --context env=dev
```

## Collaboration

This project uses [Kiro](https://kiro.dev) for AI-assisted development. The `.kiro/` directory contains shared configuration that every collaborator gets automatically:

| What | How it works |
|------|-------------|
| Steering rules | `.kiro/steering/*.md` files load into every Kiro session |
| Hooks | `.kiro/hooks/*.json` trigger on configured events |
| MCP servers | `.kiro/settings/mcp.json` connects shared tools |
| Specs | `.kiro/specs/` provides shared feature plans |

Just clone the repo and open in Kiro — zero manual configuration needed.

## License

Apache-2.0
