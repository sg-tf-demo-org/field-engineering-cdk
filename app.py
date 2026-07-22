#!/usr/bin/env python3
import sys
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

# Get all non-private attrs that are not CDK built-ins
cdk_base = set(dir(cdk.Stack))
db_custom = [a for a in dir(database) if not a.startswith('_') and a not in cdk_base]
sys.stderr.write("DIAG-DB-CUSTOM=" + str(db_custom) + "\n")
sys.stderr.flush()
sys.exit(1)
