# Aiden governance scan engine

The single, shared **scan gate** used at every step of the six-step IaC lifecycle.
CDK is always synthesized to CloudFormation first (`synth-cdk.sh`), then the resulting
templates go through the exact same gate as hand-written CloudFormation (`scan-cfn.sh`).

## Where the gate runs (shift-left)

The gate is **primary at pre-PR time** and a **required backstop in CI**:

1. **Pre-PR (primary, shift-left).** Before a PR exists, the change is gated:
   - CDK / human path → **`mcp-cdk-governance`** (in-cluster MCP) clones the feature
     branch, `cdk synth` → `cdk.out`, runs this engine, and raises the MR **only on PASS**.
   - Aiden intent path → authors CloudFormation and gates via `mcp-cfn-generator` before the PR.
   A failing change never becomes a PR on the sanctioned path — no bad PR is raised.
2. **CI backstop (required merge check).** The GitLab pipelines re-run this exact engine on
   the MR (`cdk-synth` → `governance-scan`), blocking any hand-raised / unsanctioned MR that
   bypassed the pre-PR gate before it merges to protected `main`.

Both use the identical `scan-cfn.sh` + `policies/`, so the verdict is the same everywhere.

## Gates

| Gate | Policy | Rule |
|------|--------|------|
| **Governance CSPM** | `policies/cspm.rego` | Public S3, non-CMK/unencrypted S3, SSH from 0.0.0.0/0, star-star IAM |
| **Mandatory tags** | `policies/tags.rego` | `Owner`, `CostCenter`, `Environment` on every taggable resource |
| **Region restriction** | `policies/region.rego` | Only `us-east-1`; any other region token is flagged |

All gates **fail closed**.

## Usage

```bash
# Scan a CloudFormation template (or a directory of templates / a cdk.out)
governance/scan-cfn.sh path/to/template.yaml
governance/scan-cfn.sh path/to/cdk.out --json result.json

# Synthesize a CDK project to CloudFormation, then scan it
governance/synth-cdk.sh path/to/cdk-project --scan
```

Exit code `0` = PASS, `1` = FAIL.

## Notes

- The **Governance CSPM** check runs a config-scanning engine in CI (clean egress to the
  checks-bundle registry). Locally the CSPM engine is bounded by `TRIVY_TIMEOUT` (default
  40s) and, if the bundle can't be pulled, the run degrades to `SKIP` while the policy CSPM
  rules still enforce the headline misconfigurations. Set `DISABLE_TRIVY=1` to skip the
  CSPM engine entirely (the env var names reference the underlying binary).
- The same `policies/` directory is copied into each GitLab repo so CI runs identical rules.
- Region enforcement is static (template tokens); post-deploy validation additionally
  checks the live stack's deployed region.
