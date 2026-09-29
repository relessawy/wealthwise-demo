# WealthWise baseline implementation handover

This increment provisions a separate four-service application. Environment values are placeholders. It does not alter the original WealthWise checkout or replace the existing portal delivery template.

## Prerequisites

- An OpenShift environment with an authenticated `oc` session and permission to create the isolated namespace and its resources.
- Python 3 for the thin transport launcher. Ansible/Helm and Maven run inside the cluster.
- A reachable, qualified Demo-Library runner image with `kubernetes.core 6.1.0`, Helm and `oc`; supply its immutable digest in `RUNNER_IMAGE`. Provision that runner image using the consultant foundation delivery first if it is absent. The app launcher does not install workstation collections.
- An operational OpenShift internal registry and binary Docker builds. The scoped tools service account can manage this application namespace; the normal builder account builds the images.
- A default RWO StorageClass, or set `STORAGE_CLASS` explicitly.
- Red Hat registry entitlement for the PostgreSQL image. No Artifactory or AI credentials are required for this milestone.

Initial resource requests: 4 application pods × 100m CPU/256Mi, PostgreSQL 500m/1Gi, tools pod 2 containers × 100m/256Mi; one serial image build adds 100m/256Mi. Limits are higher; inspect node usage before provisioning. Persistent storage: database 10Gi plus tools workspace 3Gi. These are initial budgets, not capacity guarantees or an HA design.

## Provision

Clone the new repository and check out the reviewed release or commit. Do not clone over the original application.

```bash
git clone https://github.com/relessawy/wealthwise-demo.git
cd wealthwise-demo
export KUBECONFIG='<path-to-authorized-kubeconfig>'
export RUNNER_IMAGE='<qualified-runner-image>@sha256:<digest>'
export WEALTHWISE_NAMESPACE='wealthwise-demo'
export STORAGE_CLASS='<rwo-storage-class>'
bash demo
```

The launcher first checks namespace ownership. It provisions a scoped tools account, workspace PVC and tools pod, transfers a fresh source directory, and runs Maven verification. The Maven image is pinned by digest. Four serial binary image builds produce immutable runtime references. The Ansible playbook then reconciles PostgreSQL and the application chart and executes API acceptance. No credentials are printed by the launcher.

If the tools image comes from another namespace in this cluster’s internal registry, the launcher creates an image-puller RoleBinding there for this one tools service account. It does not change existing bindings. The tools account has namespace administration because it creates Secrets, workload controllers and Helm releases; it is not cluster-admin. Avoid sharing access to that account with demo participants.

An interrupted invocation can be rerun. A missing/terminal tools pod is recreated, using the workspace PVC. Credential generation occurs only when its owned Secret is missing. Database PVCs are not removed. Helm release values retain the supplied image digests. Do not delete or rename the namespace/PVCs to recover a pod.

## Access and verify

```bash
oc get route wealthwise -n "$WEALTHWISE_NAMESPACE"
umask 077
mkdir -p .private/access
oc get secret wealthwise-access -n "$WEALTHWISE_NAMESPACE"   -o jsonpath='{.data.username}' | base64 --decode > .private/access/username
oc get secret wealthwise-access -n "$WEALTHWISE_NAMESPACE"   -o jsonpath='{.data.password}' | base64 --decode > .private/access/password
bash demo verify
```

On macOS use `base64 -D` if `--decode` is unavailable. Open the HTTPS Route. Select **Sign in** to authenticate with the generated account. Use a private browser window; close it after the exercise. The form session uses a one-hour idle timeout. The encrypted form cookie is Secure, HttpOnly and SameSite=Strict. The baseline is deliberately separate from the portal’s Alice/Bob login. Do not claim Keycloak SSO is implemented for this app.

Ask a financial question, choose each risk level, and open History. Expect explicitly labelled scripted responses and saved entries. The automated acceptance exercises unauthenticated/wrong-password rejection, valid responses, retries without duplicate history, malformed requests, pagination and rejection of client-supplied identity overrides.

## Assets and native operations

- `deploy/provision.yml`: Ansible orchestration and generated credentials.
- `deploy/app/`: application Deployments, internal Services, NetworkPolicies and HTTPS Route.
- `deploy/vendor/roles/postgres/` and `deploy/vendor/charts/postgresql-foundation/`: versioned database implementation from Demo-Library. Provenance is in `deploy/vendor/SOURCE.json`. Change generic logic in Demo-Library, then export a new snapshot.
- `advisor-history/src/main/resources/db/migration/`: Flyway schema migrations. Do not change an already applied migration; add a new version.
- `Containerfile`: shared runtime packaging; each module has distinct Maven coordinates and its own image.
- `scripts/provision.py`: source transfer, build and namespace bootstrap only. Component deployment logic remains Ansible/Helm.

The generated namespace, service-account, RoleBinding, PVC, Pod, ImageStream and BuildConfig definitions are in `scripts/provision.py`. It creates ordinary Kubernetes/OpenShift objects, not custom CRDs. Ansible renders the other YAML from the two versioned charts.

To inspect or rerun deployment inside the tools pod, use the exact run directory recorded by the launcher:

```bash
oc exec -n "$WEALTHWISE_NAMESPACE" wealthwise-tools -c runner --   sh -c 'cd /work/runs/<RUN_ID>/deploy && ansible-playbook provision.yml -e @run-values.json'
```

`run-values.json` contains namespace, storage and image references; password material is held in Secrets. Database credentials use TLS verification with the generated CA. The PostgreSQL role is isolated from RHDH, Keycloak and Artifactory databases.

## Troubleshooting and safe recovery

Inspect `oc get pods,builds -n "$WEALTHWISE_NAMESPACE"`, build logs and application logs. API authentication failure is distinct from a dependency outage: do not disable authentication to diagnose a 503. Check the history service and PostgreSQL readiness. Inspect `/q/health` only through trusted operational access.

For a controlled persistence check, first note a history request ID, restart the history Deployment and database StatefulSet, wait for rollout completion, and verify the same record through the API. Only perform this against the isolated WealthWise namespace.

Cleanup is deliberately not automatic. Deleting the application namespace destroys its database and tools PVCs. Capture any required evidence and obtain explicit approval before destructive cleanup. No Demo1 or existing platform namespace is part of that operation.

## Remaining milestones

Application Keycloak integration and per-persona browser acceptance; portal software template and all related views; SonarQube and multi-module artifact delivery; registry/SBOM/attestation; GitOps and mesh policy/traffic exercises. A live AI provider needs separate configuration and acceptance. This document will be extended at each implemented milestone.
