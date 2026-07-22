import aws_cdk as cdk
from constructs import Construct
from cdk_constructs.secure_bucket import SecureBucket


class FeDemoPassStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        SecureBucket(self, "FeDemoPassBucket")

        cdk.Tags.of(self).add("Owner", "platform")
        cdk.Tags.of(self).add("CostCenter", "FE-DEMO")
        cdk.Tags.of(self).add("Environment", "dev")
