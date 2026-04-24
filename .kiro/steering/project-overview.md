# Certificate Management Agent — Project Overview

This project builds an intelligent Certificate Management Agent deployed on Amazon Bedrock AgentCore. The agent automates end-to-end certificate lifecycle management across AWS (ACM, Private CA), external CAs, Kubernetes, EC2, on-premises PKI, IoT devices, and multi-cloud environments.

## Key Context

- As of February 2026, ACM public certificates have a max validity of 198 days.
- As of March 15, 2029, the max lifetime for a public TLS certificate will be less than 47 days.
- The agent compensates for known ACM limitations (no EC2 support, no export of public cert keys, no proactive alerting, no centralized dashboard, no short-lived certs, etc.).
- The agent is deployed on Amazon Bedrock AgentCore (Runtime, Memory, Identity, Gateway, Observability).

## Architecture Summary

- **Runtime**: Amazon Bedrock AgentCore (auto-scaling, microVM isolation)
- **Data Store**: Amazon DynamoDB (Certificate Inventory)
- **Workflows**: AWS Step Functions + Lambda
- **Scheduling**: Amazon EventBridge
- **Chat Interface**: AgentCore + Amazon Bedrock foundation models
- **Dashboard**: Web UI via API Gateway + CloudFront
- **Auth**: AgentCore Identity (OAuth) + Cognito / IAM Identity Center

## Spec Location

All requirements, design, and task documents are in `.kiro/specs/certificate-management-agent/`.
