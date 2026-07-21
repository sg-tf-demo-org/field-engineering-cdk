"""Trivy "Governance" scanner — IaC misconfiguration + secrets + state-derived posture.

Mirrors the drift monitor: discovers plan-validated workspaces (GOVERNANCE_DISCOVERY_URIS, falling
back to DRIFT_DISCOVERY_URIS), downloads each, runs Trivy ``config`` (IaC misconfig) and secret
scanning offline (no CVE DB), adds a light state-derived posture check, gates by severity, writes
``governance-findings.json``/``.md`` back to the workspace prefix, and POSTs a batched payload to the
Governance Aiden task. Checkov CSPM is left entirely untouched.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import object_store
from governance_notify import build_state_document, should_post_webhook
from severity_map import classify, map_requirement

try:  # best-effort run ledger
    import run_ledger
except Exception:  # noqa: BLE001
    run_ledger = None  # type: ignore

PLAN_MARKER_NAME = ".ai-plan-validated.json"

WEBHOOK_URL = (os.environ.get("WEBHOOK_URL") or "").strip()
WEBHOOK_SUPPRESS_UNCHANGED = (os.environ.get("WEBHOOK_SUPPRESS_UNCHANGED") or "true").strip().lower() in ("1", "true", "yes")
WEBHOOK_PING_ON_EMPTY = (os.environ.get("WEBHOOK_PING_ON_EMPTY") or "false").strip().lower() in ("1", "true", "yes")
SEVERITY_THRESHOLD = (os.environ.get("GOVERNANCE_SEVERITY_THRESHOLD") or "HIGH").strip().upper()
GOVERNANCE_STATE_URI = (os.environ.get("GOVERNANCE_STATE_URI") or "").strip()
TRIVY_BIN = os.environ.get("TRIVY_BIN", "trivy")
TRIVY_TIMEOUT_SEC = int(os.environ.get("GOVERNANCE_TRIVY_TIMEOUT_SEC", "300"))


# --------------------------------------------------------------------------- #
# Webhook
# --------------------------------------------------------------------------- #
ROUTING_ENABLED = bool((os.environ.get("DEPLOY_QUEUE_URL") or "").strip())


def _post_webhook(payload: dict[str, Any], *, timeout_sec: int = 60, url: str | None = None) -> tuple[int, str]:
    target = url or WEBHOOK_URL
    if not target:
        return 0, "no webhook url"
    body = json.dumps(payload, default=str).encode("utf-8")
    req = urllib.request.Request(target, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.getcode(), (resp.read() or b"").decode("utf-8", errors="replace")[:2000]
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b"").decode("utf-8", errors="replace")[:2000]
    except urllib.error.URLError as e:
        return 0, str(e.reason)


def _gov_webhook_for(s3_path: str) -> str | None:
    if not ROUTING_ENABLED:
        return WEBHOOK_URL or None
    try:
        import stack_routes

        return stack_routes.match_webhook(s3_path, "gov") or (WEBHOOK_URL or None)
    except Exception:  # noqa: BLE001
        return WEBHOOK_URL or None


# --------------------------------------------------------------------------- #
# Discovery (plan-validated workspace env roots)
# --------------------------------------------------------------------------- #
def _list_keys(*, cloud: str, bucket: str, prefix: str, region: str | None) -> list[str]:
    keys: list[str] = []
    from google.cloud import storage as gcs  # type: ignore

    for blob in gcs.Client().list_blobs(bucket, prefix=prefix):
        if blob.name and not blob.name.endswith("/"):
            keys.append(blob.name)
    return keys


def _discovered_workspaces() -> list[dict[str, Any]]:
    import workspace_discovery

    raw = os.environ.get("GOVERNANCE_DISCOVERY_URIS") or os.environ.get("DRIFT_DISCOVERY_URIS") or ""
    parts = [raw] if raw else []
    try:
        import stack_routes

        parts += stack_routes.discovery_uris()
    except Exception:  # noqa: BLE001
        pass
    return workspace_discovery.discover_workspaces(
        discovery_uris=",".join(p for p in parts if p),
        list_keys=_list_keys,
        region=object_store.gcs_location(),
    )


def _explicit_workspaces() -> list[dict[str, Any]]:
    raw = (os.environ.get("GOVERNANCE_WORKSPACES") or "").strip()
    if not raw:
        return []
    out: list[dict[str, Any]] = []
    for it in json.loads(raw):
        s3_path = (it.get("s3_path") or it.get("s3Path") or "").strip()
        if s3_path:
            out.append({
                "s3_path": s3_path,
                "working_subdir": (it.get("working_subdir") or it.get("workingSubdir") or "").strip() or None,
                "region": (it.get("region") or "").strip() or None,
            })
    return out


# --------------------------------------------------------------------------- #
# Trivy
# --------------------------------------------------------------------------- #
def _run_trivy(args: list[str]) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            [TRIVY_BIN, *args], capture_output=True, text=True, timeout=TRIVY_TIMEOUT_SEC,
            env={**os.environ, "TRIVY_DISABLE_VEX_NOTICE": "true"},
        )
    except FileNotFoundError:
        return {"ok": False, "error": "trivy binary not installed"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"trivy timed out after {TRIVY_TIMEOUT_SEC}s"}
    if not (proc.stdout or "").strip():
        return {"ok": proc.returncode == 0, "results": [], "stderr": (proc.stderr or "")[-1000:]}
    try:
        return {"ok": True, "doc": json.loads(proc.stdout)}
    except json.JSONDecodeError:
        return {"ok": False, "error": "trivy produced non-JSON output", "stderr": (proc.stderr or "")[-1000:]}


def _trivy_findings(scan_dir: Path) -> list[dict[str, Any]]:
    """Run Trivy config (misconfig) + secret scans on a workspace dir; return normalized findings."""
    findings: list[dict[str, Any]] = []
    # IaC misconfiguration (bundled policies; no network needed).
    cfg = _run_trivy(["config", "--quiet", "--format", "json", "--severity", "CRITICAL,HIGH,MEDIUM,LOW", str(scan_dir)])
    for res in (cfg.get("doc") or {}).get("Results", []) if cfg.get("ok") else []:
        target = res.get("Target") or ""
        for mc in res.get("Misconfigurations") or []:
            check_id = mc.get("AVDID") or mc.get("ID") or ""
            title = mc.get("Title") or ""
            findings.append({
                "scanner": "misconfig",
                "checkId": check_id,
                "title": title,
                "severity": (mc.get("Severity") or "UNKNOWN").upper(),
                "target": target,
                "message": mc.get("Message") or mc.get("Description") or "",
                "resolution": mc.get("Resolution") or "",
                "requirement": map_requirement(check_id, title),
            })
    # Secret scanning (bundled rules).
    sec = _run_trivy(["fs", "--scanners", "secret", "--quiet", "--format", "json", str(scan_dir)])
    for res in (sec.get("doc") or {}).get("Results", []) if sec.get("ok") else []:
        target = res.get("Target") or ""
        for s in res.get("Secrets") or []:
            rule = s.get("RuleID") or "secret"
            findings.append({
                "scanner": "secret",
                "checkId": rule,
                "title": s.get("Title") or "Exposed secret",
                "severity": (s.get("Severity") or "CRITICAL").upper(),
                "target": target,
                "message": f"{s.get('Title') or 'secret'} at line {s.get('StartLine')}",
                "requirement": map_requirement(rule, s.get("Title")),
            })
    return findings


def _state_posture(*, cloud: str, bucket: str, state_key: str, region: str | None) -> list[dict[str, Any]]:
    """Light state-derived posture: flag risky live attributes recorded in the tfstate."""
    got = object_store.get_text(cloud=cloud, bucket=bucket, key=state_key, region=region)
    if not got.get("ok"):
        return []
    try:
        doc = json.loads(got.get("text") or "{}")
    except json.JSONDecodeError:
        return []
    findings: list[dict[str, Any]] = []
    blob = json.dumps(doc)
    if '"0.0.0.0/0"' in blob:
        findings.append({
            "scanner": "state-posture", "checkId": "STATE-OPEN-INGRESS", "title": "Open ingress in live state",
            "severity": "HIGH", "target": state_key, "message": "Live state contains a 0.0.0.0/0 source range.",
            "requirement": "network.no_open_ingress",
        })
    for res in doc.get("resources") or []:
        if res.get("type") == "google_compute_instance":
            for inst in res.get("instances") or []:
                attrs = inst.get("attributes") or {}
                for ni in attrs.get("network_interface") or []:
                    if ni.get("access_config"):
                        findings.append({
                            "scanner": "state-posture", "checkId": "STATE-PUBLIC-IP",
                            "title": "VM with external IP in live state", "severity": "HIGH",
                            "target": f"{res.get('type')}.{res.get('name')}",
                            "message": "Compute instance has an external access_config (public IP).",
                            "requirement": "compute.no_public_ip",
                        })
    return findings


# --------------------------------------------------------------------------- #
# Per-workspace scan
# --------------------------------------------------------------------------- #
def _backend_state_uri(ws_dir: Path) -> tuple[str, str, str] | None:
    for name in ("backend.tf", "backend.tf.json"):
        bf = ws_dir / name
        if not bf.is_file():
            continue
        text = bf.read_text(encoding="utf-8")
        if name.endswith(".json"):
            try:
                be = ((json.loads(text).get("terraform") or {}).get("backend") or {})
            except json.JSONDecodeError:
                continue
            gcs = be.get("gcs") or {}
            if gcs.get("bucket") and gcs.get("prefix") is not None:
                return ("gcp", gcs["bucket"], f"{str(gcs['prefix']).strip('/')}/default.tfstate")
        else:
            mb = re.search(r'bucket\s*=\s*"([^"]+)"', text)
            mp = re.search(r'prefix\s*=\s*"([^"]+)"', text)
            if re.search(r'backend\s+"gcs"', text) and mb and mp:
                return ("gcp", mb.group(1), f"{mp.group(1).strip('/')}/default.tfstate")
            mk = re.search(r'key\s*=\s*"([^"]+)"', text)
            if mb and mk:
                return ("aws", mb.group(1), mk.group(1))
    return None


def _scan_workspace(ws: dict[str, Any], tmp_root: Path) -> dict[str, Any]:
    cloud, bucket, key = object_store.parse_uri(ws["s3_path"])
    prefix = key if key.endswith("/") else key + "/"
    region = ws.get("region")
    local = tmp_root / re.sub(r"[^a-zA-Z0-9._-]+", "-", prefix.strip("/"))[:120]
    if local.exists():
        shutil.rmtree(local, ignore_errors=True)
    local.mkdir(parents=True, exist_ok=True)
    object_store.download_prefix(cloud=cloud, local_dir=local, bucket=bucket, prefix=prefix, region=region)

    sub = (ws.get("working_subdir") or "").strip("/")
    scan_dir = (local / sub) if sub else local
    findings = _trivy_findings(scan_dir if scan_dir.is_dir() else local)

    state = _backend_state_uri(scan_dir if scan_dir.is_dir() else local)
    state_path = None
    if state:
        scloud, sbucket, skey = state
        state_path = object_store.make_uri(scloud, sbucket, skey)
        findings += _state_posture(cloud=scloud, bucket=sbucket, state_key=skey, region=region)

    gated = classify(findings, SEVERITY_THRESHOLD)
    actionable = gated["actionable"]

    # Write findings artifacts back to the workspace prefix.
    artifacts_prefix = f"{prefix}{sub + '/' if sub else ''}"
    summary = {
        "workspace": ws["s3_path"],
        "workingSubdir": ws.get("working_subdir"),
        "statePath": state_path,
        "threshold": SEVERITY_THRESHOLD,
        "bySeverity": gated["bySeverity"],
        "actionableCount": gated["actionableCount"],
        "hasCritical": gated["hasCritical"],
        "findings": findings,
    }
    object_store.upload_text(
        cloud=cloud, text=json.dumps(summary, indent=2, default=str),
        bucket=bucket, key=f"{artifacts_prefix}governance-findings.json", region=region,
    )
    object_store.upload_text(
        cloud=cloud, text=_findings_markdown(summary), bucket=bucket,
        key=f"{artifacts_prefix}governance-findings.md", region=region,
    )

    return {
        "s3Path": ws["s3_path"],
        "workspace": ws["s3_path"],
        "workingSubdir": ws.get("working_subdir"),
        "region": region,
        "statePath": state_path,
        "bySeverity": gated["bySeverity"],
        "hasCritical": gated["hasCritical"],
        "findings": actionable,  # dedup + webhook only on actionable (>= threshold) findings
        "allFindingCount": len(findings),
    }


def _findings_markdown(summary: dict[str, Any]) -> str:
    lines = [
        f"# Governance findings — {summary['workspace']}",
        "",
        f"Working dir: `{summary.get('workingSubdir')}`  ·  threshold: **{summary['threshold']}**",
        f"By severity: {summary['bySeverity']}  ·  actionable: **{summary['actionableCount']}**"
        + ("  ·  ⚠️ CRITICAL present" if summary["hasCritical"] else ""),
        "",
    ]
    for f in summary["findings"]:
        req = f" → `{f['requirement']}`" if f.get("requirement") else ""
        lines.append(f"- **[{f['severity']}]** `{f.get('checkId')}` {f.get('title')}{req}  ({f.get('target')})")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# State (dedup) persistence
# --------------------------------------------------------------------------- #
def _load_state() -> dict[str, Any] | None:
    if not GOVERNANCE_STATE_URI:
        return None
    cloud, bucket, key = object_store.parse_uri(GOVERNANCE_STATE_URI)
    got = object_store.get_text(cloud=cloud, bucket=bucket, key=key, region=object_store.gcs_location())
    if not got.get("ok"):
        return None
    try:
        return json.loads(got.get("text") or "{}")
    except json.JSONDecodeError:
        return None


def _save_state(doc: dict[str, Any]) -> None:
    if not GOVERNANCE_STATE_URI:
        return
    cloud, bucket, key = object_store.parse_uri(GOVERNANCE_STATE_URI)
    object_store.upload_text(
        cloud=cloud, text=json.dumps(doc, indent=2, default=str), bucket=bucket, key=key,
        region=object_store.gcs_location(),
    )


def main() -> dict[str, Any]:
    import workspace_discovery

    workspaces = workspace_discovery.merge_workspaces(_explicit_workspaces(), _discovered_workspaces())
    errors: list[dict[str, Any]] = []
    scanned: list[dict[str, Any]] = []
    tmp_root = Path(tempfile.mkdtemp(prefix="governance-"))
    try:
        for ws in workspaces:
            try:
                result = _scan_workspace(ws, tmp_root)
                scanned.append(result)
            except Exception as e:  # noqa: BLE001
                errors.append({"workspace": ws.get("s3_path"), "error": str(e)})
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

    with_findings = [w for w in scanned if w.get("findings")]

    if run_ledger is not None:
        for w in scanned:
            try:
                run_ledger.emit(
                    "governance_scan", intent=run_ledger.intent_from_path(w.get("s3Path")),
                    source="ai-governance-scan", artifactPath=w.get("s3Path"),
                    workingSubdir=w.get("workingSubdir"), bySeverity=w.get("bySeverity"),
                    hasCritical=w.get("hasCritical"), actionableCount=len(w.get("findings") or []),
                )
            except Exception:  # noqa: BLE001
                pass

    posted = 0
    skip_reason: str | None = None
    fingerprint: str | None = None
    if with_findings:
        post, skip_reason, fp = should_post_webhook(
            workspaces=with_findings, stored_state=_load_state(), suppress_unchanged=WEBHOOK_SUPPRESS_UNCHANGED
        )
        fingerprint = fp or None
        if not post:
            _save_state(build_state_document(fingerprint=fp, workspaces=with_findings))
        elif not WEBHOOK_URL and not ROUTING_ENABLED:
            errors.append({"webhook": "WEBHOOK_URL not configured"})
        else:
            # Group findings by per-stack Governance webhook (fallback: global WEBHOOK_URL).
            groups: dict[str | None, list[dict[str, Any]]] = {}
            for w in with_findings:
                url = _gov_webhook_for(w.get("s3Path") or w.get("statePath") or "")
                groups.setdefault(url, []).append(w)
            any_ok = False
            for target_url, group in groups.items():
                if not target_url:
                    continue
                names = [w.get("statePath") or w.get("s3Path") for w in group]
                body = {
                    "source": "ai-governance-scan",
                    "findingType": "cspm",
                    "findingTypeLegacy": "governance",
                    "scanner": "trivy",
                    "webhookBatch": True,
                    "stackName": names[0] if len(names) == 1 else ", ".join(n for n in names if n)[:900],
                    "stack_name": names[0] if len(names) == 1 else ", ".join(n for n in names if n)[:900],
                    "workspaceCount": len(group),
                    "hasCritical": any(w.get("hasCritical") for w in group),
                    "threshold": SEVERITY_THRESHOLD,
                    "findingWorkspaces": group,
                }
                code, snip = _post_webhook(body, url=target_url)
                posted += 1
                if 200 <= code < 300:
                    any_ok = True
                else:
                    errors.append({"webhookHttpStatus": code, "webhookResponsePreview": snip, "url": target_url})
                print(f"governance webhook POST -> HTTP {code}: {snip[:300]}", file=sys.stderr)
            if any_ok:
                _save_state(build_state_document(fingerprint=fp, workspaces=with_findings))
    elif WEBHOOK_PING_ON_EMPTY and scanned and WEBHOOK_URL:
        # No actionable (>= threshold) findings — still notify Aiden so the Governance task
        # shows each Trivy scan cycle (mirrors drift WEBHOOK_PING_ON_EMPTY for visibility).
        body = {
            "source": "ai-governance-scan",
            "findingType": "cspm",
            "findingTypeLegacy": "governance",
            "scanner": "trivy",
            "webhookBatch": True,
            "scanComplete": True,
            "scannedWorkspaceCount": len(scanned),
            "workspaceCount": 0,
            "findingWorkspaces": [],
            "threshold": SEVERITY_THRESHOLD,
            "hasCritical": False,
            "scannedWorkspaces": [
                {
                    "workspace": w.get("s3Path") or w.get("s3_path"),
                    "workingSubdir": w.get("workingSubdir"),
                    "bySeverity": w.get("bySeverity"),
                    "actionableCount": len(w.get("findings") or []),
                }
                for w in scanned
            ],
            "note": f"Trivy governance scan complete — no actionable findings at or above {SEVERITY_THRESHOLD}",
        }
        code, snip = _post_webhook(body)
        posted = 1 if 200 <= code < 300 else 0
        if not (200 <= code < 300):
            errors.append({"webhookHttpStatus": code, "webhookResponsePreview": snip})
        print(f"governance clean-scan webhook POST -> HTTP {code}: {snip[:300]}", file=sys.stderr)
    elif not with_findings and not scanned:
        skip_reason = "no_workspaces_discovered"

    result = {
        "ok": True,
        "scannedWorkspaceCount": len(scanned),
        "workspacesWithFindings": len(with_findings),
        "webhookPosted": posted,
        "webhookSkipReason": skip_reason,
        "fingerprint": fingerprint,
        "errors": errors,
    }
    print(json.dumps(result, default=str))
    return result


if __name__ == "__main__":
    main()
