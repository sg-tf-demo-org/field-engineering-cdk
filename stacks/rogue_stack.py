"""RogueStack — hand-rolled (skipped Aiden + compliant constructs).

Demo FAIL: public/unencrypted S3, world-open SSH, us-west-2 region token,
no mandatory tags.
"""
from aws_cdk import CfnOutput, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_s3 as s3
from constructs import Construct


class RogueStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        # CSPM: public + no encryption + no public-access block; no tags
        s3.CfnBucket(self, "PublicBucket", access_control="PublicRead")

        # CSPM: SSH from the internet
        ec2.CfnSecurityGroup(
            self,
            "OpenSshSg",
            group_description="break-glass ssh from world",
            security_group_ingress=[
                ec2.CfnSecurityGroup.IngressProperty(
                    ip_protocol="tcp",
                    from_port=22,
                    to_port=22,
                    cidr_ip="0.0.0.0/0",
                )
            ],
        )

        # REGION: disallowed region in an ARN
        CfnOutput(
            self,
            "LegacyArn",
            value="arn:aws:lambda:us-west-2:123456789012:function:legacy",
        )
