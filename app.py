#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.network_stack import NetworkStack
from stacks.storage_stack import StorageStack
from stacks.database_stack import DatabaseStack
from stacks.messaging_stack import MessagingStack
from stacks.compute_api_stack import ComputeApiStack
from stacks.fe_demo_pass_stack import FeDemoPassStack

app = cdk.App()

env_us = cdk.Environment(region="us-east-1")

network = NetworkStack(app, "fe-network", env=env_us)
storage = StorageStack(app, "fe-storage", env=env_us)
database = DatabaseStack(app, "fe-database", vpc=network.vpc, env=env_us)
messaging = MessagingStack(app, "fe-messaging", env=env_us)
ComputeApiStack(
    app, "fe-compute-api",
    bucket=storage.bucket,
    table=database.sessions,
    queue=messaging.queue,
    topic=messaging.topic,
    env=env_us,
)
FeDemoPassStack(app, "fe-demo-pass", env=env_us)

app.synth()
