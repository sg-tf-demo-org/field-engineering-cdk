"""DatabaseStack — relational database plus application data stores.

Provisions the most common application-tier data resources from compliant building
blocks: an RDS (PostgreSQL) instance, a DynamoDB sessions table, and an S3 audit-log
bucket. All are customer-managed-KMS encrypted, private, and org-tagged.
"""
import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from cdk_constructs import SecureBucket, SecureDatabase, SecureTable


class DatabaseStack(Stack):
    def __init__(self, scope: Construct, cid: str, *, vpc: ec2.IVpc, **kwargs):
        super().__init__(scope, cid, **kwargs)

        app_db = SecureDatabase(self, "AppDb", vpc=vpc)
        self.database = app_db.instance

        sessions = SecureTable(self, "Sessions", partition_key="sessionId")
        self.sessions = sessions.table

        audit = SecureBucket(self, "AuditLogs")
        self.audit_bucket = audit.bucket

        cdk.Tags.of(self).add("Owner", "platform")
        cdk.Tags.of(self).add("CostCenter", "FE-DEMO")
        cdk.Tags.of(self).add("Environment", "dev")
