# CertAgent Workshop

AI-powered TLS/SSL certificate lifecycle management built on Amazon Bedrock, Lambda, and DynamoDB.

## Deployment

### Workshop Studio (automatic)

This template is designed for **AWS Workshop Studio** — it deploys automatically when a participant account is provisioned.

- **Template:** `infra/workshop-account-setup.yaml`
- Creates: VPC, Lambda functions, DynamoDB, SNS, EventBridge, Secrets Manager, SageMaker Domain + Space
- The JupyterLab space lifecycle config auto-clones this repo and configures the notebooks
- Participants open Studio, launch the space, and start labs immediately — zero setup

To configure in Workshop Studio:
1. Set `infra/workshop-account-setup.yaml` as the account provisioning template
2. The SAM transform requires `CAPABILITY_IAM` and `CAPABILITY_AUTO_EXPAND`
3. No parameters needed (all defaults work)

### Manual deployment (for testing or standalone use)

```bash
# From the certificate-management/ directory:
sam build --template-file infra/workshop-account-setup.yaml

sam deploy \
  --template-file infra/workshop-account-setup.yaml \
  --stack-name certagent-workshop \
  --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
  --resolve-s3
```

### What happens on deploy

1. **VPC** created with 2 public subnets + internet gateway
2. **7 Lambda functions** deployed via SAM from `lambdas/` source
3. **DynamoDB** table + **SNS** topic + **EventBridge** daily scan rule created
4. **Secrets Manager** seeded with a placeholder DigiCert API key (mock mode)
5. **12 SSM parameters** written under `/workshop/certagent/`
6. **SageMaker Domain** + UserProfile + JupyterLab Space created
7. On space start, **lifecycle config** runs:
   - Installs Python dependencies
   - `git clone`s this repo into `~/certagent-workshop/`
   - Reads SSM → writes `/tmp/certagent_config.json`
   - Creates `~/certagent-notebooks/` symlink

### Participant experience

1. Open the SageMaker Studio URL from stack outputs
2. Launch the **certagent-lab** space (auto-starts lifecycle config)
3. Open `certagent-notebooks/01_explore_lambdas.ipynb`
4. Start the labs — everything is already deployed

## Workshop Labs

| Lab | Notebook | What you do |
|-----|----------|-------------|
| 01 | `01_explore_lambdas.ipynb` | Invoke Lambda functions with mock data, inspect DynamoDB |
| 02 | `02_certificate_lifecycle.ipynb` | Full scan -> renew -> status -> inventory flow |
| 03 | `03_bedrock_agent.ipynb` | Create Bedrock Agent, have conversations |
| 04 | `04_proactive_monitoring.ipynb` | EventBridge, SNS alerts, agent-mode scan |
| 05 | `05_cleanup.ipynb` | Delete the Bedrock Agent and secrets |

All labs use **mock mode** by default — no DigiCert account required.

## Architecture

```
EventBridge (daily cron)
     │
     ▼
Lambda: scan-certificates ──► DigiCert API (or mock)
     │
     ├──► DynamoDB (certagent-inventory)
     ├──► SNS (email alert)
     └──► Bedrock Agent (intelligent briefing)
              │
              ├──► Lambda: renew-certificate
              ├──► Lambda: check-status
              ├──► Lambda: download-certificate
              ├──► Lambda: store-certificate
              └──► Lambda: list-inventory
                        │
                        ▼
              Secrets Manager (private keys + cert chains)
```

## Repository Structure

```
certificate-management/
├── infra/
│   ├── workshop-account-setup.yaml   <-- THE template (Workshop Studio auto-deploy)
│   ├── workshop-master.yaml          Nested stack alternative (manual deploy)
│   ├── workshop-infra.yaml           App infra only (for nested approach)
│   └── sagemaker-domain.yaml         SageMaker only (for nested approach)
├── notebooks/                        Workshop lab notebooks (5 labs)
├── lambdas/                          Lambda function source code
│   ├── scan_certificates/
│   ├── renew_certificate/
│   ├── check_status/
│   ├── download_certificate/
│   ├── store_certificate/
│   └── list_inventory/
├── agent/                            Bedrock Agent configuration
│   ├── agent_instruction.txt         System prompt
│   └── api_schema.yaml               OpenAPI action group schema
├── slack/                            Slack integration handler
└── scripts/                          Helper scripts
```

## Cleanup

1. Run `05_cleanup.ipynb` to delete the Bedrock Agent and secrets created during labs
2. Delete the CloudFormation stack (done automatically by Workshop Studio at event end):
   ```bash
   aws cloudformation delete-stack --stack-name certagent-workshop
   ```
   This removes the VPC, Lambda, DynamoDB, SageMaker domain — everything.

## Configuration

All infrastructure outputs are stored in SSM Parameter Store under `/workshop/certagent/`.
The SageMaker lifecycle script reads these at space startup and writes `/tmp/certagent_config.json`,
which every notebook loads in its first cell.

| SSM Parameter | Value |
|--------------|-------|
| `/workshop/certagent/region` | AWS region |
| `/workshop/certagent/cert-table-name` | DynamoDB table name |
| `/workshop/certagent/lambda-scan` | Scan Lambda function name |
| `/workshop/certagent/lambda-renew` | Renew Lambda function name |
| `/workshop/certagent/lambda-status` | Status Lambda function name |
| `/workshop/certagent/sns-topic-arn` | SNS notification topic ARN |
| `/workshop/certagent/cert-secrets-prefix` | Secrets Manager path prefix |
