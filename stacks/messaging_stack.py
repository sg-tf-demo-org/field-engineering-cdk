"""MessagingStack — SQS work queue with DLQ and an SNS fan-out topic."""
from aws_cdk import Stack
from constructs import Construct

from fm_constructs import DlqQueue, SecureTopic


class MessagingStack(Stack):
    def __init__(self, scope: Construct, cid: str, **kwargs):
        super().__init__(scope, cid, **kwargs)

        work = DlqQueue(self, "Work")
        self.queue = work.queue

        events = SecureTopic(self, "Events")
        self.topic = events.topic
