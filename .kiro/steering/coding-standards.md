# Coding Standards

## Language and Runtime

- Primary language: Python 3.12+
- Infrastructure as Code: AWS CDK (TypeScript or Python)
- Lambda functions: Python with AWS Lambda Powertools
- Use type hints throughout all Python code

## Code Style

- Follow PEP 8 for Python code
- Use `black` for formatting, `ruff` for linting
- Maximum line length: 120 characters
- Use docstrings (Google style) for all public functions and classes
- Use meaningful variable and function names — no single-letter variables except loop counters

## AWS Best Practices

- Use least-privilege IAM policies
- Never hardcode credentials or secrets — use Secrets Manager or SSM Parameter Store
- Use structured JSON logging via Lambda Powertools
- Tag all AWS resources with: Project, Environment, Owner
- Use environment variables for configuration, not hardcoded values

## Testing

- Write unit tests for all business logic (pytest)
- Write integration tests for AWS service interactions
- Minimum 80% code coverage target
- Use moto or localstack for mocking AWS services in tests

## Git Conventions

- Branch naming: `feature/`, `bugfix/`, `chore/` prefixes
- Commit messages: follow Conventional Commits format
- Never push directly to main — use pull requests
- All PRs require at least one review
