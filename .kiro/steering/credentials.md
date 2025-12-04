---
inclusion: always
---

# Credentials Handling

When working with AWS services, deployment, or any operations requiring credentials:

1. **Never hardcode credentials** in code or configuration files
2. **Always prompt the user** for required credentials, API keys, or configuration values
3. **Use environment variables** for sensitive data (e.g., `.env` files)
4. **Reference .env.example** files to understand what credentials are needed
5. **Ask before assuming** - if credentials might be needed, confirm with the user first

Common scenarios requiring credentials:
- AWS deployments (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
- Database connections (DATABASE_URL, DB_PASSWORD)
- API keys for external services
- CDK deployments and stack operations
