"""NetworkStack — VPC, flow logs, and a locked-down application security group."""
import aws_cdk as cdk
from aws_cdk import Stack
from constructs import Construct

from cdk_constructs import SecureVpc


class NetworkStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        network = SecureVpc(self, "Platform")
        self.vpc = network.vpc
        self.app_sg = network.app_sg

        cdk.Tags.of(self).add("Owner", "platform")
        cdk.Tags.of(self).add("CostCenter", "FE-DEMO")
        cdk.Tags.of(self).add("Environment", "dev")
