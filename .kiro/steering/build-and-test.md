# Build and Test Instructions

## Prerequisites

- Python 3.12+
- Node.js 18+ (for CDK)
- AWS CDK CLI (`npm install -g aws-cdk`)
- AWS CLI configured with appropriate credentials

## Project Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_discovery_scanner.py

# Run integration tests (requires AWS credentials)
pytest tests/integration/ -m integration
```

## Linting and Formatting

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type checking
mypy src/
```

## CDK Deployment

```bash
# Synthesize CloudFormation template
cdk synth

# Deploy to dev environment
cdk deploy --context env=dev

# Diff changes before deploying
cdk diff
```
