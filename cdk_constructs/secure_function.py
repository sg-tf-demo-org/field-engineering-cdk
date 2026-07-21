"""SecureFunction — FM-CDK building block.

A Lambda function with a least-privilege execution role (no wildcard action+resource),
a dedicated bounded-retention log group, and org-required tags. Environment variables
are encrypted with a customer-managed KMS key. Passes Governance CSPM by construction.

Note: we attach an explicit log group (instead of the deprecated logRetention custom
resource) so no broad-privilege log-retention provider role is synthesized.
"""
from aws_cdk import RemovalPolicy, Duration, Tags
from aws_cdk import aws_kms as kms
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_logs as logs
from constructs import Construct

_DEFAULT_CODE = """
import json

def handler(event, context):
    return {"statusCode": 200, "body": json.dumps({"ok": True})}
"""


class SecureFunction(Construct):
    def __init__(self, scope: Construct, cid: str, *, handler: str = "index.handler",
                 code: str | None = None, environment: dict | None = None,
                 encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment_name: str = "dev"):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.log_group = logs.LogGroup(
            self, "LogGroup",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.function = lambda_.Function(
            self, "Function",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler=handler,
            code=lambda_.Code.from_inline(code or _DEFAULT_CODE),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment=environment or {},
            environment_encryption=self.key,
            log_group=self.log_group,
        )

        for res in (self.function, self.key, self.log_group):
            Tags.of(res).add("Owner", owner)
            Tags.of(res).add("CostCenter", cost_center)
            Tags.of(res).add("Environment", environment_name)
