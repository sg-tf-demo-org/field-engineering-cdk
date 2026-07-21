"""Governance webhook deduplication, per workspace (mirrors drift/terraform/drift_notify.py).

Keyed on each workspace's set of actionable findings (check id + target + severity) so one workspace
can be remediated/re-alerted independently of others.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

STATE_VERSION = 1


def _workspace_key(ws: dict[str, Any]) -> str:
    return f"{ws.get('s3Path') or ws.get('workspace') or ''}#{ws.get('workingSubdir') or ''}"


def _workspace_fingerprint(ws: dict[str, Any]) -> str:
    parts = []
    for f in sorted(
        (ws.get("findings") or []),
        key=lambda r: (r.get("checkId") or "", r.get("target") or "", r.get("severity") or ""),
    ):
        parts.append((f.get("checkId"), f.get("target"), f.get("severity"), f.get("requirement")))
    blob = json.dumps([_workspace_key(ws), parts], sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def per_workspace_fingerprints(workspaces: list[dict[str, Any]]) -> dict[str, str]:
    return {_workspace_key(ws): _workspace_fingerprint(ws) for ws in workspaces}


def overall_fingerprint(workspaces: list[dict[str, Any]]) -> str:
    per_ws = per_workspace_fingerprints(workspaces)
    blob = json.dumps(sorted(per_ws.items()), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def should_post_webhook(
    *, workspaces: list[dict[str, Any]], stored_state: dict[str, Any] | None, suppress_unchanged: bool
) -> tuple[bool, str, str]:
    """Return (post, reason, fingerprint); POST when any workspace's findings are new/changed."""
    if not workspaces:
        return False, "no_findings", ""
    current = per_workspace_fingerprints(workspaces)
    fp = overall_fingerprint(workspaces)
    if not suppress_unchanged:
        return True, "suppress_disabled", fp
    if not stored_state or stored_state.get("version") != STATE_VERSION:
        return True, "first_run", fp
    stored = stored_state.get("workspaces") or {}
    changed = sorted(w for w, f in current.items() if stored.get(w) != f)
    if changed:
        return True, "findings_changed:" + ",".join(changed), fp
    return False, "unchanged_findings", fp


def build_state_document(*, fingerprint: str, workspaces: list[dict[str, Any]]) -> dict[str, Any]:
    per_ws = per_workspace_fingerprints(workspaces)
    return {
        "version": STATE_VERSION,
        "fingerprint": fingerprint or overall_fingerprint(workspaces),
        "workspaces": per_ws,
        "scannedWorkspaces": sorted(per_ws.keys()),
    }
