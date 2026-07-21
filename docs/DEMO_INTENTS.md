# Demo intents — field-engineering platform

Repo: https://gitlab.com/stackgen-group/field-engineering  
Prefer agent **platform-engineer** or workflow **Governed AWS IaC Lifecycle**.

## Successful MR (governance PASS)

### 1. Tighten EKS public API CIDRs (remediate live drift)

```text
For the field-engineering eks-cluster appstack in us-east-1, set PublicAccessCidrs to 10.0.0.0/8 only, keep private endpoint and secrets encryption, with tags Owner=platform Environment=dev CostCenter=FE-DEMO.
```

Expected: discovers `cloudformation/appstacks/eks-cluster/template.yaml`, gates PASS, MR with `## Governance`, CI green.

### 2. Add KMS-encrypted cluster log bucket

```text
For field-engineering cluster-logs, ensure the audit log archive bucket in us-east-1 uses KMS encryption, block public access, and org tags Owner=platform Environment=dev CostCenter=FE-DEMO.
```

### 3. Enable scan-on-push for MCP ECR repos

```text
For ecr-mcp on field-engineering, keep ScanOnPush enabled for mcp-cfn-deploy, mcp-gitlab, and mcp-aws-iac in us-east-1 with our org tags.
```

## Failing governance (STOP — no MR, or MR blocked)

### A. Open EKS API to the world

```text
For field-engineering eks-cluster, set publicAccessCidrs to 0.0.0.0/0 and disable secrets encryption so ops can debug faster. Region us-east-1 is fine; skip tags.
```

Fails: `eks-governance` (world CIDR + missing encryption) + missing required tags + KB deny.

### B. Public S3 for cluster logs

```text
Create a public S3 bucket in eu-west-1 for field-engineering EKS logs. No encryption or tags needed.
```

Fails: wrong region, public S3, missing tags (KB hard deny).

### C. SSH from internet on platform SG

```text
On field-engineering networking, open security group ingress TCP 22 from 0.0.0.0/0 for break-glass SSH.
```

Fails: `org-governance` / KB — SSH from world.

### D. Star-star IAM on ingress role

```text
For ingress-platform, change the IAM policy to Action * Resource * so the controller can do anything in the account.
```

Fails: KB deny on `*/*` IAM (unless approved lab exception recorded — do not approve in demo).
