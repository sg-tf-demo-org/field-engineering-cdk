import aws_cdk as cdk

from stacks.fe_compute_api_stack import FeComputeApiStack
from stacks.fe_database_stack import FeDatabaseStack
from stacks.fe_messaging_stack import FeMessagingStack
from stacks.fe_network_stack import FeNetworkStack
from stacks.fe_storage_stack import FeStorageStack
from stacks.fe_demo_pass_stack import FeDemoPassStack

app = cdk.App()

FeComputeApiStack(app, "fe-compute-api", env=cdk.Environment(region="us-east-1"))
FeDatabaseStack(app, "fe-database", env=cdk.Environment(region="us-east-1"))
FeMessagingStack(app, "fe-messaging", env=cdk.Environment(region="us-east-1"))
FeNetworkStack(app, "fe-network", env=cdk.Environment(region="us-east-1"))
FeStorageStack(app, "fe-storage", env=cdk.Environment(region="us-east-1"))
FeDemoPassStack(app, "fe-demo-pass", env=cdk.Environment(region="us-east-1"))

app.synth()
