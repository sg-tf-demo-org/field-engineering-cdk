#!/usr/bin/env python3
"""field-engineering — AWS CDK (Python) platform application.

A realistic multi-stack CDK app assembled from pre-built, governance-compliant
CDK building blocks (cdk_constructs/). Everything is pinned to us-east-1 and tagged
with the org-required tags so the synthesized CloudFormation passes the Governance
gate (Governance CSPM + mandatory tags + region us-east-1) by construction.
"""
import aws_cdk as cdk

from stacks import (
    ComputeApiStack,
    DatabaseStack,
    FeDemoPassStack,
    MessagingStack,
    NetworkStack,
    StorageStack,
)

# Region is locked to us-east-1 (region-restriction governance gate).
ENV = cdk.Environment(region="us-east-1")

app = cdk.App()

network = NetworkStack(app, "fe-network", env=ENV)
storage = StorageStack(app, "fe-storage", env=ENV)
messaging = MessagingStack(app, "fe-messaging", env=ENV)
DatabaseStack(app, "fe-database", vpc=network.vpc, env=ENV)
ComputeApiStack(
    app, "fe-compute-api",
    bucket=storage.bucket,
    table=storage.table,
    queue=messaging.queue,
    topic=messaging.topic,
    env=ENV,
)
FeDemoPassStack(app, "fe-demo-pass", env=ENV)

# App-wide mandatory tags (mandatory-tags governance gate).
cdk.Tags.of(app).add("Owner", "platform")
cdk.Tags.of(app).add("CostCenter", "FE-DEMO")
cdk.Tags.of(app).add("Environment", "dev")

app.synth()
