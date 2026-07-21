"""DlqQueue — FM-CDK building block.

An SQS queue with an attached dead-letter queue, customer-managed KMS encryption,
SSL enforced, and org-required tags. Passes Governance CSPM by construction.
"""
from aws_cdk import Duration, RemovalPolicy, Tags
from aws_cdk import aws_kms as kms
from aws_cdk import aws_sqs as sqs
from constructs import Construct


class DlqQueue(Construct):
    def __init__(self, scope: Construct, cid: str, *, max_receive_count: int = 5,
                 encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev"):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.dlq = sqs.Queue(
            self, "Dlq",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.key,
            retention_period=Duration.days(14),
            enforce_ssl=True,
        )
        self.queue = sqs.Queue(
            self, "Queue",
            encryption=sqs.QueueEncryption.KMS,
            encryption_master_key=self.key,
            enforce_ssl=True,
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=max_receive_count,
                queue=self.dlq,
            ),
        )

        for q in (self.queue, self.dlq, self.key):
            Tags.of(q).add("Owner", owner)
            Tags.of(q).add("CostCenter", cost_center)
            Tags.of(q).add("Environment", environment)
