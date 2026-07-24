#!/usr/bin/env python3
"""fe-demo-pass — CMK-encrypted demo stack.

A governance-compliant CDK stack that provisions a KMS CMK and an
S3 bucket encrypted with that key.  All resources are tagged via the
app-wide Tags.of(app) call in app.py; no duplicate tags are needed here.
"""
import aws_cdk as cdk
from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_kms as kms,
    aws_s3 as s3,
)
from constructs import Construct


class FeDemoPassStack(Stack):
    """CMK-encrypted S3 bucket stack for the fe-demo-pass demo."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Customer-managed KMS key (CMK) with key rotation enabled
        key = kms.Key(
            self,
            "FeDemoPassKey",
            description="CMK for fe-demo-pass stack",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
        key.add_alias("alias/fe-demo-pass-key")

        # Private, CMK-encrypted, SSL-enforced, versioned S3 bucket
        bucket = s3.Bucket(
            self,
            "FeDemoPassBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=key,
            bucket_key_enabled=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
        )
