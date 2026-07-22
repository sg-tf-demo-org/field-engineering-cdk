"""PublicS3Stack — intentionally non-compliant demo stack.

S3 bucket with PublicRead ACL, SSE-S3 encryption, deployed in us-west-2.
NOTE: This configuration is intentionally non-compliant for demonstration.
"""
import aws_cdk as cdk
from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct


class PublicS3Stack(cdk.Stack):
    """
    S3 bucket with PublicRead ACL, SSE-S3 encryption, deployed in us-west-2.
    NOTE: This configuration is intentionally non-compliant for demonstration.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "PublicBucket",
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )
