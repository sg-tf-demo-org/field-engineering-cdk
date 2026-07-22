#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.compute_api_stack import ComputeApiStack
from stacks.database_stack import DatabaseStack
from stacks.messaging_stack import MessagingStack
from stacks.network_stack import NetworkStack
from stacks.storage_stack import StorageStack
from stacks.fe_demo_pass_stack import FeDemoPassStack

app = cdk.App()

ComputeApiStack(app, "fe-compute-api", env=cdk.Environment(region="us-east-1"))
DatabaseStack(app, "fe-database", env=cdk.Environment(region="us-east-1"))
MessagingStack(app, "fe-messaging", env=cdk.Environment(region="us-east-1"))
NetworkStack(app, "fe-network", env=cdk.Environment(region="us-east-1"))
StorageStack(app, "fe-storage", env=cdk.Environment(region="us-east-1"))

FeDemoPassStack(app, "fe-demo-pass", env=cdk.Environment(region="us-east-1"))
cdk.Tags.of(app).add("Owner", "platform")
cdk.Tags.of(app).add("CostCenter", "FE-DEMO")
cdk.Tags.of(app).add("Environment", "dev")

app.synth()
