"""RogueStack — hand-rolled (bypasses the FM building blocks).

This simulates a developer who skipped Aiden's pre-PR governance gate and pushed a
non-compliant change straight to GitLab: a PUBLIC, UNENCRYPTED S3 bucket and a
reference to a disallowed region (us-west-2).
"""
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class RogueStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        # CSPM violation: public + unencrypted, no public-access block.
        s3.CfnBucket(self, "PublicBucket", access_control="PublicRead")

        # Region violation: hardcoded us-west-2 ARN.
        CfnOutput(self, "LegacyArn",
                  value="arn:aws:lambda:us-west-2:123456789012:function:legacy")
