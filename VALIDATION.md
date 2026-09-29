# WealthWise identity/catalog milestone — 29 September 2026

Status: **automated identity/catalog acceptance and Alice browser walkthrough verified**. Baseline PR #1 was merged at the user's request; its feature branch was deleted. This milestone is a separate change and does not claim delivery of the later template/CI/mesh stages.

| Check | Observed result |
|---|---|
| Original WealthWise repository | Original commit and all recorded tracked SHA-256 values unchanged |
| Cluster Maven verification | 13 Java tests passed, no failures/errors; issuer/subject isolation tests included |
| Source-transfer boundary | Python test passes: private/ignored files and external symlinks excluded |
| Keycloak client | Separate confidential client; exact callback/logout target; PKCE S256; implicit/password/service-account flows disabled |
| OIDC/API acceptance in runner | 25 checks passed; Alice/Bob code flows, distinct subjects, separate history, anonymous/forged token rejection, retries/conflicts, input checks, cookie protections and logout |
| API contract | Actual deployed OpenAPI registered as a provided API; bearer security documented |
| Catalog | Seven entities accepted: System, four Components, PostgreSQL Resource and API; Alice can read application/API |
| Repeated identity reconciliation | 13 ok, 0 changed, 0 failed |
| Repeated application reconciliation | 14 ok, 0 changed, 0 failed; images/credentials retained |
| Repeated portal compatibility migration | 5 ok, 0 changed, 0 failed; no second rollout |
| Catalog publication | 7 ok, 0 changed, 0 failed; multipart line endings normalized to avoid redundant commits |
| Browser | Alice session, financial answer, Balanced scenario and both History entries observed; callback landing and portal Swagger rendering verified |

The final frontend excludes OIDC/logout routes from SPA routing and marks its XHRs appropriately so expired sessions receive an authentication failure rather than an HTML redirect. Final runtime changes were built in the cluster; the last targeted rebuild replaced only the frontend and retained the already-qualified backend digests. Default provisioning still builds all modules.

A portal allowlist omission initially rejected the database Resource and therefore the catalog package. Demo-Library PR #73 corrects the shared template; an owned-release compatibility playbook preserves deployed Helm values and adds the missing kind. Catalog publication initially committed unchanged data because MIME transport converted LF to CRLF; comparison now normalizes line endings. These failures were fixed before the recorded successful acceptance.

The prior baseline's negative network probes and database/history restart persistence remain historical evidence; they were not re-run or presented as fresh tests in this milestone. Identity and the application were repeat-reconciled, but an entire environment stop/start is not claimed.

## Pending later milestones

- Optional second-persona interactive browser walkthrough; Alice/Bob isolation already passed protocol tests.
- WealthWise software-template repository creation, TechDocs and Dev Spaces profile.
- Jenkins/SonarQube publication for all four modules.
- Images, SBOM/attestation, GitOps promotion and Service Mesh exercises.
- Optional live AI integration. No HA, backup/restore or vendor support certification claim.

`docs/identity-catalog-qualification.json` contains sanitized automated evidence. Secrets and tokens remain outside Git.

The Alice browser walkthrough exposed two issues that automated checks had missed: an authenticated callback could land on an unmapped URL, and the website catalog layout hid the API tab. A protected callback landing resource now redirects to the fixed application root; new acceptance checks verify its redirect and anonymous denial. The Quarkus backend-for-frontend is classified as a service, exposing its API tab. Both corrections were verified in the browser on 29 September 2026.
