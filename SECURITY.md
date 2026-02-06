# Security Policy

## Supported Versions

We actively support and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of Klydo MCP Server seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Create Public Issues

Please **DO NOT** create public GitHub issues for security vulnerabilities.

### 2. Report Privately

Send a detailed report to:

- **Email**: security@klydo.in
- **GitHub Security Advisories**: [Report a vulnerability](https://github.com/myselfshravan/klydo-mcp/security/advisories/new)

### 3. Include These Details

Please include as much information as possible:

- Type of vulnerability (e.g., injection, authentication bypass, data exposure)
- Full paths of affected source files
- Step-by-step instructions to reproduce
- Proof-of-concept or exploit code (if possible)
- Impact assessment and potential attack scenarios

### 4. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Resolution Target**: Within 30 days (depending on severity)

## Security Best Practices

When using Klydo MCP Server, please follow these guidelines:

### Environment Variables

```bash
# ✅ DO: Set tokens via environment variables
export KLYDO_KLYDO_API_TOKEN="your-secret-token"

# ❌ DON'T: Hardcode tokens in your code
KLYDO_KLYDO_API_TOKEN = "your-secret-token"  # Never do this!
```

### Configuration Files

```bash
# ✅ DO: Use .env files (not committed to git)
cp .env.example .env
# Edit .env with your secrets

# Make sure .env is in .gitignore
echo ".env" >> .gitignore
```

### Production Deployments

1. **Use Secrets Management**
   - AWS Secrets Manager
   - HashiCorp Vault
   - Kubernetes Secrets
   - Environment variables injected by CI/CD

2. **Restrict Access**
   - Use least-privilege principles
   - Rotate API tokens regularly
   - Monitor for unauthorized access

3. **Network Security**
   - Run behind a firewall/VPN if needed
   - Use TLS for all external communications
   - Consider rate limiting

4. **Logging**
   - Don't log sensitive data (tokens, personal info)
   - Set `KLYDO_DEBUG=false` in production
   - Monitor logs for suspicious activity

## Known Security Considerations

### API Token Handling

The Klydo MCP Server uses API tokens to authenticate with the Klydo.in catalog API. These tokens:

- Should be kept confidential
- Should be rotated periodically
- Are passed via the `KLYDO_KLYDO_API_TOKEN` environment variable
- Are used in HTTP Authorization headers

### Data Handling

The MCP Server:

- Does not store user data persistently
- Uses in-memory caching (cleared on restart)
- Makes external API calls to klydo.in
- Does not collect analytics or telemetry

### Third-Party Dependencies

We regularly update dependencies to patch security vulnerabilities. Key dependencies:

| Package | Purpose |
|---------|---------|
| httpx | HTTP client (TLS-enabled) |
| pydantic | Data validation |
| fastmcp | MCP protocol implementation |

## Security Updates

Security updates are released as:

1. **Patch versions** for critical vulnerabilities
2. **Minor versions** for non-critical security improvements
3. Updates are announced via:
   - GitHub Releases
   - CHANGELOG.md
   - GitHub Security Advisories (for critical issues)

## Acknowledgments

We appreciate researchers who help improve our security. Responsible disclosures may be acknowledged in our CHANGELOG (with your permission).

---

Thank you for helping keep Klydo MCP Server and its users safe! 🔒