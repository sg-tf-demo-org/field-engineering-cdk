"""SecureVpc — FM-CDK building block.

A VPC with private/public subnets across AZs, VPC flow logs to a CloudWatch log
group, and a default application security group that does NOT expose SSH/RDP to the
internet. Org-required tags are applied. Passes Governance CSPM by construction.
"""
from aws_cdk import RemovalPolicy, Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from constructs import Construct


class SecureVpc(Construct):
    def __init__(self, scope: Construct, cid: str, *, max_azs: int = 2,
                 owner: str = "platform", cost_center: str = "FE-DEMO",
                 environment: str = "dev"):
        super().__init__(scope, cid)

        self.vpc = ec2.Vpc(
            self, "Vpc",
            max_azs=max_azs,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                    # Do not auto-assign public IPs (CSPM: no public-IP subnets).
                    map_public_ip_on_launch=False,
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
        )

        flow_log_group = logs.LogGroup(
            self, "FlowLogs",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )
        self.vpc.add_flow_log(
            "FlowLog",
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(flow_log_group),
        )

        # App SG: only intra-VPC HTTPS in/out. No 22/3389 from 0.0.0.0/0 and
        # no unrestricted egress (CSPM: no open egress to 0.0.0.0/0).
        self.app_sg = ec2.SecurityGroup(
            self, "AppSg", vpc=self.vpc,
            description="App SG - internal HTTPS only",
            allow_all_outbound=False,
        )
        self.app_sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Intra-VPC HTTPS in",
        )
        self.app_sg.add_egress_rule(
            peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(443),
            description="Intra-VPC HTTPS out",
        )

        for res in (self.vpc, flow_log_group, self.app_sg):
            Tags.of(res).add("Owner", owner)
            Tags.of(res).add("CostCenter", cost_center)
            Tags.of(res).add("Environment", environment)
