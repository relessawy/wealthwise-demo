# WealthWise Demo

A private adaptation of WealthWise for a fictional ACME Bank. The original application is unchanged. The existing Lit/Vaadin interface is retained, with four independently deployable Quarkus services and a dedicated PostgreSQL database.

## Baseline story

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
export RUNNER_IMAGE='<qualified-runner-image>@sha256:<digest>'
bash demo
```

The default command builds/tests in an OpenShift tools pod, builds container images, invokes Ansible/Helm and checks the public API. You do not install Ansible, Galaxy collections, Maven or Java on your laptop. `bash demo verify` repeats API acceptance; `bash demo build` is an optional developer-local Maven build.

Private credentials and execution records stay under `.private/` and in cluster Secrets. Never commit them.

## Scope and gates

Read [VALIDATION.md](VALIDATION.md) for observed evidence and pending checks. Baseline authentication is a **single generated demonstration account**, not the final Keycloak persona integration. Static UI files are public; application APIs require credentials (Quarkus form login with an encrypted HttpOnly session cookie; Basic authentication is also supported for automated checks). History owner identity is supplied by the authenticated frontend and trusted only on restricted internal service links. Cluster administrators remain trusted.

The next milestones are application Keycloak login, portal template/catalog/API/TechDocs/workspace integration, multi-service Jenkins/SonarQube publication, image/SBOM/provenance delivery and GitOps/Service Mesh exercises. No claim is made that these later integrations are active for WealthWise yet. Live AI is an optional future provider, never a silent fallback.

## Source ownership

[UPSTREAM.md](UPSTREAM.md) records the original source commit. No upstream application license was supplied; keep this repository private until redistribution permission is confirmed. Generic database assets are a versioned export from Demo-Library, not a separately maintained implementation.
