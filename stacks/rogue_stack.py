"""RogueStack — hand-rolled (skipped Aiden + compliant constructs).

Demo FAIL: public/unencrypted S3, us-west-2 region token, no mandatory tags.
"""
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct


class RogueStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        # CSPM: public + no encryption + no public-access block
        s3.CfnBucket(self, "PublicBucket", access_control="PublicRead")

        # REGION: disallowed region in an ARN
        CfnOutput(
            self,
            "LegacyArn",
            value="arn:aws:lambda:us-west-2:123456789012:function:legacy",
        )
