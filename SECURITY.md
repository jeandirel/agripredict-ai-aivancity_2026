# Security Policy

## Supported version

The supported academic release is `1.0.x`.

## Reporting a vulnerability

Do not disclose secrets, private parcel data or exploitable details in a public issue. Contact the repository owner privately and provide:

- affected component and version ;
- reproduction steps ;
- expected impact ;
- suggested remediation when available.

## Security boundaries

- Kaggle credentials must remain in environment variables or GitHub Secrets.
- No secret may be committed to Git.
- The API validates request structure but is not a substitute for an authenticated production gateway.
- Model artifacts must come from a trusted workflow and controlled storage.
- Production deployments require TLS, access control, rate limiting, logging minimisation and dependency scanning.

## Data incident response

If restricted data or a secret is committed:

1. revoke the credential immediately ;
2. remove the file ;
3. purge Git history when required ;
4. assess exposure ;
5. notify affected parties when applicable ;
6. document corrective actions.
