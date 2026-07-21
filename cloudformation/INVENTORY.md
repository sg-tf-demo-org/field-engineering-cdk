# Live inventory — EKS `field-engineering` (us-east-1)

Console: https://us-east-1.console.aws.amazon.com/eks/clusters/field-engineering?region=us-east-1

## AWS control plane / network

| Component | Live value | CFN appstack |
|-----------|------------|--------------|
| EKS cluster | `field-engineering` v1.36, Auto Mode (`general-purpose`,`system`) | `eks-cluster` |
| Cluster role | `AmazonEKSAutoClusterRole` | `eks-node-iam` |
| Node role | `AmazonEKSAutoNodeRole` | `eks-node-iam` |
| VPC | default `vpc-046a1d2485887edea` (172.31.0.0/16) | `networking` (lab = 10.40.0.0/16) |
| Subnets | private `subnet-0afdb75…` / `subnet-0e8b26…` + public ELB-tagged | `networking` |
| NAT | `nat-0d824db19a4101abe` | `networking` |
| Cluster SG | `sg-0607c2a2c351d64d8` | created by EKS |
| API access | public+private, **publicAccessCidrs=`0.0.0.0/0`** (governance drift) | `eks-cluster` params |
| Logging | api, audit, authenticator, controllerManager, scheduler | `eks-cluster` |
| Secrets encryption | **none** on live (governance gap) | `eks-cluster` KMS |
| Addon | metrics-server | `eks-cluster` |
| Ingress NLB | `k8s-ingressn-ingressn-69a02f485c` (internet-facing) | `ingress-platform` |
| DNS | Route53 `stackgen.run` `Z04651531ULS293Y1EQT` | `dns-external` |
| ECR | `mcp-cfn-deploy`, `mcp-gitlab`, `mcp-aws-iac` | `ecr-mcp` |
| Log archive | (optional) | `cluster-logs` |

## In-cluster (Helm / manifests — not CFN)

Namespaces: `ingress-nginx`, `cert-manager`, `external-dns`, `otel-demo`, `mcp-aws`, `mcp-gitlab`, `mcp-kubernetes`, `data-recipes`, `ollama`, `kubernetes-dashboard`, `opentelemetry-operator`.

Hostnames on `*.stackgen.run` via ingress-nginx + cert-manager + external-dns.
