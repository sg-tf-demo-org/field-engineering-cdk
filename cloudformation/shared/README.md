# Shared conventions

- Stack name: `fe-<appstack>-<env>` (e.g. `fe-cluster-logs-dev`)
- Live EKS cluster: `field-engineering` (us-east-1) — lab CFN uses `field-engineering-<env>`
- Tags on every taggable resource: Owner, Environment, ManagedBy=aiden, CostCenter, AppStack
- File paths for MCP: always `cloudformation/appstacks/<app>/template.yaml` (never a directory)
