# Security delivery baseline

The optional `security-image` Maven profile builds an image archive for scanning
before publication. The qualification pipeline scans source and Maven dependencies,
runs all module tests, builds the frontend image, converts it to OCI format and
scans the archive. High/critical findings and scan errors block publication.

The application uses Quarkus 3.27.5.3, Jackson 2.21.7 and Parsson 1.1.8. Jackson
and Parsson are explicit dependency-management overrides for the recorded security
findings; review them when advancing the Quarkus platform. The platform update
retains Java 21 and the existing Quarkus 3.27 release line.

The security profile pins Eclipse Temurin 21 JRE Alpine for linux/amd64:
`sha256:bec16bceecb1a89defa333c77ac76d29a6b0d59fcb4f50218b476efa68e30bb4`.
This is a community Temurin runtime, not a Red Hat runtime. Existing deployment
charts and their image selections are not changed by enabling a Maven profile.

On 30 September 2026, Jenkins qualification build 9 passed all four modules' tests,
reported zero Maven dependency and container findings, and published the scanned
frontend image. Source analysis retained 14 medium findings in administration
scripts; these remain review items and are not presented as zero findings.
The exact published image passed OpenShift runtime readiness in an isolated pod.
These observations are time-bound; rerun scans for each delivered revision.

The evaluated old Red Hat UBI runtime had 104 high findings. An updated UBI runtime
reduced that to 11 and a Debian distroless alternative to two; both remained blocked.
No exclusions or reduced thresholds were used to obtain a passing release.

The pipeline archives full scan results and the published digest. The frontend
image does not by itself certify the other three service images or constitute
application promotion. Their deployed image digests remain separately managed.
