"""CDK stacks for the field-engineering platform demo."""
from .network_stack import NetworkStack
from .storage_stack import StorageStack
from .messaging_stack import MessagingStack
from .compute_api_stack import ComputeApiStack
from .database_stack import DatabaseStack
from .fe_demo_cmk_s3_stack import FeDemoCmkS3Stack

__all__ = [
    "NetworkStack",
    "StorageStack",
    "MessagingStack",
    "ComputeApiStack",
    "DatabaseStack",
    "FeDemoCmkS3Stack",
]
