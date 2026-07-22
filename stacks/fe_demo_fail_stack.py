"""Intentional FAIL stack — PublicRead + SSE-S3 + us-west-2."""
from aws_cdk import Stack, aws_s3 as s3
from constructs import Construct

class FeDemoFailStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)
        s3.Bucket(self, "Bad", public_read_access=True, encryption=s3.BucketEncryption.S3_MANAGED)
