"""SnsStack — SNS topic encrypted with a customer-managed KMS key.

Uses the SecureTopic building block (CMK + SSE aws:kms + TLS policy + org tags).
Adds a KMS Alias for discoverability and applies the mandatory governance tags
at the stack level.
"""
import aws_cdk as cdk
from aws_cdk import aws_kms as kms
from constructs import Construct

from cdk_constructs import SecureTopic


class SnsStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SecureTopic creates a CMK (enable_key_rotation=True) and an SNS Topic
        # encrypted with that key (SSE aws:kms), enforces TLS in transit, and
        # applies the org-required tags to both the key and the topic.
        secure = SecureTopic(
            self,
            "SecureSnsTopicDev",
            owner="platform",
            cost_center="FE-DEMO",
            environment="dev",
        )
        self.topic = secure.topic
        self.key = secure.key

        # Add discoverable KMS alias for the CMK.
        kms.Alias(
            self,
            "SnsKeyAlias",
            alias_name="alias/sns-cmk-dev",
            target_key=secure.key,
        )

        # Mandatory governance tags at stack scope (belt-and-suspenders).
        cdk.Tags.of(self).add("Owner", "platform")
        cdk.Tags.of(self).add("CostCenter", "FE-DEMO")
        cdk.Tags.of(self).add("Environment", "dev")
        cdk.Tags.of(self).add("ManagedBy", "aiden")
