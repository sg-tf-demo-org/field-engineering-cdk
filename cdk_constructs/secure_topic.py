"""SecureTopic — FM-CDK building block.

An SNS topic encrypted with a customer-managed KMS key, SSL enforced via topic
policy, and org-required tags. Passes Governance CSPM by construction.
"""
from aws_cdk import RemovalPolicy, Tags
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_sns as sns
from constructs import Construct


class SecureTopic(Construct):
    def __init__(self, scope: Construct, cid: str, *, encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev"):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.topic = sns.Topic(self, "Topic", master_key=self.key)

        # Enforce TLS in transit.
        self.topic.add_to_resource_policy(
            iam.PolicyStatement(
                sid="EnforceTLS",
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["sns:Publish"],
                resources=[self.topic.topic_arn],
                conditions={"Bool": {"aws:SecureTransport": "false"}},
            )
        )

        for res in (self.topic, self.key):
            Tags.of(res).add("Owner", owner)
            Tags.of(res).add("CostCenter", cost_center)
            Tags.of(res).add("Environment", environment)
