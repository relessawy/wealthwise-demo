# Existing portal Resource-kind compatibility

For an existing owned Red Hat Developer Hub Helm chart 1.10.4 only. Fresh provisioning with the corrected Demo-Library template already permits Resource entities.

Use the existing platform runner namespace and image (no new privileges are granted):

```bash
export PLATFORM_RUNNER_NAMESPACE='<existing-automation-namespace>'
export RUNNER_IMAGE='<qualified-runner-image>@sha256:<digest>'
export PORTAL_NAMESPACE='<existing-portal-namespace>'
export PORTAL_NAME='<existing-portal-Helm-release>'
python3 scripts/portal_compatibility.py
```

The temporary pod uses the existing `automation-runner` service account. The playbook checks release ownership and exact chart version/checksum, reads retained Helm values, extends catalog rules only if needed and waits for the portal. It preserves existing integrations, policies and Secrets. It deletes only its own temporary compatibility pod after success. On failure the pod remains for diagnosis and exits after its bounded lifetime.

`chart.tgz` is the unchanged qualified 1.10.4 chart exported from Demo-Library commit bbb38a68a41919ae4a2644271e650fbda68c26f4, path automation/vendor/developer-hub/redhat-developer-hub-1.10.4.tgz, SHA-256 de135c957a00ac0a87ef1bf1acc7a57f6f29004bb915262e08f2c0df9a3e8e57. Its upstream license accompanies this directory. This compatibility playbook does not replace the shared Developer Hub provisioning role.
