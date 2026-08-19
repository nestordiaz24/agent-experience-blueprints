# Security Policy

## Supported versions

Security fixes are applied to the latest release and the default branch while this project is in preview.

## Reporting a vulnerability

Report vulnerabilities privately through the repository's GitHub Security Advisory page. Do not open a public issue or include credentials, customer data, prompts, retrieved content, or access tokens in a report.

Include a concise description, affected version or commit, reproduction steps using synthetic data, and the expected impact. Maintainers will acknowledge the report after triage and coordinate disclosure and remediation through the advisory.

## Sample security boundary

This repository is reference code, not a hosted service. Never commit real tenant identifiers, secrets, production prompts, customer records, or telemetry exports. Cloud-connected samples must use least-privilege delegated identity and keep provider credentials on the server.
