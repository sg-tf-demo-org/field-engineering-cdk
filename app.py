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

db_attrs = [a for a in dir(database) if not a.startswith('_')]
msg_attrs = [a for a in dir(messaging) if not a.startswith('_')]
stor_attrs = [a for a in dir(storage) if not a.startswith('_')]
sys.stdout.write("DB=" + str([a for a in db_attrs if any(k in a.lower() for k in ['table','dynamo','db'])]) + "\n")
sys.stdout.write("MSG=" + str([a for a in msg_attrs if any(k in a.lower() for k in ['queue','topic','sns','sqs'])]) + "\n")
sys.stdout.write("STOR=" + str([a for a in stor_attrs if any(k in a.lower() for k in ['bucket','s3'])]) + "\n")
sys.stdout.flush()
sys.exit(1)
