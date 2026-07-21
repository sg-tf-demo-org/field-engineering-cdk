# ai-governance-scan — Trivy-based IaC misconfig + secret + state-posture scanner (one-shot CronJob).
# Mirrors the drift scanner: reuses the cloud-agnostic object_store from the deploy MCP.
#
# Build from the REPO ROOT so object_store.py can be reused from terraform-deploy-mcp:
#   docker buildx build -f governance/trivy/Dockerfile -t <img> .
FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/tmp \
    AI_STORAGE_BACKEND=gcs

ARG TRIVY_VERSION=0.71.1
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl tar \
    && curl -fsSL "https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz" -o /tmp/trivy.tgz \
    && tar -xzf /tmp/trivy.tgz -C /usr/local/bin trivy \
    && rm -f /tmp/trivy.tgz \
    && rm -rf /var/lib/apt/lists/*

COPY governance/trivy/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Reuse the canonical cloud-agnostic storage layer from the deploy MCP.
COPY terraform-deploy-mcp/object_store.py /app/object_store.py
COPY shared/run_ledger.py /app/run_ledger.py
COPY shared/workspace_discovery.py /app/workspace_discovery.py
COPY shared/stack_routes.py /app/stack_routes.py
COPY governance/trivy/severity_map.py governance/trivy/governance_notify.py governance/trivy/governance_scan.py /app/

USER 65534:65534

ENTRYPOINT ["python", "/app/governance_scan.py"]
