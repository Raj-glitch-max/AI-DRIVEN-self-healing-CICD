# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you find any vulnerability, please report it to us immediately.

**DO NOT** open public issues for security vulnerabilities.

### How to Report

Please email security concerns to: [security@ai-cicd.project] (replace with actual email)

In your report, please include:
- A description of the vulnerability.
- Steps to reproduce the issue.
- Impact of the vulnerability.
- Any proof of concept code, if available.

### Response Timeline

- **Acknowledgement**: We will acknowledge receipt of your report within 48 hours.
- **Assessment**: We will assess the vulnerability and provide an estimated timeline for a fix within 1 week.
- **Resolution**: We will aim to release a fix as soon as possible, prioritizing critical issues.

## Security Measures

This project implements the following security measures:

- **Non-root Containers**: Docker containers run as a non-root user (`appuser`) to minimize impact of potential container breakouts.
- **Secrets Management**: Sensitive information (API keys, tokens) is managed via environment variables and never committed to version control.
- **Input Validation**: API endpoints validate input to prevent common injection attacks.
- **Dependencies**: We regularly scan and update dependencies to address known vulnerabilities.
- **Rate Limiting**: (If applicable) Public endpoints are rate-limited to prevent abuse.

## Safe Harbor

If you conduct security research on this project in good faith and follow this policy, we will not pursue legal action against you.
