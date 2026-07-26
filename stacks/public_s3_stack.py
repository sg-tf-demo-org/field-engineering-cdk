"""Non-compliant demo stack: public S3 bucket with SSE-S3 encryption in us-west-2."""
import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class PublicS3Stack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        s3.Bucket(
            self,
            "PublicDemoBucket",
            bucket_name="fe-demo-public-bucket-usw2",
            access_control=s3.BucketAccessControl.PUBLIC_READ,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
        )
