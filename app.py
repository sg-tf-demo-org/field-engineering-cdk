#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.storage_stack import StorageStack
from stacks.database_stack import DatabaseStack
from stacks.messaging_stack import MessagingStack
from stacks.network_stack import NetworkStack
from stacks.fe_demo_pass_stack import FeDemoPassStack

app = cdk.App()

storage = StorageStack(app, "storage", env=cdk.Environment(region="us-east-1"))
network = NetworkStack(app, "network", env=cdk.Environment(region="us-east-1"))
database = DatabaseStack(app, "database", vpc=network.vpc, env=cdk.Environment(region="us-east-1"))
messaging = MessagingStack(app, "messaging", env=cdk.Environment(region="us-east-1"))

FeDemoPassStack(
    app,
    "fe-demo-pass",
    bucket=storage.bucket,
    table=database.dynamo_table,
    queue=messaging.queue,
    topic=messaging.topic,
    env=cdk.Environment(region="us-east-1"),
)

app.synth()
