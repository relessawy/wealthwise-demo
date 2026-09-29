FROM registry.access.redhat.com/ubi9/openjdk-21-runtime@sha256:14e5af876865b25abdc15c137dd30e68b3394aaee18e26bd1777036a52a907c5
WORKDIR /deployments
COPY --chown=185:0 quarkus-app/ /deployments/
USER 185
ENV JAVA_APP_JAR=/deployments/quarkus-run.jar
EXPOSE 8080
