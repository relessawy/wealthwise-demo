# WealthWise identity and catalog implementation handover

This increment builds the separate four-service application, connects it to an existing Keycloak realm, and registers its system, services, database and actual OpenAPI contract in Developer Hub. All environment values below are placeholders. The original WealthWise checkout and the existing portal software templates are unchanged.

## Prerequisites and capacity

- An authenticated `oc` session and Python 3. The launcher uses Python's standard library; Maven, Java, Ansible, Galaxy collections and HTTP verification dependencies run in OpenShift.
- A qualified immutable automation runner image with `kubernetes.core 6.1.0`, Helm, Git, `oc` and Python requests. Use the consultant foundation delivery to provision it when absent.
- OpenShift internal registry/binary Docker builds, a default RWO StorageClass and entitlement to the qualified Red Hat PostgreSQL image.
- Existing owned Keycloak service, realm and personas (Alice, Bob and Carol), provisioned by the identity foundation. This increment creates only a separate application client. It does not change realm settings, user passwords, groups or the portal client.
- Existing Developer Hub with working private Bitbucket integration, catalog registration permission for Carol and catalog read permission for Alice. Catalog rules must include **Resource**, in addition to System, Component and API. The shared Demo-Library portal template includes this correction (PR #73, commit `12face8c45b7b95663603e663738db3969b0e049`); existing releases need the compatibility update described below.

Application requests: 4 × 100m CPU/256Mi; PostgreSQL 500m/1Gi; tools pod 2 × 100m/256Mi. One serial image build adds 100m/256Mi. Database PVC 10Gi; tools PVC 3Gi. These are incremental requests, not a capacity guarantee. Keycloak, the portal and their databases already exist and require their own capacity. No HA or backup/restore scope is implied.

## Configure and run

Clone the new repository outside the original checkout and select the reviewed tag:

```bash
git clone https://github.com/relessawy/wealthwise-demo.git
cd wealthwise-demo
git fetch origin --tags
git switch --detach <REVIEWED_TAG>
export KUBECONFIG='<path-to-authorized-kubeconfig>'
export RUNNER_IMAGE='<qualified-runner-image>@sha256:<digest>'
export WEALTHWISE_NAMESPACE='<owned-application-namespace>'
export STORAGE_CLASS='<rwo-storage-class>'
export IDENTITY_NAMESPACE='<identity-namespace>'
export IDENTITY_NAME='<identity-service-and-route-name>'
export IDENTITY_REALM='<existing-realm>'
export PORTAL_NAMESPACE='<developer-hub-namespace>'
export PORTAL_NAME='<developer-hub-release-and-route-name>'
bash demo
```

One default command runs modular stages: source transfer, client reconciliation, Maven tests, four image builds, PostgreSQL/application Helm reconciliation, OIDC acceptance, private catalog publication and portal registration/acceptance. Optional commands:

```bash
bash demo apply    # Application and identity stages, including application acceptance
bash demo verify   # Application OIDC and API acceptance only
bash demo onboard  # Publish/register/verify catalog only; no application rebuild
bash demo build    # Optional developer-local Maven build
```

The tools service account manages only the application namespace. If its image resides in another internal-registry namespace, the launcher adds one scoped image-puller binding. The user's `oc` session reads existing foundation Secrets. Administrative inputs enter Ansible through stdin and a mode-0600 temporary file removed on normal exit/signals. They are not committed, printed or written to evidence. The application receives only its own client credential. Verification uses existing synthetic persona credentials in memory through stdin. Do not grant participants access to the automation account.

## Identity behavior

`deploy/identity.yml` owns client `wealthwise-<application-namespace>` and Secret `wealthwise-oidc`. The client is confidential, uses authorization code flow with PKCE S256, and permits exactly `https://<application-route>/oidc/callback`. Implicit flow, password grants and service accounts are disabled. Logout permits return only to the application root. TLS verification remains enabled for Keycloak and Bitbucket requests.

The frontend accepts its OIDC session or a valid bearer token for this client. Issuer/signature/audience validation is performed by Quarkus. Secure HttpOnly cookies protect the session; API XHR requests receive an authentication failure instead of an HTML login page. The visible sign-in link starts the top-level code flow. Sign-out ends the application/Keycloak session; logging out of the shared identity provider can also affect subsequent sign-in to other applications.

The callback also has a protected landing resource that redirects authenticated requests to the application root. This prevents a completed login from ending on an unmapped callback page and removes authorization parameters from the displayed URL. It does not process codes itself or bypass Quarkus authentication.

The history owner is SHA-256 of the verified issuer and subject, not a supplied username/header. This remains stable if a username changes and separates identical subjects across realms. Alice and Bob have separate history. Internal services trust the authenticated frontend's identity only within their restricted NetworkPolicy boundary; cluster administrators remain trusted. Full end-to-end service identity is a later mesh milestone.

The old baseline Secret `wealthwise-access` may remain on an upgraded installation, but no current Deployment references it and Basic/form password authentication is removed. Old `demo` history is retained in PostgreSQL and is not reassigned to Alice or Bob. No data migration or deletion is performed.

## Demonstrate and validate

```bash
oc get route wealthwise -n "$WEALTHWISE_NAMESPACE"
bash demo verify
```

1. Open the HTTPS Route and choose **Sign in with your bank account**. Use the existing Alice credentials from the identity handover, not the retired baseline `demo` account.
2. Ask an illustrative household-budget question. The response must explicitly identify itself as a scripted demonstration.
3. Choose Conservative, Balanced and Aggressive investment scenarios. Open History and confirm the saved entries.
4. Sign out. In a separate/private browser session sign in as Bob and confirm Alice's entries are absent.
5. Open Developer Hub, search **WealthWise**, and inspect Overview, API and Dependencies. The System groups the frontend, financial/investment/history services and PostgreSQL Resource. The API tab has the actual deployed OpenAPI definition.
6. For live API interaction, sign in to WealthWise and use its **Interactive API explorer** link at `/q/swagger-ui/`; same-origin requests can use the existing application session. The portal API tab's cross-origin “Try it out” behavior is not accepted by this increment.

Automated checks cover code flow/PKCE, Alice/Bob identities, separate history, forged tokens, anonymous denial, retries/conflicts, risk choices, malformed requests, cookie protections, OpenAPI and logout. Browser-rendered interaction is a separate acceptance gate; see VALIDATION.md.

## Catalog source and maintenance

Application source remains authoritative in the private `wealthwise-demo` GitHub repository. Ansible publishes only a generated `catalog-info.yaml` and README to a separate private `wealthwise-demo-catalog` repository in the portal's configured Bitbucket workspace/project. This is a catalog delivery artifact, not a second application implementation. It contains URLs and the public API contract, never credentials.

Catalog source and handover links are pinned to the release in `VERSION`. The versioned Jinja template is `catalog/catalog.yaml.j2`; `deploy/catalog.yml` supplies actual environment values and reads the deployed OpenAPI document. Registration is idempotent for the exact location URL. Repeat publication compares content before committing. The catalog is stored persistently by the existing portal; foundation recreation requires rerunning `bash demo onboard`.

The frontend is catalogued as a `service`: it is a Quarkus backend-for-frontend serving both the web interface and authenticated API. The portal's service layout exposes its provided API; a `website` classification uses a layout without that tab. After changing existing metadata, schedule an entity refresh and reload the component page.

No TechDocs, CI, topology, Quay or Argo CD annotations are added to imply unfinished integrations. The handover and application links work independently of those later plugins. The existing generic Jenkins template remains available and unchanged.

## Native assets and operations

- `deploy/identity.yml`: owned Keycloak client and application Secret.
- `deploy/provision.yml`: shared PostgreSQL role and application Helm release.
- `deploy/app/templates/application.yaml`: four Deployments, internal Services, NetworkPolicies and one HTTPS Route.
- `deploy/vendor/roles/postgres/` and `deploy/vendor/charts/postgresql-foundation/`: versioned generic database export; provenance in `deploy/vendor/SOURCE.json`.
- `advisor-history/src/main/resources/db/migration/`: Flyway migrations; add a new migration instead of editing an applied one.
- `deploy/catalog.yml` and `catalog/catalog.yaml.j2`: generated private Bitbucket catalog package.
- `scripts/`: thin `oc` transport and API acceptance; component reconciliation remains Ansible/Helm.

These application assets create ordinary Kubernetes/OpenShift objects, not new CRDs. Keycloak Operator CRDs belong to the prerequisite identity foundation. To render/inspect native YAML or repeat the application deployment inside the runner:

```bash
oc exec -n "$WEALTHWISE_NAMESPACE" wealthwise-tools -c runner -- \
  sh -c 'cd /work/runs/<RUN_ID>/deploy && helm template wealthwise app -f run-values.json'
oc exec -n "$WEALTHWISE_NAMESPACE" wealthwise-tools -c runner -- \
  sh -c 'cd /work/runs/<RUN_ID>/deploy && ansible-playbook provision.yml -e @run-values.json'
```

Use the exact run ID reported by the launcher. Advanced targeted rebuilds may set `WEALTHWISE_BUILD_MODULES=ww-frontend`; this reuses the existing owned backend ImageStream digests and must only be used when those backend sources are unchanged. The default rebuilds all four modules. The namespace argument is supplied by Ansible on deployment; rendered YAML can omit metadata.namespace. Database credentials use verify-full TLS with the mounted CA. Evidence is retrieved to `.private/acceptance/` and `.private/runs/`; it contains no passwords/tokens.

## Existing portal compatibility

Older portal templates omitted `Resource` from `catalog.rules`, causing a mixed catalog package to fail processing. Reconcile the updated shared Developer Hub role, or use the reviewed compatibility playbook delivered with this application. It reads the existing Helm values, checks ownership/chart version, preserves all values, and adds `Resource` only when missing. Run it with the existing authorized platform runner, not the application service account. Its native playbook and README are in `deploy/portal-compatibility/`.

## Recovery and limits

Rerun the same command after an interrupted run. Missing/failed tools pods are recreated against the existing tools PVC. Application client credentials and database PVCs are retained. Do not delete namespaces/PVCs to recover a pod. Cleanup remains separate and requires explicit authorization.

Database/history pod restart persistence was accepted in the baseline; repeat provisioning and identity isolation are tested in this increment. An environment-wide stop/start for this new application is not yet accepted.

Next milestones: create a versioned WealthWise software template and repository delivery; publish TechDocs and a persistent development profile; extend Jenkins/SonarQube to all modules; build images/SBOM/attestation; GitOps promotion and mesh exercises. A live AI provider remains optional and explicitly separate.

OIDC design reference: https://quarkus.io/guides/security-oidc-code-flow-authentication/
