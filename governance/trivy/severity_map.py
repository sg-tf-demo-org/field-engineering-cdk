"""Severity gating + Trivy-check-ID → Governance_Configuration requirement mapping.

The Governance scanner runs Trivy ``config`` (IaC misconfiguration) + secret scanning. This module:
  * gates findings by severity (Critical/High drive the self-healing loop), and
  * maps well-known Trivy/AVD check IDs (and titles) to the governance requirement they violate, so
    the Governance Monitor task and the Remediate Security skill can speak in our policy terms.
"""

from __future__ import annotations

from typing import Any

SEVERITY_ORDER = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

# Default gate: Critical/High are actionable; Medium/Low are informational.
DEFAULT_THRESHOLD = "HIGH"

# Trivy/AVD check id (or substring of the check title, lowercased) -> governance requirement key.
# Keep aligned with knowledge-bases/<CLOUD>/Governance_Configuration.md.
CHECK_TO_REQUIREMENT: dict[str, str] = {
    # GCS / storage
    "AVD-GCP-0001": "storage.uniform_bucket_level_access",
    "AVD-GCP-0066": "storage.no_public_access",
    "public-access": "storage.no_public_access",
    # Compute / network
    "AVD-GCP-0031": "compute.no_public_ip",
    "AVD-GCP-0030": "compute.shielded_vm",
    "AVD-GCP-0032": "compute.os_login",
    "AVD-GCP-0035": "network.no_open_ingress",
    "AVD-GCP-0027": "compute.no_serial_port",
    "0.0.0.0/0": "network.no_open_ingress",
    # IAM / keys
    "AVD-GCP-0007": "iam.no_sa_key_creation",
    "AVD-GCP-0011": "iam.no_default_service_account",
    # KMS / encryption
    "AVD-GCP-0064": "kms.rotation_enabled",
    "AVD-GCP-0065": "encryption.cmek_required",
    # Logging
    "AVD-GCP-0040": "logging.audit_logs_enabled",
    # Secrets (trivy secret scanner)
    "generic-secret": "secrets.no_plaintext_secrets",
    "private-key": "secrets.no_plaintext_secrets",
}


def severity_rank(severity: str | None) -> int:
    return SEVERITY_ORDER.get((severity or "UNKNOWN").upper(), 0)


def meets_threshold(severity: str | None, threshold: str = DEFAULT_THRESHOLD) -> bool:
    return severity_rank(severity) >= severity_rank(threshold)


def map_requirement(check_id: str | None, title: str | None = None) -> str | None:
    """Map a Trivy check id (or title substring) to a governance requirement key."""
    if check_id and check_id in CHECK_TO_REQUIREMENT:
        return CHECK_TO_REQUIREMENT[check_id]
    hay = f"{check_id or ''} {title or ''}".lower()
    for key, req in CHECK_TO_REQUIREMENT.items():
        if key.lower() in hay:
            return req
    return None


def classify(findings: list[dict[str, Any]], threshold: str = DEFAULT_THRESHOLD) -> dict[str, Any]:
    """Split findings into actionable (>= threshold) vs informational, with counts by severity."""
    actionable: list[dict[str, Any]] = []
    informational: list[dict[str, Any]] = []
    by_severity: dict[str, int] = {}
    has_critical = False
    for f in findings:
        sev = (f.get("severity") or "UNKNOWN").upper()
        by_severity[sev] = by_severity.get(sev, 0) + 1
        if sev == "CRITICAL":
            has_critical = True
        (actionable if meets_threshold(sev, threshold) else informational).append(f)
    return {
        "actionable": actionable,
        "informational": informational,
        "bySeverity": by_severity,
        "hasCritical": has_critical,
        "actionableCount": len(actionable),
        "threshold": threshold,
    }
