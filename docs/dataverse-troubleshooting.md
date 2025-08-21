# Dataverse Operations Troubleshooting Guide

## Common Issues and Solutions

### 1) Timeout Errors

Problem: read operation timed out

Fixes implemented:
- Increased metadata request timeout to 60s (read/connect)
- Exponential backoff retries for transient errors

What you can do:
- Re-run with: python blc.py dataverse probe
- Verify network and DNS

### 2) Authentication Failures (401)

- Ensure .env contains AZURE_* and DATAVERSE_URL
- Ensure app registration has Dataverse application permissions
- Confirm tenant/URL correctness

### 3) Entity Not Found (404)

- Use entity logical names (lowercase), e.g., account, contact
- Confirm the entity exists in your environment

### 4) Rate Limiting (429)

- Backoff retries will space requests
- Reduce request volume or add caching

## Performance

- Connection pooling enabled (httpx Limits)
- Entity definitions cached per run

## Debugging Tips

- Enable DEBUG logging
- Use CLI probes:
  - python blc.py dataverse probe
  - python blc.py dataverse entity-def account
  - python blc.py dataverse query account --top 3

