"""NetworkStack — VPC, flow logs, and a locked-down application security group."""
from aws_cdk import Stack
from constructs import Construct

from fm_constructs import SecureVpc


class NetworkStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        network = SecureVpc(self, "Platform")
        self.vpc = network.vpc
        self.app_sg = network.app_sg
