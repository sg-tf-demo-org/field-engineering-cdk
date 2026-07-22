"""Intentional FAIL: public SSE-S3 bucket in us-west-2."""
from aws_cdk import Stack, aws_s3 as s3, RemovalPolicy
from constructs import Construct


class FeDemoFailPublicStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)
        s3.Bucket(
            self,
            "BadPublic",
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            encryption=s3.BucketEncryption.S3_MANAGED,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
