# Requirements Document

## Introduction

The Certificate Management Agent is an intelligent orchestration system designed to automate and simplify the end-to-end lifecycle management of TLS/SSL certificates across AWS accounts, regions, and hybrid/multi-cloud environments. It addresses critical pain points including manual renewal processes, lack of centralized visibility, expiration-related outages, compliance gaps, and the operational complexity of managing certificates at scale. The agent integrates with AWS Certificate Manager (ACM), AWS Private CA, external Certificate Authorities, Kubernetes cert-manager, and on-premises PKI infrastructure.

The Agent is specifically designed to compensate for known ACM limitations and drawbacks, providing automation, visibility, and management capabilities that ACM does not natively offer. It extends certificate management beyond ACM to cover external CAs, Kubernetes, EC2 instances, IoT devices, code signing, and on-premises infrastructure.

Key industry context:
- As of February 2026, ACM public certificates have a maximum validity of 198 days.
- As of March 15, 2029, the maximum lifetime for a public TLS certificate will be less than 47 days.
- These shortened lifetimes make automated certificate management essential.

## Requirements Summary

| # | Requirement | Summary |
|---|-------------|---------|
| 1A | ACM-Managed Certificate Inventory and Discovery | Discover and inventory all ACM-issued (public and private) and imported certificates across all AWS accounts and regions. Track ACM-specific metadata like ARNs, validation status, renewal eligibility, and resource associations. |
| 1B | Non-ACM Certificate Inventory and Discovery | Discover and inventory certificates outside ACM — EC2 instances, Kubernetes (cert-manager), external CAs (DigiCert, Let's Encrypt, Venafi), on-premises PKI, IoT devices, and other cloud providers (Azure, GCP). Normalize all into a unified inventory. |
| 2A | ACM Certificate Expiration Monitoring and Alerting | Monitor ACM-managed certificates (public, private, imported) for upcoming expirations. Flag certificates ineligible for auto-renewal (unattached, imported). Multi-channel alerts with renewal eligibility status. |
| 2B | Non-ACM Certificate Expiration Monitoring and Alerting | Monitor non-ACM certificates (EC2, Kubernetes, external CA, on-premises, IoT, other cloud) for upcoming expirations. Include source-specific context (instance ID, pod name, file path) and whether automated renewal is configured. |
| 3A | ACM Certificate Automated Renewal and Remediation | Pre-validate ACM renewal conditions (DNS records, SLR, Private CA status, resource association). Remediate DNS validation issues. Coordinate imported cert renewal via External CA APIs. Handle CloudFront us-east-1 requirement. |
| 3B | Non-ACM Certificate Automated Renewal and Deployment | Auto-renew and deploy certificates on EC2 (via SSM), Kubernetes (via cert-manager API), external CAs (via API/ACME/Lambda), on-premises (via connector plugins), IoT Core, and other cloud providers. Service restart/reload on deployment. |
| 4A | ACM Certificate Rotation Management | Manage rotation schedules for ACM certificates. Adapt to shortened public cert lifetimes (47-day max by March 2029). Handle pinning-sensitive certs. Coordinate imported cert rotation with External CAs. |
| 4B | Non-ACM Certificate Rotation Management | Manage rotation schedules for EC2, Kubernetes, external CA, on-premises, and IoT certificates. Support 24-hour rotation for short-lived certs. Zero-downtime deployment with rollback on failure. |
| 5 | Compliance Reporting | Generate audit-ready reports (PDF, CSV, JSON) on certificate posture — key strength, issuer, expiry status, policy compliance. Scheduled generation with filtering by account, region, source type, and cert type. |
| 6 | Policy Enforcement | Evaluate certificates against configurable policies: minimum key size, allowed CAs, wildcard restrictions, CT log presence, max lifetime. Flag violations and alert on critical non-compliance. |
| 7A | Incident Triage for ACM Certificate Failures | Map expired/failing ACM certificates to affected AWS services (ELBs, CloudFront, API Gateway). Resolve dependency chains to end-user endpoints. Blast radius report with ACM-specific remediation steps within 60 seconds. |
| 7B | Incident Triage for Non-ACM Certificate Failures | Map expired/failing non-ACM certificates to affected EC2 instances, Kubernetes pods/ingresses, on-premises endpoints, and IoT devices. Source-specific remediation steps (SSM commands, kubectl, connector actions). |
| 8 | Cross-Cloud and Hybrid Certificate Management | Manage certificates across Kubernetes, EC2, on-premises PKI, external CAs, IoT Core, and other cloud providers. Unified lifecycle management with deployment, service restart, and renewal across all targets. |
| 9 | Imported Certificate Management | Automate lifecycle of imported ACM certificates — integrate with external CA APIs or Lambda-based connectors for renewal, re-import renewed certs, and verify resource association. Eliminate manual renewal. |
| 10 | Cost Optimization | Identify unused Private CAs and unattached ACM certificates. Calculate monthly costs, project annual savings, and recommend deactivation/deletion after verifying no active certs depend on the resource. |
| 11 | Validation Management and DNS Remediation | Manage DNS/email validation for ACM certificates. Auto-create CNAME records in Route 53, send clear instructions for non-Route 53 DNS, diagnose validation failures, and recommend migration from email to DNS validation. |
| 12 | Multi-Account and Cross-Region Orchestration | Operate across multiple AWS accounts and regions via IAM role assumption. Support AWS Organizations auto-discovery, cross-region provisioning (us-east-1 for CloudFront), and RAM-based Private CA sharing. |
| 13 | Agent Deployment on Amazon Bedrock AgentCore | Deploy on AgentCore Runtime with auto-scaling and microVM isolation. Leverage AgentCore Memory, Identity (OAuth), Gateway (tools/MCP), Observability (CloudWatch/OTEL), and Code Interpreter. DynamoDB for inventory, Lambda/Step Functions for workflows, EventBridge for scheduling. |
| 14 | SLR and IAM Misconfiguration Detection | Proactively detect ACM Service-Linked Role issues, missing Route 53 permissions, and cross-account Private CA sharing misconfigurations. Alert with specific remediation steps before renewal failures occur. |
| 15 | Certificate Type Support Beyond TLS | Manage non-TLS certificates from Private CA and external sources: S/MIME (email encryption), code signing, IoT device authentication. Type-specific renewal workflows and policy rules. |
| 16 | Audit Trail and Change Tracking | Record every certificate lifecycle event (discovery, renewal, deployment, rotation, revocation) in tamper-resistant logs. Queryable by cert ID, time range, action type, or account. 365-day default retention. |
| 17 | Notification and Escalation Management | Configurable notification routing by cert tags, account, region, team. Escalation policies that increase recipients/channels as severity grows. Suppression rules for maintenance windows. |
| 18 | Certificate Health Dashboard | Centralized web UI showing real-time cert health across all accounts, regions, and sources. Drill-down views, 90-day expiration timeline, renewal workflow status, IAM health, and search/filter capabilities. |
| 19 | Certificate Revocation Management | Revoke certificates via ACM, Private CA, or external CA. Update CRLs, verify OCSP status, auto-provision replacement certificates, and deploy to affected targets. Full audit trail of revocation actions. |
| 20 | Automated Certificate Provisioning | Automate new certificate provisioning: CSR generation, CA submission (ACM, Private CA, or external CA), and deployment to target resources. End-to-end from request to deployed cert. |
| 21 | Self-Service Certificate Request Workflow | Self-service API for teams to request certificates with configurable approval gates. Enforce request policies (allowed domains, key algorithms, cert types per team). Full audit trail. |
| 22 | CI/CD Pipeline Integration | CLI and API for CI/CD pipelines to request, retrieve, and deploy certificates during releases. Support CodePipeline, CodeBuild, and webhook-based systems. Code signing cert deployment tracking. |
| 23 | Certificate Chain Validation | Validate complete certificate chains (leaf → intermediate → root). Detect broken chains, expired intermediates, and untrusted roots. Daily scheduled checks plus post-renewal/deployment validation. |
| 24 | Certificate Backup and Disaster Recovery | Back up certificate inventory metadata and exportable private keys to encrypted S3/Secrets Manager. Point-in-time recovery with configurable retention. Reconcile backups with fresh discovery on restore. |
| 25 | Rate Limiting and Throttling Awareness | Track and enforce API rate limits for ACM, Private CA, and external CAs. Queue requests approaching limits, apply exponential backoff on throttling, and prioritize renewal over discovery operations. |
| 26 | Certificate Transparency Monitoring | Monitor CT logs for unauthorized certificate issuance on organization domains. Alert on rogue/misissued certs and optionally trigger revocation. Configurable domain watch lists. |
| 27 | Secrets Management Integration | Store all private keys in Secrets Manager or SSM SecureString with KMS encryption. Enforce no-plaintext policy. Automatic KMS key rotation. Full audit trail of all private key access events. |
| 28 | Multi-Tenancy Support | Tenant isolation by account, tags, domain patterns, or org unit. Tenant-scoped access controls, notification routing, policies, and reports. Global admin role for org-wide visibility. |
| 29 | Conversational Chat Interface | Natural language chat UI (embedded in dashboard + standalone) for querying cert status, triggering actions, and getting recommendations. Powered by Amazon Bedrock on AgentCore with conversation memory, OAuth auth, and confirmation gates for destructive actions. |

## Requirements

### Requirement 1A: ACM-Managed Certificate Inventory and Discovery

**User Story:** As a cloud operations engineer, I want the Agent to automatically discover and inventory all ACM-managed certificates (ACM-issued public, ACM-issued private via Private CA, and imported certificates) across my AWS accounts and regions, so that I have complete visibility into my AWS certificate estate.

#### Acceptance Criteria

1. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL enumerate all ACM-issued public certificates across all configured AWS accounts and regions and store the metadata in the Certificate_Inventory.
2. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL enumerate all ACM-issued private certificates (issued via Private_CA through ACM) across all configured AWS accounts and regions and store the metadata in the Certificate_Inventory.
3. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL enumerate all imported certificates in ACM across all configured AWS accounts and regions and store the metadata in the Certificate_Inventory, tagging each as "imported" with the originating External_CA if known.
4. FOR each ACM-managed certificate, THE Certificate_Inventory SHALL store: domain name, Subject Alternative Names (SANs), issuer, serial number, key algorithm, key size, validity start date, expiration date, validation method (DNS or email), validation status, associated AWS resources (ELB, CloudFront, API Gateway, etc.), source account, source region, ACM certificate ARN, renewal eligibility status, and whether the certificate is ACM-issued or imported.
5. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL identify ACM certificates that are NOT associated with any AWS resource and tag the certificates as "unattached" in the Certificate_Inventory.
6. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL identify the issuing Private_CA for each ACM-issued private certificate and record the Private_CA ARN, Private_CA status (Active, Disabled, Deleted), and whether the Private_CA is shared via RAM from another account.
7. THE Discovery_Scanner SHALL support configurable scan schedules with a minimum granularity of one hour.
8. WHEN a discovery scan completes, THE Agent SHALL generate a summary report for ACM-managed certificates containing: total ACM-issued public certificates, total ACM-issued private certificates, total imported certificates, certificates grouped by account and region, unattached certificates, and certificates with renewal eligibility issues.
9. IF a discovery scan fails for a specific account or region, THEN THE Agent SHALL log the failure with the account identifier and region, continue scanning remaining targets, and include the failure in the scan summary report.
10. WHEN a new ACM-managed certificate is discovered that does not exist in the Certificate_Inventory, THE Agent SHALL record the certificate and tag the certificate as newly discovered.

### Requirement 1B: Non-ACM Certificate Inventory and Discovery

**User Story:** As a multi-cloud platform engineer, I want the Agent to automatically discover and inventory all certificates managed outside of ACM — including certificates on EC2 instances, Kubernetes clusters, on-premises infrastructure, external CA platforms, IoT devices, and other cloud providers — so that I have unified visibility across my entire certificate estate beyond ACM.

#### Acceptance Criteria

1. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover certificates installed on configured EC2 instances by scanning configured file paths (such as /etc/ssl/certs, /etc/pki/tls, /etc/nginx/ssl, /etc/apache2/ssl) or querying an installed host agent via SSM Run Command.
2. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover certificates managed by Kubernetes cert-manager in all configured Kubernetes clusters via the Kubernetes API and store the metadata in the Certificate_Inventory.
3. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover certificates from configured External_CA platforms (DigiCert CertCentral, Let's Encrypt, Venafi Trust Protection Platform) using their respective APIs.
4. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover certificates from configured on-premises PKI systems and certificate stores through configurable connector plugins that implement a standard discovery interface.
5. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover IoT device certificates registered in AWS IoT Core and certificates issued by Private_CA for IoT device authentication.
6. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover certificates from other cloud providers (Azure Key Vault, Google Cloud Certificate Manager) through configurable cloud connector plugins.
7. WHEN a discovery scan is initiated, THE Discovery_Scanner SHALL discover non-TLS certificates including S/MIME email encryption certificates, code signing certificates, and mutual TLS (mTLS) client certificates from configured sources.
8. FOR each non-ACM certificate, THE Certificate_Inventory SHALL store: domain name or subject, Subject Alternative Names (SANs), issuer, serial number, key algorithm, key size, validity start date, expiration date, certificate type (TLS, S/MIME, code signing, IoT device, mTLS client), certificate source type (EC2, Kubernetes, External_CA, on-premises, IoT Core, other cloud), deployment target details (instance ID, pod name, file path, endpoint), and the External_CA or PKI system that issued the certificate.
9. THE Agent SHALL normalize certificate metadata from all non-ACM Certificate_Source types into the same unified schema used for ACM certificates in the Certificate_Inventory, enabling cross-source queries and reporting.
10. THE Discovery_Scanner SHALL support configurable scan schedules for non-ACM sources with a minimum granularity of one hour, independently configurable from ACM scan schedules.
11. WHEN a discovery scan completes, THE Agent SHALL generate a summary report for non-ACM certificates containing: total certificates grouped by source type (EC2, Kubernetes, External_CA, on-premises, IoT, other cloud), certificates by certificate type, and certificates by issuing CA.
12. IF a non-ACM Certificate_Source is unreachable during a discovery scan (EC2 instance offline, Kubernetes cluster unreachable, External_CA API unavailable), THEN THE Agent SHALL log the connectivity failure with the source identifier and reason, use the last known certificate data for that source, continue scanning remaining targets, and send a warning notification.
13. WHEN a new non-ACM certificate is discovered that does not exist in the Certificate_Inventory, THE Agent SHALL record the certificate and tag the certificate as newly discovered.

### Requirement 2A: ACM Certificate Expiration Monitoring and Alerting

**User Story:** As a platform reliability engineer, I want the Agent to proactively alert me about upcoming ACM certificate expirations and flag certificates that are not eligible for auto-renewal, so that I can prevent outages caused by expired ACM certificates.

#### Acceptance Criteria

1. THE Agent SHALL evaluate all ACM-managed certificates (ACM-issued public, ACM-issued private, and imported) in the Certificate_Inventory against configured Alert_Threshold values on a daily basis.
2. THE Agent SHALL support configurable Alert_Threshold values, with default thresholds at 90, 60, 30, 14, and 7 days before expiration.
3. WHEN an ACM certificate's remaining validity falls below a configured Alert_Threshold, THE Agent SHALL send a notification containing the certificate domain name, ACM ARN, expiration date, days remaining, issuer, associated AWS resources, source account/region, and renewal eligibility status (auto-renewable, requires manual action, or imported-no-auto-renewal).
4. THE Agent SHALL support notification delivery via Amazon SNS, email, Slack webhook, PagerDuty, Microsoft Teams webhook, and Amazon EventBridge.
5. WHEN an ACM-issued certificate is approaching expiration but is NOT associated with any AWS resource, THE Agent SHALL flag the certificate as ineligible for auto-renewal and include this in the alert.
6. WHEN an imported certificate in ACM is approaching expiration, THE Agent SHALL include in the alert that ACM does not auto-renew imported certificates and indicate whether an External_CA integration is configured for automated renewal.
7. THE Agent SHALL escalate notification severity as expiration approaches: informational at 90 days, warning at 30 days, critical at 7 days, and emergency at 1 day.
8. IF an ACM certificate has already expired, THEN THE Agent SHALL send an emergency notification and trigger the Incident_Triage_Engine for that certificate.
9. WHEN an ACM certificate is renewed or replaced, THE Agent SHALL clear all active alerts for that certificate.

### Requirement 2B: Non-ACM Certificate Expiration Monitoring and Alerting

**User Story:** As a multi-cloud platform engineer, I want the Agent to proactively alert me about upcoming expirations for certificates managed outside ACM — on EC2 instances, Kubernetes clusters, external CAs, on-premises systems, and other cloud providers — so that I can prevent outages across my entire certificate estate.

#### Acceptance Criteria

1. THE Agent SHALL evaluate all non-ACM certificates (EC2, Kubernetes, External_CA, on-premises, IoT, other cloud) in the Certificate_Inventory against configured Alert_Threshold values on a daily basis.
2. THE Agent SHALL support configurable Alert_Threshold values per certificate source type, with default thresholds at 90, 60, 30, 14, and 7 days before expiration.
3. WHEN a non-ACM certificate's remaining validity falls below a configured Alert_Threshold, THE Agent SHALL send a notification containing the certificate domain name, expiration date, days remaining, issuer, certificate source type, deployment target details (instance ID, pod name, file path, endpoint), and whether an automated renewal integration is configured.
4. THE Agent SHALL support notification delivery via Amazon SNS, email, Slack webhook, PagerDuty, Microsoft Teams webhook, and Amazon EventBridge.
5. WHEN a Kubernetes cert-manager certificate is approaching expiration, THE Agent SHALL include in the alert whether cert-manager auto-renewal is configured and its current status.
6. WHEN an EC2 instance certificate is approaching expiration, THE Agent SHALL include in the alert the instance ID, certificate file path, and the service (nginx, Apache, etc.) that depends on the certificate.
7. WHEN an External_CA-managed certificate is approaching expiration, THE Agent SHALL include in the alert whether an API integration or Lambda connector is configured for automated renewal with that CA.
8. WHILE a non-ACM certificate remains below an Alert_Threshold and has not been renewed, THE Agent SHALL send reminder notifications at a configurable frequency, defaulting to once per day.
9. THE Agent SHALL escalate notification severity as expiration approaches: informational at 90 days, warning at 30 days, critical at 7 days, and emergency at 1 day.
10. IF a non-ACM certificate has already expired, THEN THE Agent SHALL send an emergency notification and trigger the Incident_Triage_Engine for that certificate.
11. WHEN a non-ACM certificate is renewed or replaced, THE Agent SHALL clear all active alerts for that certificate.

### Requirement 3A: ACM Certificate Automated Renewal and Remediation

**User Story:** As a DevOps engineer, I want the Agent to ensure ACM-managed certificates (public, private, and imported) renew successfully by pre-validating renewal conditions and remediating issues, so that ACM auto-renewal never fails silently.

#### Acceptance Criteria

1. WHEN an ACM-issued public certificate is within 45 days of expiration and is associated with a supported AWS resource, THE Agent SHALL verify that DNS validation records are present and correct.
2. IF DNS validation records are missing or incorrect for an ACM public certificate pending renewal, THEN THE Agent SHALL attempt to create or update the required CNAME records in Route 53 and log the remediation action.
3. WHEN a Private_CA-issued certificate managed by ACM is within 60 days of expiration, THE Agent SHALL verify that the issuing Private_CA is in Active state and that the certificate is associated with a supported resource.
4. IF the issuing Private_CA is not in Active state for a certificate pending renewal, THEN THE Agent SHALL send a critical alert identifying the Private_CA and the affected certificates.
5. WHEN an ACM-issued certificate is approaching expiration but is NOT associated with any supported AWS resource, THE Agent SHALL send a critical alert that auto-renewal will not occur and recommend associating the certificate with a resource or manually renewing.
6. WHEN a Private_CA-issued certificate has been exported for use on EC2 instances, IoT devices, or on-premises resources, THE Agent SHALL retrieve the renewed certificate and private key from ACM and initiate the deployment workflow to the target systems.
7. WHEN an imported certificate from an External_CA is within a configurable number of days of expiration, THE Agent SHALL invoke the configured renewal integration for that External_CA to request a new certificate, import the renewed certificate into ACM, and associate it with the same resources.
8. IF an External_CA does not provide an API for automated renewal of an imported certificate, THEN THE Agent SHALL send a notification to the certificate owner with renewal instructions, required certificate format, and ACM import steps.
9. WHEN a certificate is associated with a CloudFront distribution, THE Agent SHALL ensure the certificate is provisioned in the us-east-1 region.
10. IF a renewal or deployment action fails, THEN THE Agent SHALL retry the action up to a configurable number of times with exponential backoff, and send a critical alert if all retries are exhausted.
11. THE Agent SHALL log all ACM renewal and remediation actions with timestamps, certificate ARNs, actions taken, and outcomes in an auditable format.

### Requirement 3B: Non-ACM Certificate Automated Renewal and Deployment

**User Story:** As a multi-cloud platform engineer, I want the Agent to automatically renew and deploy certificates managed outside ACM — on EC2 instances, Kubernetes clusters, external CAs, on-premises systems, and IoT devices — so that I can eliminate manual renewal across my entire infrastructure.

#### Acceptance Criteria

1. WHEN a Kubernetes cert-manager certificate is within the configured renewal window, THE Agent SHALL trigger cert-manager renewal via the Kubernetes API and monitor the renewal status to completion.
2. IF a Kubernetes cert-manager renewal fails, THEN THE Agent SHALL send a critical alert with the failure reason, cluster name, namespace, and certificate resource name.
3. WHEN an EC2 instance certificate is within the configured renewal window, THE Agent SHALL request a renewed certificate from the configured CA (Private_CA or External_CA), deploy the certificate files to the configured paths on the instance via SSM Run Command or host agent, and restart or reload the configured service (such as nginx, Apache, or application process).
4. WHEN an External_CA-managed certificate (not imported into ACM) is within the configured renewal window, THE Agent SHALL invoke the External_CA API (DigiCert, Let's Encrypt ACME, Venafi, or custom Lambda connector) to request a renewed certificate and deploy it to the associated targets.
5. WHEN an on-premises PKI certificate is within the configured renewal window, THE Agent SHALL invoke the configured on-premises connector plugin to request renewal and coordinate deployment to the on-premises target systems.
6. WHEN an IoT device certificate registered in AWS IoT Core is within the configured renewal window, THE Agent SHALL coordinate renewal through Private_CA or the configured CA and update the IoT Core certificate registration.
7. WHEN a certificate from another cloud provider (Azure Key Vault, Google Cloud Certificate Manager) is within the configured renewal window, THE Agent SHALL invoke the configured cloud connector plugin to trigger renewal.
8. WHEN a renewed non-ACM certificate is obtained, THE Agent SHALL deploy the certificate to all associated Deployment_Target resources and verify successful deployment by checking the certificate served at the target endpoint.
9. IF a non-ACM renewal or deployment action fails, THEN THE Agent SHALL retry the action up to a configurable number of times with exponential backoff, and send a critical alert if all retries are exhausted.
10. THE Agent SHALL log all non-ACM renewal and deployment actions with timestamps, certificate identifiers, source type, deployment targets, actions taken, and outcomes in an auditable format.

### Requirement 4A: ACM Certificate Rotation Management

**User Story:** As a security engineer, I want the Agent to handle frequent rotations of ACM-managed certificates driven by shortened public certificate lifetimes, so that my organization is prepared for the industry shift to 47-day maximum certificate lifetimes by March 2029.

#### Acceptance Criteria

1. THE Agent SHALL support configurable Rotation_Schedule values for ACM-managed certificates (public, private, and imported), individually or grouped by account, region, or domain pattern.
2. WHEN a Rotation_Schedule triggers for an ACM certificate, THE Agent SHALL initiate the Renewal_Workflow regardless of the certificate's current expiration date.
3. WHEN the maximum public TLS certificate lifetime changes (198 days as of February 2026, less than 47 days as of March 2029), THE Agent SHALL adjust default rotation schedules for ACM public certificates to ensure renewal occurs before the new maximum lifetime is reached.
4. WHEN rotating an ACM certificate, THE Agent SHALL ensure the new certificate is issued, deployed to all associated AWS resources (ELB, CloudFront, API Gateway), and verified before the previous certificate is decommissioned.
5. IF an application uses certificate pinning with an ACM certificate, THEN THE Agent SHALL flag the certificate as pinning-sensitive and send a pre-rotation notification to the certificate owner at a configurable lead time before rotation.
6. THE Agent SHALL track the rotation history for each ACM certificate, including issuance date, ACM ARN, deployment date, associated resources, and decommission date.
7. WHEN rotating an imported ACM certificate, THE Agent SHALL coordinate with the External_CA integration to obtain a new certificate and re-import it into ACM before the current certificate expires.

### Requirement 4B: Non-ACM Certificate Rotation Management

**User Story:** As a multi-cloud platform engineer, I want the Agent to handle frequent rotations of certificates managed outside ACM — on EC2 instances, Kubernetes clusters, external CAs, and on-premises systems — so that all certificates across my infrastructure follow consistent rotation policies.

#### Acceptance Criteria

1. THE Agent SHALL support configurable Rotation_Schedule values for non-ACM certificates, individually or grouped by source type, deployment target, or domain pattern.
2. WHEN a Rotation_Schedule triggers for a non-ACM certificate, THE Agent SHALL initiate the appropriate Renewal_Workflow for the certificate's source type regardless of the certificate's current expiration date.
3. THE Agent SHALL support rotation frequencies as short as every 24 hours for short-lived certificate use cases on EC2 instances, Kubernetes clusters, and IoT devices.
4. WHEN rotating a Kubernetes cert-manager certificate, THE Agent SHALL trigger cert-manager to issue a new certificate and verify the new certificate is active on the ingress or service before the previous certificate expires.
5. WHEN rotating an EC2 instance certificate, THE Agent SHALL obtain a new certificate from the configured CA, deploy the certificate files to the instance, and restart or reload the dependent service with zero-downtime if the service supports graceful reload.
6. WHEN rotating an External_CA-managed certificate, THE Agent SHALL invoke the External_CA API to request a new certificate and deploy it to all associated targets.
7. WHEN rotating an on-premises or IoT device certificate, THE Agent SHALL coordinate with the configured connector plugin or IoT Core to issue and deploy the replacement certificate.
8. THE Agent SHALL track the rotation history for each non-ACM certificate, including issuance date, source type, deployment target, deployment date, and decommission date.
9. IF a non-ACM certificate rotation fails at any step (issuance, deployment, or verification), THEN THE Agent SHALL roll back to the previous certificate if possible, send a critical alert, and log the failure details.

### Requirement 5: Compliance Reporting

**User Story:** As a compliance officer, I want the Agent to generate audit-ready reports on certificate posture across my organization, so that I can demonstrate compliance with security policies and regulatory requirements.

#### Acceptance Criteria

1. THE Compliance_Reporter SHALL generate reports containing the following for each certificate: domain name, issuing Certificate Authority, key algorithm, key size, expiration status, validation method, associated resources, policy compliance status, and certificate source type (ACM-managed, imported, Kubernetes, EC2, external).
2. WHEN a compliance report is requested, THE Compliance_Reporter SHALL evaluate all certificates in the Certificate_Inventory against the configured policy rules and include pass/fail status for each rule.
3. THE Compliance_Reporter SHALL support report generation in PDF, CSV, and JSON formats.
4. THE Compliance_Reporter SHALL support scheduled report generation at configurable intervals (daily, weekly, monthly).
5. THE Compliance_Reporter SHALL include an executive summary section with aggregate statistics: total certificates, certificates by compliance status, certificates by key strength, certificates by issuer, certificates approaching expiration, and certificates by management source.
6. WHEN a compliance report is generated, THE Compliance_Reporter SHALL store the report in a configurable Amazon S3 bucket with versioning enabled.
7. THE Compliance_Reporter SHALL support filtering reports by account, region, certificate source type, compliance status, expiration window, and certificate type.

### Requirement 6: Policy Enforcement

**User Story:** As a security architect, I want the Agent to enforce certificate policies and flag non-compliant certificates, so that my organization maintains a strong security posture and adheres to internal standards.

#### Acceptance Criteria

1. THE Policy_Engine SHALL evaluate each certificate in the Certificate_Inventory against the following configurable policy rules: minimum key size, allowed key algorithms, allowed Certificate Authorities, wildcard certificate restrictions, Certificate Transparency log presence, maximum certificate lifetime, and required SANs.
2. WHEN a certificate violates a policy rule, THE Policy_Engine SHALL record the violation with the certificate identifier, the violated rule, the current value, and the expected value.
3. WHEN a certificate uses a wildcard domain, THE Policy_Engine SHALL flag the certificate as a policy finding if the wildcard policy is set to restricted.
4. WHEN a certificate uses a key size below the configured minimum (default: 2048 bits for RSA, 256 bits for ECDSA), THE Policy_Engine SHALL flag the certificate as non-compliant.
5. WHEN a certificate is issued by a Certificate Authority not in the configured trusted CA list, THE Policy_Engine SHALL flag the certificate as issued by an untrusted authority.
6. WHEN a public certificate does not have a corresponding entry in a CT_Log, THE Policy_Engine SHALL flag the certificate as missing CT log transparency.
7. IF a newly discovered certificate violates a critical policy rule, THEN THE Policy_Engine SHALL send an immediate alert to the security team.
8. THE Policy_Engine SHALL support policy rule configuration via a YAML or JSON policy definition file.
9. WHEN policy rules are updated, THE Policy_Engine SHALL re-evaluate all certificates in the Certificate_Inventory against the updated rules within one evaluation cycle.

### Requirement 7A: Incident Triage for ACM Certificate Failures

**User Story:** As an incident responder, I want the Agent to quickly map an expired or failing ACM certificate to all affected AWS services and endpoints, so that I can assess blast radius across ACM-integrated resources and prioritize remediation.

#### Acceptance Criteria

1. WHEN an expired or failing ACM certificate is identified, THE Incident_Triage_Engine SHALL map the certificate to all associated AWS resources including Elastic Load Balancers, CloudFront distributions, API Gateway endpoints, and any other ACM-integrated services.
2. WHEN an ACM incident triage is initiated, THE Incident_Triage_Engine SHALL produce a report containing: the ACM certificate ARN, domain name, expiration date, all associated AWS resources, the services and endpoints impacted, and the estimated blast radius.
3. THE Incident_Triage_Engine SHALL resolve the dependency chain from the ACM certificate to the end-user-facing endpoints, including intermediate resources such as target groups, listener rules, and CloudFront origins.
4. WHEN an ACM incident triage report is generated, THE Incident_Triage_Engine SHALL include recommended remediation steps specific to the ACM certificate type (public, private, imported) and the affected AWS services.
5. FOR imported ACM certificates, THE Incident_Triage_Engine SHALL include whether an External_CA integration is configured and whether emergency re-import is possible.
6. THE Incident_Triage_Engine SHALL complete the ACM triage mapping and produce the report within 60 seconds of initiation.
7. IF the Incident_Triage_Engine cannot determine all affected AWS resources for an ACM certificate, THEN THE Incident_Triage_Engine SHALL include a list of resources that could not be resolved and the reason for the failure.

### Requirement 7B: Incident Triage for Non-ACM Certificate Failures

**User Story:** As an incident responder, I want the Agent to quickly map an expired or failing non-ACM certificate to all affected EC2 instances, Kubernetes services, on-premises endpoints, and IoT devices, so that I can assess blast radius across my entire infrastructure and prioritize remediation.

#### Acceptance Criteria

1. WHEN an expired or failing certificate on an EC2 instance is identified, THE Incident_Triage_Engine SHALL map the certificate to the instance ID, the certificate file path, the dependent service (nginx, Apache, application), and any downstream services or load balancers that route traffic to the instance.
2. WHEN an expired or failing Kubernetes certificate is identified, THE Incident_Triage_Engine SHALL map the certificate to the cluster name, namespace, pod names, ingress resources, and services that depend on the certificate.
3. WHEN an expired or failing External_CA or on-premises certificate is identified, THE Incident_Triage_Engine SHALL map the certificate to the deployment targets, endpoints, and services that depend on the certificate based on the Certificate_Inventory metadata.
4. WHEN an expired or failing IoT device certificate is identified, THE Incident_Triage_Engine SHALL map the certificate to the IoT Core thing name, device group, and any MQTT topics or rules that depend on the device's authentication.
5. WHEN a non-ACM incident triage is initiated, THE Incident_Triage_Engine SHALL produce a report containing: the certificate details, source type, all associated deployment targets, the services and endpoints impacted, and the estimated blast radius.
6. WHEN a non-ACM incident triage report is generated, THE Incident_Triage_Engine SHALL include recommended remediation steps specific to the certificate source type and deployment target (e.g., SSM command to deploy replacement cert to EC2, kubectl command to trigger cert-manager renewal).
7. THE Incident_Triage_Engine SHALL complete the non-ACM triage mapping and produce the report within 60 seconds of initiation.
8. IF the Incident_Triage_Engine cannot determine all affected resources for a non-ACM certificate (e.g., EC2 instance offline, Kubernetes cluster unreachable), THEN THE Incident_Triage_Engine SHALL include a list of resources that could not be resolved, the reason for the failure, and the last known state from the Certificate_Inventory.

### Requirement 8: Cross-Cloud and Hybrid Certificate Management

**User Story:** As a multi-cloud platform engineer, I want the Agent to manage certificates across Kubernetes clusters, on-premises infrastructure, EC2 instances, and other cloud providers, so that I have unified certificate lifecycle management beyond ACM-integrated services.

#### Acceptance Criteria

1. THE Agent SHALL integrate with Kubernetes cert-manager to discover, monitor, and trigger renewal of certificates in configured Kubernetes clusters via the Kubernetes API.
2. THE Agent SHALL support discovery and monitoring of certificates on EC2 instances by scanning configured certificate file paths (such as /etc/ssl/certs, /etc/pki/tls, /etc/nginx/ssl) or querying an installed host agent.
3. THE Agent SHALL support integration with on-premises PKI systems through configurable connector plugins that implement a standard discovery and renewal interface.
4. THE Agent SHALL support integration with External_CA platforms including DigiCert CertCentral API, Let's Encrypt ACME protocol, and Venafi Trust Protection Platform API for certificate discovery and renewal.
5. WHEN a certificate managed by Kubernetes cert-manager is within the configured Alert_Threshold, THE Agent SHALL send an expiration notification and optionally trigger cert-manager renewal via the Kubernetes API.
6. WHEN a certificate on an EC2 instance is renewed, THE Agent SHALL deploy the new certificate files to the instance via SSM Run Command or host agent, and restart or reload the configured service (such as nginx, httpd, or application process).
7. THE Agent SHALL normalize certificate metadata from all Certificate_Source types into a unified schema in the Certificate_Inventory.
8. IF a cross-cloud or on-premises Certificate_Source is unreachable during a discovery scan, THEN THE Agent SHALL log the connectivity failure, use the last known certificate data, and send a warning notification.
9. THE Agent SHALL support discovery and monitoring of certificates from other cloud providers (Azure Key Vault, Google Cloud Certificate Manager) through configurable cloud connector plugins.
10. THE Agent SHALL support management of IoT device certificates registered in AWS IoT Core, including discovery, expiration monitoring, and renewal coordination.

### Requirement 9: Imported Certificate Management

**User Story:** As an operations engineer, I want the Agent to manage the lifecycle of imported certificates in ACM, including integration with external CAs for automated renewal, so that I can eliminate the manual process of renewing and re-importing certificates.

#### Acceptance Criteria

1. THE Agent SHALL maintain a registry of imported certificates in ACM with their originating External_CA, renewal configuration, and original import metadata.
2. WHEN an imported certificate is within the configured Alert_Threshold, THE Agent SHALL check if the originating External_CA has a configured API integration.
3. WHEN an External_CA API integration is configured (DigiCert, Let's Encrypt, Venafi, or custom), THE Agent SHALL invoke the External_CA API to request a renewed certificate, import the renewed certificate into ACM, and associate the certificate with the same resources as the expiring certificate.
4. THE Agent SHALL support External_CA integrations via configurable Lambda functions that implement a standard renewal interface, enabling integration with any CA that has an API.
5. WHEN an imported certificate is renewed and re-imported, THE Agent SHALL verify that all associated resources are using the new certificate and that the certificate chain is valid.
6. THE Agent SHALL support EventBridge Scheduler integration to periodically check imported certificate expiration dates and trigger renewal workflows.
7. IF an imported certificate renewal fails, THEN THE Agent SHALL send a critical alert with the failure reason and provide manual renewal instructions including the required certificate format, key requirements, and ACM import steps.
8. THE Agent SHALL track the renewal history of each imported certificate, including the originating CA, previous certificate serial numbers, and import timestamps.

### Requirement 10: Cost Optimization

**User Story:** As a cloud financial operations analyst, I want the Agent to identify unused or underutilized certificate resources and provide cost recommendations, so that I can reduce unnecessary spending on certificate infrastructure.

#### Acceptance Criteria

1. THE Cost_Analyzer SHALL identify Private_CA Certificate Authorities that have not issued a certificate within a configurable period (default: 90 days) and flag the Private_CA as potentially unused.
2. THE Cost_Analyzer SHALL identify ACM certificates that are not associated with any AWS resource and flag the certificates as unused.
3. THE Cost_Analyzer SHALL calculate the estimated monthly cost of each Private_CA and include the cost in the Certificate_Inventory.
4. WHEN a cost optimization report is requested, THE Cost_Analyzer SHALL produce a report containing: unused Private_CAs with their monthly cost, unused ACM certificates, and specific cost reduction recommendations.
5. THE Cost_Analyzer SHALL provide a projected annual savings estimate for each cost recommendation.
6. IF a Private_CA is flagged as unused, THEN THE Cost_Analyzer SHALL verify that no certificates issued by the Private_CA are still in active use before recommending deactivation or deletion.

### Requirement 11: Validation Management and DNS Remediation

**User Story:** As a DNS administrator, I want the Agent to manage certificate validation records and remediate validation failures, so that certificate renewals are not blocked by missing or incorrect DNS records.

#### Acceptance Criteria

1. WHEN a certificate requires DNS validation, THE Agent SHALL verify that the required CNAME validation records exist in the DNS zone and that the record values match the expected values.
2. WHEN DNS validation records are managed in Route 53, THE Agent SHALL create, update, or delete validation CNAME records as needed for certificate issuance and renewal.
3. WHEN DNS validation records are managed outside of Route 53, THE Agent SHALL send a notification to the DNS administrator with the exact required CNAME record name, value, and the target DNS zone, formatted for easy copy-paste into the DNS provider.
4. IF email validation is configured for a certificate and the validation email fails to deliver, THEN THE Agent SHALL send an alert recommending migration to DNS validation and provide the required CNAME record details as an alternative.
5. THE Agent SHALL track the validation status of each certificate and include the validation method, validation status, and last validation check timestamp in the Certificate_Inventory.
6. WHEN a certificate renewal fails due to a validation error, THE Agent SHALL diagnose the root cause (missing DNS record, incorrect record value, DNS propagation delay, email delivery failure, or outdated admin email contacts) and include the diagnosis in the alert notification.
7. THE Agent SHALL periodically verify that existing DNS validation records remain correct and have not been accidentally deleted or modified, and send an alert if a validation record is missing for a certificate that requires it.

### Requirement 12: Multi-Account and Cross-Region Orchestration

**User Story:** As a cloud platform architect, I want the Agent to operate across multiple AWS accounts and regions with proper IAM permissions, so that I can manage certificates centrally for my entire organization.

#### Acceptance Criteria

1. THE Agent SHALL support assuming IAM roles in multiple AWS accounts to perform certificate discovery, monitoring, and management operations.
2. THE Agent SHALL support configuration of target accounts and regions via a YAML or JSON configuration file.
3. WHEN operating across accounts, THE Agent SHALL use least-privilege IAM roles with permissions scoped to certificate management operations.
4. THE Agent SHALL support AWS Organizations integration to automatically discover accounts within an organization.
5. WHEN a certificate is required in a specific region (such as us-east-1 for CloudFront), THE Agent SHALL ensure the certificate is provisioned in the correct region and track the regional requirement in the Certificate_Inventory.
6. THE Agent SHALL support Private_CA certificate sharing across accounts using AWS Resource Access Manager (RAM) and manage the cross-account permissions.
7. IF an IAM role assumption fails for a target account, THEN THE Agent SHALL log the failure, continue operations for remaining accounts, and send an alert identifying the inaccessible account.

### Requirement 13: Agent Deployment and Configuration on Amazon Bedrock AgentCore

**User Story:** As a platform engineer, I want to deploy the Certificate Management Agent on Amazon Bedrock AgentCore with minimal setup, so that I can leverage managed agent runtime, built-in memory, identity, observability, and tool integration without managing custom infrastructure.

#### Acceptance Criteria

1. THE Agent SHALL be deployed on Amazon Bedrock AgentCore Runtime, leveraging its managed auto-scaling (from zero to thousands of sessions) and microVM-based session isolation for secure multi-tenant operation.
2. THE Agent SHALL be deployable via AWS CloudFormation or AWS CDK with a single deployment template that provisions the AgentCore agent, supporting infrastructure (DynamoDB, S3, EventBridge), and required IAM roles.
3. THE Agent SHALL use AgentCore Memory to maintain conversation context, certificate interaction history, and user preferences across sessions, enabling context-aware responses in the Chat_Interface.
4. THE Agent SHALL use AgentCore Identity to authenticate and authorize users via OAuth standards, integrating with Amazon Cognito or IAM Identity Center for user authentication and tenant-scoped access control.
5. THE Agent SHALL use AgentCore Gateway to expose certificate management operations (discovery, renewal, provisioning, revocation, reporting) as agent-compatible tools, and to connect to external systems (External_CA APIs, Kubernetes clusters, on-premises PKI) via MCP servers or Lambda functions.
6. THE Agent SHALL use AgentCore Observability (powered by Amazon CloudWatch) for comprehensive monitoring, including real-time dashboards, detailed audit trails of agent reasoning and actions, and OpenTelemetry-compatible tracing.
7. THE Agent SHALL use Amazon DynamoDB for the Certificate_Inventory data store.
8. THE Agent SHALL use AWS Lambda for event-driven operations (certificate event processing, External_CA integrations) and AWS Step Functions for multi-step Renewal_Workflow orchestration that requires coordination across multiple services.
9. THE Agent SHALL use Amazon EventBridge for scheduling scans, evaluations, rotation triggers, and report generation.
10. THE Agent SHALL store its configuration in AWS Systems Manager Parameter Store or AWS Secrets Manager.
11. WHEN the Agent is first deployed, THE Agent SHALL perform an initial full discovery scan across all configured accounts, regions, and external sources.
12. THE Agent SHALL be framework-agnostic, supporting deployment with any compatible agent framework (such as Strands Agents, LangGraph, or CrewAI) on AgentCore Runtime.
13. THE Agent SHALL support AgentCore Code Interpreter for dynamic certificate analysis tasks such as parsing certificate files, validating certificate chains programmatically, and generating custom reports.

### Requirement 14: SLR and IAM Misconfiguration Detection

**User Story:** As a security operations engineer, I want the Agent to detect IAM and Service-Linked Role misconfigurations that could prevent certificate auto-renewal, so that I can fix permission issues before they cause renewal failures.

#### Acceptance Criteria

1. THE Agent SHALL verify that the ACM Service-Linked Role exists and has the required permissions in each monitored account.
2. WHEN the ACM Service-Linked Role is missing or misconfigured, THE Agent SHALL send an alert with the specific misconfiguration details and step-by-step remediation instructions.
3. THE Agent SHALL verify that IAM permissions required for DNS validation record management in Route 53 are correctly configured.
4. THE Agent SHALL verify that cross-account Private_CA sharing permissions via RAM are correctly configured for accounts that use shared Private_CAs.
5. IF an IAM permission issue is detected that could prevent certificate renewal, THEN THE Agent SHALL include the affected certificates, the specific permission gap, and the required IAM policy statement in the alert notification.
6. THE Agent SHALL perform IAM configuration checks on a configurable schedule (default: daily) and report the results in the Health_Dashboard.

### Requirement 15: Certificate Type Support Beyond TLS

**User Story:** As a security engineer, I want the Agent to manage non-TLS certificate types issued by Private CA and external sources, including certificates for email encryption, code signing, and IoT device authentication, so that I have unified management for all certificate types.

#### Acceptance Criteria

1. THE Agent SHALL discover and inventory certificates issued by Private_CA for email encryption (S/MIME), code signing, and IoT device authentication in addition to TLS certificates.
2. THE Agent SHALL track the certificate type (TLS, email encryption, code signing, IoT device) in the Certificate_Inventory.
3. WHEN a non-TLS certificate issued by Private_CA is within the configured Alert_Threshold, THE Agent SHALL send an expiration notification specific to the certificate type.
4. THE Agent SHALL support configurable renewal workflows for each certificate type, as renewal and deployment procedures differ by certificate type.
5. THE Policy_Engine SHALL support policy rules specific to each certificate type, including allowed key usages and extended key usages.
6. THE Agent SHALL support discovery and management of code signing certificates used in CI/CD pipelines, tracking the signing key expiration and associated build systems.

### Requirement 16: Audit Trail and Change Tracking

**User Story:** As an auditor, I want the Agent to maintain a complete audit trail of all certificate lifecycle events, so that I can trace every change made to certificates in the environment.

#### Acceptance Criteria

1. THE Agent SHALL record an audit event for every certificate lifecycle action including discovery, provisioning, renewal, deployment, rotation, revocation, policy evaluation, and alert notification.
2. THE Agent SHALL include the following in each audit event: timestamp, action type, certificate identifier, actor (Agent or user), source account, source region, action outcome, and any error details.
3. THE Agent SHALL store audit events in a tamper-resistant log, such as Amazon CloudWatch Logs with a retention policy or Amazon S3 with object lock.
4. WHEN an audit trail query is submitted via the Agent API, THE Agent SHALL return matching audit events filtered by certificate identifier, time range, action type, or account.
5. THE Agent SHALL retain audit events for a configurable period, with a default retention of 365 days.

### Requirement 17: Notification and Escalation Management

**User Story:** As an operations manager, I want the Agent to support flexible notification routing and escalation policies, so that the right teams are notified at the right time based on certificate ownership and severity.

#### Acceptance Criteria

1. THE Agent SHALL support configurable notification routing rules based on certificate tags, account, region, certificate type, and owning team.
2. THE Agent SHALL support escalation policies that increase notification recipients and channels as certificate expiration approaches or remediation actions fail.
3. WHEN a notification is sent, THE Agent SHALL record the notification in the audit trail with the recipients, channel, and message content.
4. THE Agent SHALL support suppression rules to temporarily silence notifications for specific certificates or accounts during planned maintenance windows.
5. IF a critical alert is not acknowledged within a configurable time period, THEN THE Agent SHALL escalate the alert to the next level in the escalation policy.

### Requirement 18: Certificate Health Dashboard

**User Story:** As a platform operations lead, I want a centralized web-based dashboard showing real-time certificate health across all accounts, regions, and certificate sources, so that I can quickly assess my organization's certificate posture without querying multiple systems.

#### Acceptance Criteria

1. THE Health_Dashboard SHALL display a real-time overview of all certificates in the Certificate_Inventory, grouped by account, region, certificate source type, and health status.
2. THE Health_Dashboard SHALL display certificate health status using the following categories: healthy (more than 30 days to expiration), warning (7-30 days to expiration), critical (less than 7 days to expiration), expired, and revoked.
3. THE Health_Dashboard SHALL provide drill-down views from aggregate summaries to individual certificate details, including associated resources, renewal status, and policy compliance.
4. THE Health_Dashboard SHALL display a timeline view showing upcoming expirations across the next 90 days.
5. THE Health_Dashboard SHALL display the status of recent and in-progress renewal workflows, including success, failure, and pending actions.
6. THE Health_Dashboard SHALL support filtering and searching by domain name, account, region, certificate type, issuer, health status, and certificate source.
7. THE Health_Dashboard SHALL display IAM and SLR configuration health status for each monitored account.
8. THE Health_Dashboard SHALL be accessible via a web interface served through API Gateway and CloudFront, with authentication via Amazon Cognito or IAM Identity Center.

### Requirement 19: Certificate Revocation Management

**User Story:** As a security incident responder, I want the Agent to manage certificate revocation when a private key is compromised or a certificate needs to be invalidated, so that I can quickly respond to security incidents involving certificates.

#### Acceptance Criteria

1. WHEN a revocation request is submitted via the Agent API, THE Revocation_Manager SHALL revoke the specified certificate through the appropriate CA (ACM, Private_CA, or External_CA).
2. WHEN a Private_CA-issued certificate is revoked, THE Revocation_Manager SHALL update the Certificate Revocation List (CRL) and verify the revocation is reflected in the CRL within the configured CRL update interval.
3. THE Revocation_Manager SHALL track the OCSP (Online Certificate Status Protocol) responder status for certificates that support OCSP and verify that revocation status is correctly reported.
4. WHEN a certificate is revoked, THE Revocation_Manager SHALL trigger the Provisioning_Engine to issue a replacement certificate and deploy the replacement to all affected Deployment_Target resources.
5. THE Revocation_Manager SHALL record all revocation actions in the audit trail with the revocation reason, requestor, and timestamp.
6. IF a revocation request fails, THEN THE Revocation_Manager SHALL send a critical alert with the failure reason and provide manual revocation instructions.

### Requirement 20: Automated Certificate Provisioning

**User Story:** As a DevOps engineer, I want the Agent to automate the provisioning of new certificates, including CSR generation, CA submission, and initial deployment, so that I can rapidly provision certificates for new services without manual steps.

#### Acceptance Criteria

1. WHEN a Certificate_Request is submitted via the Agent API, THE Provisioning_Engine SHALL generate a Certificate Signing Request (CSR) with the specified domain name, SANs, key algorithm, and key size.
2. THE Provisioning_Engine SHALL submit the CSR to the configured CA (ACM, Private_CA, or External_CA) and track the issuance status to completion.
3. WHEN a certificate is issued, THE Provisioning_Engine SHALL deploy the certificate to the specified Deployment_Target resources and verify successful deployment.
4. THE Provisioning_Engine SHALL support provisioning certificates through ACM for integrated AWS services, through Private_CA for exportable certificates, and through External_CA APIs for external certificates.
5. IF a certificate provisioning request fails, THEN THE Provisioning_Engine SHALL send an alert with the failure reason and the step at which provisioning failed.

### Requirement 21: Self-Service Certificate Request Workflow

**User Story:** As a development team lead, I want my team to submit certificate requests through a self-service workflow with approval gates, so that certificate provisioning follows organizational governance without blocking development velocity.

#### Acceptance Criteria

1. THE Agent SHALL expose a self-service API endpoint for submitting Certificate_Request objects containing the requested domain name, SANs, certificate type, intended deployment targets, and requesting team.
2. THE Agent SHALL support configurable approval workflows that route Certificate_Request objects to designated approvers based on domain name patterns, certificate type, and requesting team.
3. WHEN a Certificate_Request is approved, THE Agent SHALL invoke the Provisioning_Engine to provision and deploy the certificate.
4. WHEN a Certificate_Request is rejected, THE Agent SHALL notify the requestor with the rejection reason.
5. THE Agent SHALL enforce configurable request policies, including allowed domain name patterns, maximum SAN count, allowed key algorithms, and allowed certificate types per team.
6. THE Agent SHALL record all Certificate_Request submissions, approvals, rejections, and provisioning outcomes in the audit trail.

### Requirement 22: CI/CD Pipeline Integration

**User Story:** As a release engineer, I want the Agent to integrate with CI/CD pipelines for automated certificate deployment during application releases, so that certificate updates are part of the standard deployment process.

#### Acceptance Criteria

1. THE Agent SHALL provide a CLI tool and API endpoints that CI/CD pipelines can invoke to request, retrieve, and deploy certificates as part of a deployment workflow.
2. WHEN a CI/CD pipeline requests a certificate for a deployment, THE Agent SHALL provision or retrieve the certificate and return the certificate ARN or certificate files to the pipeline.
3. THE Agent SHALL support integration with AWS CodePipeline, AWS CodeBuild, and generic webhook-based CI/CD systems for certificate deployment triggers.
4. WHEN a deployment pipeline completes, THE Agent SHALL verify that the deployed certificate is correctly installed and accessible on the target endpoint.
5. THE Agent SHALL support deployment of code signing certificates to CI/CD build systems, tracking which signing certificates are used by which pipelines.

### Requirement 23: Certificate Chain Validation

**User Story:** As a security engineer, I want the Agent to validate the complete certificate chain from leaf to root for all managed certificates, so that I can detect broken chains, missing intermediates, and trust issues before they cause service disruptions.

#### Acceptance Criteria

1. THE Chain_Validator SHALL validate the complete certificate chain (leaf, intermediate, root) for each certificate in the Certificate_Inventory.
2. WHEN a certificate chain is incomplete (missing intermediate certificates), THE Chain_Validator SHALL flag the certificate as having a broken chain and send an alert with the missing certificate details.
3. WHEN a certificate chain contains an expired intermediate or root certificate, THE Chain_Validator SHALL flag the certificate and send a critical alert.
4. THE Chain_Validator SHALL verify that the root certificate in each chain is present in the configured trust store.
5. THE Chain_Validator SHALL perform chain validation on a configurable schedule (default: daily) and after every certificate renewal or deployment.
6. IF a chain validation failure is detected on a deployed certificate, THEN THE Chain_Validator SHALL include the affected endpoints and recommended remediation steps in the alert.

### Requirement 24: Certificate Backup and Disaster Recovery

**User Story:** As a disaster recovery engineer, I want the Agent to back up certificate metadata and exportable private keys, so that I can restore certificate configurations after a disaster without re-issuing all certificates.

#### Acceptance Criteria

1. THE Agent SHALL back up the Certificate_Inventory metadata to a configurable Amazon S3 bucket with versioning and encryption enabled on a configurable schedule (default: daily).
2. THE Agent SHALL back up exportable private keys (from Private_CA-issued certificates) to AWS Secrets Manager or a configurable encrypted S3 bucket with server-side encryption using AWS KMS.
3. WHEN a disaster recovery restore is initiated, THE Agent SHALL restore the Certificate_Inventory from the latest backup and reconcile with a fresh discovery scan.
4. THE Agent SHALL maintain backup retention for a configurable period (default: 90 days) with point-in-time recovery capability.
5. IF a backup operation fails, THEN THE Agent SHALL send a critical alert and retry the backup within one hour.

### Requirement 25: Rate Limiting and Throttling Awareness

**User Story:** As a platform engineer, I want the Agent to respect API rate limits for ACM, Private CA, and external CA APIs, so that the Agent does not trigger throttling that could impact other operations in my AWS accounts.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL track API call rates for ACM, Private_CA, and each configured External_CA and enforce configurable rate limits per API per account per region.
2. WHEN the Rate_Limiter detects that an API call rate is approaching the configured threshold (default: 80% of the known rate limit), THE Rate_Limiter SHALL queue subsequent requests and process the requests at a rate below the threshold.
3. IF an API call receives a throttling response, THEN THE Rate_Limiter SHALL apply exponential backoff with jitter and retry the request up to a configurable number of times.
4. THE Rate_Limiter SHALL prioritize renewal and remediation operations over discovery and reporting operations when rate limits are constrained.
5. THE Rate_Limiter SHALL log all throttling events and include throttling statistics in the Health_Dashboard.

### Requirement 26: Certificate Transparency Monitoring

**User Story:** As a security operations engineer, I want the Agent to monitor Certificate Transparency logs for unauthorized certificate issuance for my domains, so that I can detect and respond to rogue or misissued certificates.

#### Acceptance Criteria

1. THE CT_Monitor SHALL monitor configured Certificate Transparency logs for new certificate issuance events matching the organization's configured domain names and domain patterns.
2. WHEN a certificate is detected in a CT_Log that was not provisioned by the Agent or a known authorized CA, THE CT_Monitor SHALL send a critical alert with the certificate details, issuing CA, and issuance timestamp.
3. THE CT_Monitor SHALL support configurable domain watch lists specifying which domain names and wildcard patterns to monitor.
4. THE CT_Monitor SHALL check CT logs on a configurable schedule (default: every 6 hours) and record all detected issuance events in the audit trail.
5. WHEN an unauthorized certificate issuance is confirmed, THE CT_Monitor SHALL create an incident record and optionally trigger the Revocation_Manager to request revocation from the issuing CA.

### Requirement 27: Secrets Management Integration

**User Story:** As a security architect, I want the Agent to integrate with secrets management systems for secure storage and retrieval of private keys, so that private keys are never stored in plaintext or in insecure locations.

#### Acceptance Criteria

1. THE Secrets_Integration SHALL store all private keys managed by the Agent in AWS Secrets Manager or AWS Systems Manager Parameter Store (SecureString) with encryption using AWS KMS customer-managed keys.
2. WHEN a private key is needed for certificate deployment to an EC2 instance, Kubernetes cluster, or on-premises system, THE Secrets_Integration SHALL retrieve the key from the secrets store and transmit the key over an encrypted channel.
3. THE Secrets_Integration SHALL support automatic rotation of the KMS keys used to encrypt stored private keys on a configurable schedule.
4. THE Agent SHALL enforce that private keys are never written to unencrypted storage, logged in plaintext, or included in notification messages.
5. THE Secrets_Integration SHALL record all private key access events in the audit trail with the accessor identity, access reason, and timestamp.

### Requirement 28: Multi-Tenancy Support

**User Story:** As a managed service provider, I want the Agent to support multi-tenant operation where different teams or business units have isolated views and management of their own certificates, so that I can offer certificate management as a shared service.

#### Acceptance Criteria

1. THE Agent SHALL support tenant isolation through configurable tenant definitions based on AWS account, certificate tags, domain name patterns, or organizational unit.
2. THE Agent SHALL enforce tenant-scoped access controls so that API requests, dashboard views, and reports are restricted to the requesting tenant's certificates.
3. THE Agent SHALL support tenant-specific notification routing, policy rules, and approval workflows.
4. WHEN a compliance report is generated for a tenant, THE Compliance_Reporter SHALL include certificates belonging to that tenant and exclude certificates belonging to other tenants.
5. THE Agent SHALL support a global administrator role that has visibility across all tenants for organization-wide reporting and policy enforcement.

### Requirement 29: Conversational Chat Interface

**User Story:** As a certificate owner, I want to interact with the Agent through a natural language chat interface where I can ask questions about my certificates, request actions, and get recommendations, so that I can manage certificates without needing to navigate dashboards or write API calls.

#### Acceptance Criteria

1. THE Chat_Interface SHALL accept natural language queries from users and return structured responses about certificate status, expiration timelines, renewal history, policy compliance, and associated resources.
2. THE Chat_Interface SHALL support queries such as "show me all certificates expiring in the next 30 days", "why did the renewal fail for [domain]", "which services are using certificate [ARN or domain]", and "what certificates are non-compliant".
3. THE Chat_Interface SHALL support action requests such as "renew the certificate for [domain]", "trigger a discovery scan", "generate a compliance report for [account]", and "revoke certificate [identifier]", invoking the corresponding Agent tools via AgentCore Gateway with appropriate authorization checks.
4. THE Chat_Interface SHALL be accessible via a web-based chat widget embedded in the Health_Dashboard and via a standalone web endpoint.
5. THE Chat_Interface SHALL authenticate users via AgentCore Identity (OAuth standards) integrated with Amazon Cognito or IAM Identity Center, and enforce the same tenant-scoped access controls as the Health_Dashboard.
6. THE Chat_Interface SHALL leverage AgentCore Memory to maintain conversation context across sessions, enabling follow-up questions without restating full context (for example, "now filter that to us-east-1 only") and remembering user preferences and frequently queried certificates.
7. THE Chat_Interface SHALL use Amazon Bedrock foundation models (or a configurable LLM backend) for natural language understanding and response generation, deployed on AgentCore Runtime.
8. WHEN a user asks a question, THE Chat_Interface SHALL query the Certificate_Inventory, audit trail, and Agent operational data via AgentCore Gateway tools to provide accurate, real-time answers with source references (certificate ARNs, account IDs, timestamps).
9. WHEN a user requests a destructive or high-impact action (revocation, bulk renewal, policy change), THE Chat_Interface SHALL require explicit confirmation before executing the action.
10. THE Chat_Interface SHALL log all user interactions (queries and actions) in the audit trail via AgentCore Observability with the user identity, query text, response summary, and any actions triggered.
11. THE Chat_Interface SHALL leverage AgentCore Runtime's auto-scaling to handle concurrent user sessions and AgentCore's microVM isolation to ensure session-level data privacy between users and tenants.


## Glossary

- **Agent**: The Certificate Management Agent system being specified in this document
- **ACM**: AWS Certificate Manager, the AWS service for provisioning and managing TLS certificates
- **Private_CA**: AWS Private Certificate Authority, used to issue private certificates for internal services, IoT devices, code signing, and email encryption
- **Certificate_Inventory**: The centralized data store maintained by the Agent containing metadata for all discovered certificates across all sources
- **Certificate_Source**: Any system from which the Agent discovers certificates, including ACM, Private CA, Kubernetes cert-manager, on-premises PKI, and external CAs
- **External_CA**: A Certificate Authority not managed by AWS, such as DigiCert, Let's Encrypt, Venafi, or an on-premises CA
- **Renewal_Workflow**: The automated sequence of steps the Agent executes to renew a certificate, including validation, issuance, and deployment
- **Discovery_Scanner**: The Agent component responsible for scanning accounts, regions, and external sources to find certificates
- **Policy_Engine**: The Agent component that evaluates certificates against configurable compliance and security policies
- **Incident_Triage_Engine**: The Agent component that maps expired or failing certificates to affected services and endpoints
- **Compliance_Reporter**: The Agent component that generates audit-ready reports on certificate posture
- **Cost_Analyzer**: The Agent component that identifies unused or underutilized certificate resources and provides cost recommendations
- **Health_Dashboard**: The Agent component that provides a centralized web-based UI for real-time certificate health visibility across accounts, regions, and sources
- **Provisioning_Engine**: The Agent component that handles automated certificate provisioning, including CSR generation, CA submission, and initial deployment
- **Revocation_Manager**: The Agent component that handles certificate revocation operations, CRL management, and OCSP status tracking
- **Chain_Validator**: The Agent component that validates certificate chain integrity from leaf to root
- **CT_Monitor**: The Agent component that monitors Certificate Transparency logs for unauthorized certificate issuance
- **Secrets_Integration**: The Agent component that integrates with secrets management systems for secure private key storage and retrieval
- **Validation_Method**: The mechanism used to prove domain ownership, either DNS-based (CNAME records) or email-based
- **CT_Log**: Certificate Transparency Log, a public append-only log of issued certificates
- **SLR**: Service-Linked Role, an IAM role linked to an AWS service that the service uses to perform actions on behalf of the user
- **Rotation_Schedule**: A configurable schedule defining how frequently certificates should be rotated
- **Alert_Threshold**: A configurable number of days before certificate expiration at which the Agent sends notifications
- **Deployment_Target**: An AWS resource or external system where a certificate is installed, such as ELB, CloudFront, API Gateway, EC2 instance, or Kubernetes ingress
- **Certificate_Request**: A self-service request submitted by a developer or team to provision a new certificate through the Agent
- **Rate_Limiter**: The Agent component that tracks and enforces API rate limits for ACM, Private CA, and external CA APIs to prevent throttling
- **Chat_Interface**: The Agent component that provides a conversational natural language front-end for customers to query certificate status, trigger actions, and receive recommendations
- **AgentCore**: Amazon Bedrock AgentCore, the fully managed agentic platform used to deploy and operate the Certificate Management Agent, providing managed runtime (auto-scaling, microVM isolation), memory, identity, observability, tool gateway, and code interpreter capabilities

## ACM Limitations Addressed

This section maps each known ACM limitation or drawback to the specific requirement(s) in this document that address it, providing explicit traceability.

| # | ACM Limitation / Drawback | Addressed By | How Addressed |
|---|---------------------------|-------------|---------------|
| L1 | ACM can only auto-renew certs issued by ACM or Private CA, not external CAs (unless external CA has API + Lambda) | Req 9 (AC 3, 4), Req 3 (AC 6, 7) | Agent integrates with External_CA APIs and Lambda-based connectors to automate renewal of imported certificates that ACM cannot renew |
| L2 | ACM public certificates cannot be deployed to EC2 instances directly — only to integrated services (ELB, CloudFront, API Gateway) | Req 8 (AC 2, 5), Req 3 (AC 5) | Agent deploys Private_CA-exported certificates to EC2 instances via host agent or SSM, with service restart/reload |
| L3 | ACM-issued public certificate private keys cannot be exported | Req 8 (AC 2), Req 3 (AC 5), Req 15 (AC 4) | Agent uses Private_CA certificates (which are exportable) for EC2, IoT, and on-premises targets; manages the export and deployment workflow |
| L4 | Regional scope — certificates must be provisioned per-region (except CloudFront requires us-east-1) | Req 12 (AC 5), Req 3 (AC 11) | Agent orchestrates cross-region provisioning, ensures CloudFront certs are in us-east-1, and manages per-region certificate inventory |
| L5 | DNS validation confusing for customers managing zones outside Route 53 | Req 11 (AC 3, 6), Req 3 (AC 2) | Agent detects non-Route 53 DNS, sends clear instructions with exact CNAME records, and diagnoses validation failures |
| L6 | Email validation is fragile — depends on specific admin email addresses | Req 11 (AC 4), Req 3 (AC 2) | Agent detects email validation failures, recommends migration to DNS validation, and provides the required CNAME details |
| L7 | Auto-renewal only works if certificate is actively associated with a supported resource AND validation conditions are met | Req 3 (AC 1, 2, 3), Req 14 (AC 1-5) | Agent pre-validates renewal conditions (resource association, DNS records, SLR, IAM) and remediates issues before renewal window |
| L8 | No proactive alerting built into ACM — customers must set up CloudWatch/EventBridge themselves | Req 2 (AC 1-8), Req 17 (AC 1-5) | Agent provides built-in multi-channel alerting with configurable thresholds, escalation policies, and routing rules |
| L9 | No centralized dashboard for cert health across accounts/regions | Req 18 (AC 1-8) | Agent provides a centralized Health_Dashboard with real-time visibility across all accounts, regions, and certificate sources |
| L10 | ACM cannot issue short-lived certificates | Req 4 (AC 3, 7), Req 20 (AC 1-5) | Agent supports rotation frequencies as short as 24 hours and automates provisioning through Private_CA or External_CA for short-lived certs |
| L11 | Domain Validation Issues: DNS CNAME records not correctly added, email validation fails with outdated contacts | Req 11 (AC 1-6) | Agent validates DNS records, auto-creates CNAMEs in Route 53, diagnoses root causes, and alerts on email validation failures |
| L12 | Automatic Renewal Failures: Fails if domain validation not maintained or SLR misconfigured | Req 14 (AC 1-5), Req 3 (AC 1-4) | Agent proactively checks SLR configuration, DNS validation state, and IAM permissions before renewal window opens |
| L13 | Certificate Import Limitations: Imported certs not automatically renewed | Req 9 (AC 1-7) | Agent maintains imported cert registry with External_CA mappings, automates renewal via API/Lambda integrations, and re-imports |
| L14 | Service Integration Restrictions: ACM public certs cannot be exported, must use specific AWS services | Req 8 (AC 2, 5), Req 3 (AC 5, 8) | Agent manages Private_CA certs for non-integrated services and handles export, deployment, and service restart workflows |
| L15 | Certificate Pinning Conflicts: Apps using cert pinning fail when rotated cert applied | Req 4 (AC 5) | Agent flags pinning-sensitive certificates and sends pre-rotation notifications with configurable lead time |
| L16 | Internal CA/Shared Account Complexity: Private certs across accounts with shared Private CAs lead to complex IAM issues | Req 12 (AC 6), Req 14 (AC 4) | Agent manages RAM-based cross-account Private_CA sharing and validates cross-account IAM permissions |
| L17 | Unsupported Certificate Types: ACM does not support all certificate types | Req 15 (AC 1-5) | Agent manages S/MIME, code signing, IoT device certs via Private_CA with type-specific workflows and policies |
