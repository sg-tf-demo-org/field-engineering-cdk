"""SecureDatabase — CDK building block.

A governance-compliant Amazon RDS (PostgreSQL) instance: customer-managed KMS
storage encryption, NOT publicly accessible, deployed into private subnets,
deletion protection, automated backups, IAM database authentication, and a
generated master credential stored in a CMK-encrypted Secrets Manager secret.
Passes Governance CSPM by construction. Use this instead of a raw rds.DatabaseInstance.
"""
from aws_cdk import Duration, RemovalPolicy, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_kms as kms
from aws_cdk import aws_rds as rds
from constructs import Construct


class SecureDatabase(Construct):
    def __init__(self, scope: Construct, cid: str, *, vpc: ec2.IVpc,
                 encryption_key: kms.IKey | None = None,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev"):
        super().__init__(scope, cid)

        self.key = encryption_key or kms.Key(
            self, "Key", enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Dedicated SG with NO unrestricted egress (CSPM: no open egress to
        # 0.0.0.0/0). A database never initiates outbound connections.
        self.security_group = ec2.SecurityGroup(
            self, "Sg", vpc=vpc,
            description="RDS SG - no egress",
            allow_all_outbound=False,
        )

        self.instance = rds.DatabaseInstance(
            self, "Db",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_16_3
            ),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[self.security_group],
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            # CSPM: storage encrypted with a customer-managed key.
            storage_encrypted=True,
            storage_encryption_key=self.key,
            # CSPM: never publicly reachable.
            publicly_accessible=False,
            deletion_protection=True,
            backup_retention=Duration.days(7),
            iam_authentication=True,
            credentials=rds.Credentials.from_generated_secret(
                "dbadmin", encryption_key=self.key
            ),
            cloudwatch_logs_exports=["postgresql"],
            removal_policy=RemovalPolicy.SNAPSHOT,
        )

        for res in (self.instance, self.key):
            Tags.of(res).add("Owner", owner)
            Tags.of(res).add("CostCenter", cost_center)
            Tags.of(res).add("Environment", environment)
