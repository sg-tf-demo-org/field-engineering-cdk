# Governing policies (field-engineering)

| File | Enforces |
|------|----------|
| `org-governance.guard` | Private S3 BPA, no SSH from `0.0.0.0/0` |
| `eks-governance.guard` | Private API endpoint, control-plane logging, secrets encryption, **no `0.0.0.0/0` publicAccessCidrs** |

Aiden Knowledge Hub `Governance_Configuration` also requires: region `us-east-1` only, tags `Owner`/`Environment`/`ManagedBy=aiden`/`CostCenter`, deny public S3 and star-star IAM (except approved lab exceptions).

CI runs `cfn-lint`. Guard rules are evaluated by Aiden skills before MR (`## Governance` must cite PASS/FAIL).
