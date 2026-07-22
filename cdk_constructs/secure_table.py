"""SecureTable — FM-CDK building block.

A DynamoDB table encrypted with a customer-managed KMS key, point-in-time recovery
enabled, on-demand billing, and org-required tags. Passes Governance CSPM by
construction.
"""
from aws_cdk import RemovalPolicy, Tags
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_kms as kms
from constructs import Construct


class SecureTable(Construct):
    def __init__(self, scope: Construct, cid: str, *,
                 partition_key: str = "id",
                 sort_key: str | None = None,
                 encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev"):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        sort_key_attr = (
            dynamodb.Attribute(name=sort_key, type=dynamodb.AttributeType.STRING)
            if sort_key is not None
            else None
        )

        self.table = dynamodb.Table(
            self, "Table",
            partition_key=dynamodb.Attribute(
                name=partition_key, type=dynamodb.AttributeType.STRING,
            ),
            sort_key=sort_key_attr,
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.key,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        Tags.of(self).add("Owner", owner)
        Tags.of(self).add("CostCenter", cost_center)
        Tags.of(self).add("Environment", environment)
