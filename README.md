# field-engineering — AWS CDK (Python) platform

A realistic multi-stack **AWS CDK (Python)** application that simulates a real
platform-engineering repo. It provisions the most common AWS services and is
**governance-compliant by construction** so the synthesized CloudFormation passes
the org governance gate:

- **Governance CSPM** — customer-managed KMS everywhere, no public access, least privilege
- **Mandatory tags** — `Owner`, `CostCenter`, `Environment` on every taggable resource
- **Region restriction** — `us-east-1` only

## What's in here

| Stack | Services |
|-------|----------|
| `fe-network` | VPC (2 AZ), VPC flow logs, locked-down app security group |
| `fe-storage` | S3 data-lake bucket (CMK), DynamoDB catalog table (CMK, PITR) |
| `fe-messaging` | SQS work queue + DLQ (CMK), SNS events topic (CMK) |
| `fe-compute-api` | Lambda (least-privilege) fronted by API Gateway (access logging) |

All resources are assembled from pre-built, compliant building blocks in
`fm_constructs/` (`SecureBucket`, `DlqQueue`, `SecureTopic`, `SecureTable`,
`SecureFunction`, `SecureVpc`). Devs assemble blocks instead of hand-writing raw
resources, so guardrails are baked in.

## Governance

CDK is **never** scanned as source. It is synthesized to CloudFormation
(`cdk synth -> cdk.out/`) and the templates go through the **same** gate used
everywhere else:

```bash
pip install -r requirements.txt
npm install -g aws-cdk
cdk synth --all -o cdk.out
governance/scan-cfn.sh cdk.out --json governance-result.json
```

### How governance is enforced (two layers)

1. **Shift-left / pre-PR (primary):** developers call **`mcp-cdk-governance`**,
   which clones the branch, synthesizes CDK -> CloudFormation, runs the gate, and
   raises the MR **only on PASS**. A failing change never becomes a PR on the
   sanctioned path.
2. **Bypass backstop (this repo):** if someone pushes a branch / opens an MR
   **directly** in GitLab (bypassing Aiden), a GitLab webhook notifies **Aiden**,
   which independently pulls the branch and re-runs the same gate — so the bypass
   is caught. The `.gitlab-ci.yml` pipeline is the required merge check as an
   additional defense-in-depth layer.

## Layout

```
app.py                 # CDK app entrypoint (us-east-1, app-wide mandatory tags)
cdk.json
requirements.txt
fm_constructs/         # pre-built compliant building blocks
stacks/                # network / storage / messaging / compute-api stacks
governance/            # the scan gate (Trivy CSPM + Rego tags/region)
.gitlab-ci.yml         # governance backstop pipeline
```
