# WealthWise baseline validation — 29 September 2026

Status: **automated baseline verified; authenticated browser journey pending user sign-in**. This is a review candidate, not acceptance of the later portal/GitOps/mesh milestones.

| Check | Observed result |
|---|---|
| Original repository and tracked source | Commit and every recorded file SHA-256 unchanged |
| Four-module build in OpenShift | Maven verify passed; 10 Java tests, zero failures/errors |
| Source transfer boundary | Python test passed: ignored credentials, private files and external symlinks excluded |
| Container delivery | Four images built in the isolated namespace; immutable digests passed to Helm; base image pinned by digest |
| Ansible deployment | PostgreSQL role/chart reused; application chart deployed successfully |
| Public API acceptance | 14 checks passed: missing/bad auth, deterministic answers, all risk choices, duplicate/conflicting requests, malformed input, pagination and identity override |
| Form authentication | Login succeeds; session grants API access; cookie Secure, HttpOnly, SameSite=Strict |
| Network isolation | Unlabelled tools pod timed out against both advisors, history and PostgreSQL; authenticated application flow succeeds |
| Unchanged Ansible reconciliation | Passed with 14 ok, 0 changed, 0 failed; generated credentials were retained |
| Persistence | Recorded history remained after PostgreSQL StatefulSet and history Deployment restarts |
| UI | Application and login form render in the browser; signed-in question/risk/history navigation awaits browser sign-in |

The final source uses Java 21, Quarkus 3.27.3, web-bundler 2.2.1 and PostgreSQL 16. Version compatibility was exercised by these builds and runtime checks; no comprehensive vulnerability scan or Red Hat support certification is claimed.

The old UI bundler failed against the newer Quarkus API and was upgraded. Invalid embedded Secret resources and stale scaffold tests were replaced. UI history registration, routing, error states and responsive header were corrected. A Qute inline-CSS build failure was fixed before deployment. These failures are not accepted as passing tests.

The browser automation tool blocks Terminal access used for private credential transfer; the user has been asked to sign in through the ordinary form. No workstation controls were disabled. The authenticated browser journey remains explicitly pending.

## Not delivered in this baseline

- WealthWise Keycloak/Alice/Bob integration and application persona acceptance.
- Portal template, API/TechDocs/workspace/catalog onboarding for WealthWise.
- Jenkins/SonarQube artifact publication for the four modules.
- SBOM, attestation, GitOps deployment/promotion, mesh traffic/security exercises.
- Live AI provider integration, event-driven history, HA, backup or restore.

These are separate milestones, not implied by the working qualification application.
