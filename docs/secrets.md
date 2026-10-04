# Application secrets with Vault

WealthWise uses Vault for its existing OIDC login credential. Vault Secrets Operator
(VSO) authenticates through the `wealthwise-vault` Kubernetes service account and a
Vault role restricted to one application path. It synchronizes the credential into
`wealthwise-vault-oidc`; the frontend reads its issuer, client ID and client secret
from that Secret at startup. Values do not appear in Developer Hub.

The standalone Vault server uses persistent storage and verified TLS. This demo is
single-node with manual unseal, not a highly available production deployment. Its
private recovery file stays with the platform operator, outside Git and RHDH.

## Developer view

Open this component's **Overview** in RHDH. The **Secrets · Vault** card shows
connection, application authentication, delivery, consumption and rotation evidence.
Unknown means the check has not been demonstrated. Stale means the collector has
not supplied recent evidence. A successful connection does not prove secret access.
Use **Manage cards** to hide or restore Vault, Jenkins, Snyk and Splunk summaries;
**Restore defaults** brings configured cards back. Preferences are personal to this
application in this browser. They do not alter policies or remove detailed tabs.

## Platform operator workflow

The Demo Library `automation/vault` runbook installs the provider, scopes access,
synchronizes the existing credential and switches the Helm `identitySecretName` to
`wealthwise-vault-oidc`. The original `wealthwise-oidc` Secret is retained for an
explicit rollback. Subsequent provisioning reads `wealthwise-vault-integration`
to retain the chosen Secret reference.

VSO refreshes every minute. When secret data changes, its configured rollout target
restarts the frontend so environment variables are reloaded. Rotating the real OIDC
client secret requires coordinating the identity provider and Vault; changing only
one side breaks new logins. Do not run arbitrary rotation commands during a demo.
A rotation verification status must be backed by a new successful login after that
coordinated update; a synchronized version alone is not end-to-end evidence.

## Troubleshooting

- **Vault unavailable:** ask the platform operator to check server readiness and seal status.
- **Authentication or delivery failure:** check the scoped service account, Vault role,
  policy and VSO conditions. Do not grant broader secret access as a workaround.
- **Consumption unknown:** check the deployment's Secret reference and perform a fresh
  application login; a ready pod alone does not establish authentication success.
- **Stale:** check the metadata collector. Treat previous success as historical evidence.

Provider setup: [Demo Library](https://github.com/relessawy/Demo-Library/tree/main/automation/vault).
Reusable card: [custom plugin repository](https://github.com/relessawy/rhdh-custom-plugins/tree/main/plugins/application-health).
