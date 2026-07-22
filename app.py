#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.network_stack import NetworkStack
from stacks.storage_stack import StorageStack
from stacks.database_stack import DatabaseStack
from stacks.messaging_stack import MessagingStack
from stacks.compute_api_stack import ComputeApiStack
from stacks.fe_demo_pass_stack import FeDemoPassStack

app = cdk.App()

network_stack = NetworkStack(app, "fe-network", env=cdk.Environment(region="us-east-1"))
storage_stack = StorageStack(app, "fe-storage", env=cdk.Environment(region="us-east-1"))
database_stack = DatabaseStack(
    app,
    "fe-database",
    vpc=network_stack.vpc,
    env=cdk.Environment(region="us-east-1"),
)
messaging_stack = MessagingStack(app, "fe-messaging", env=cdk.Environment(region="us-east-1"))
ComputeApiStack(
    app,
    "fe-compute-api",
    bucket=storage_stack.bucket,
    table=database_stack.sessions_table,
    queue=messaging_stack.queue,
    topic=messaging_stack.topic,
    env=cdk.Environment(region="us-east-1"),
)

FeDemoPassStack(app, "fe-demo-pass", env=cdk.Environment(region="us-east-1"))

cdk.Tags.of(app).add("Owner", "platform")
cdk.Tags.of(app).add("CostCenter", "FE-DEMO")
cdk.Tags.of(app).add("Environment", "dev")

app.synth()
