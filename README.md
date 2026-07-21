# field-engineering

**Source of truth** for CloudFormation that models the [field-engineering EKS platform](https://us-east-1.console.aws.amazon.com/eks/clusters/field-engineering?region=us-east-1) (us-east-1).

Replaces the toy `cloudformation/demo/demo-assets` path for realistic platform demos.

```text
cloudformation/
  INVENTORY.md                 # live AWS ↔ appstack map
  appstacks/<app>/template.yaml
  appstacks/<app>/params/{dev,stage,uat,prod}.json
  policies/*.guard             # org + EKS governance
  shared/README.md
.gitlab-ci.yml
```

Stack naming: `fe-<app>-<env>`.

## Deploy path

Intent → Aiden gates (KB + lint/guard) → MR with `## Governance` → CI → approve → Aiden webhook → `mcp-cfn-deploy`.
