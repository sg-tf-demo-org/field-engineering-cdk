"""Pre-built CDK building blocks (field-engineering platform).

Reusable, governance-compliant constructs the platform/dev teams assemble instead
of hand-writing raw resources. Each block bakes in the org guardrails (customer-managed
KMS encryption, private access, least privilege, org-required tags) so the synthesized
CloudFormation passes the governance gate (Governance CSPM + mandatory tags + region
us-east-1) by construction.
"""
from .secure_bucket import SecureBucket
from .dlq_queue import DlqQueue
from .secure_topic import SecureTopic
from .secure_table import SecureTable
from .secure_function import SecureFunction
from .secure_vpc import SecureVpc
from .secure_database import SecureDatabase

__all__ = [
    "SecureBucket",
    "DlqQueue",
    "SecureTopic",
    "SecureTable",
    "SecureFunction",
    "SecureVpc",
    "SecureDatabase",
]
