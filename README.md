# WealthWise Demo

A private adaptation of WealthWise for a fictional ACME Bank. The original application is unchanged. The existing Lit/Vaadin interface is retained, with four independently deployable Quarkus services and a dedicated PostgreSQL database.

## Demo story

Sign in to the demonstration, ask a financial-planning question, select an illustrative investment risk mix, and view persisted history. Responses are deterministic and clearly labelled. **No live AI, model account, Kafka, Serverless or GPU is required.** This is synthetic training material, not a financial-advice product.

```
Browser → HTTPS Route → frontend → financial advisor → history → PostgreSQL
                               ↘ investment advisor ↗
                               ↘ history (read)
```

The frontend uses same-origin APIs; backend Services have no external Routes. NetworkPolicies restrict callers. The dedicated database uses TLS verification, a separate role and Flyway migrations. Request IDs prevent duplicate history entries when a request is retried.

## Start

See [the implementation handover](docs/IMPLEMENTATION.md) for prerequisites and the complete procedure. With `oc` authenticated, Python 3, and the qualified automation runner image configured:

```bash
# Configure identity, portal and runner values using docs/IMPLEMENTATION.md.
bash demo
```

The default command builds/tests in an OpenShift tools pod, builds container images, invokes Ansible/Helm checks Keycloak login/user isolation, and publishes/registers the catalog and API. You do not install Ansible, Galaxy collections, Maven or Java on your laptop. `bash demo verify` repeats API acceptance; `bash demo build` is an optional developer-local Maven build.

Private credentials and execution records stay under `.private/` and in cluster Secrets. Never commit them.

## Scope and gates

Read [VALIDATION.md](VALIDATION.md) for observed evidence and pending checks. WealthWise uses the existing Keycloak realm through a separate confidential client with PKCE. Alice and Bob have separate history, bound to their verified issuer/subject. Static UI files are public; APIs require an OIDC session or valid token. Sign out ends the shared identity session. The old generated `demo` account is no longer active.

Developer Hub contains the WealthWise system, four components, PostgreSQL Resource and real API contract. Generated catalog metadata lives in a private Bitbucket repository; application source remains here. Consultant commands and native assets are in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md).

Software-template creation, TechDocs/workspaces, multi-service Jenkins/SonarQube, image/SBOM/provenance and GitOps/mesh remain subsequent milestones. Live AI is optional future work, never a silent fallback.

## Source ownership

[UPSTREAM.md](UPSTREAM.md) records the original source commit. No upstream application license was supplied; keep this repository private until redistribution permission is confirmed. Generic database assets are a versioned export from Demo-Library, not a separately maintained implementation.

### Separate environment catalog

Set `WEALTHWISE_CATALOG_REPOSITORY=demo2-wealthwise-catalog` before `bash demo all`
when provisioning another environment in the same Bitbucket workspace. Publication
and RHDH registration use that repository together. The default remains
`wealthwise-demo-catalog`; use a new name to avoid updating the first environment.
