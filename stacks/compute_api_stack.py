"""ComputeApiStack — Lambda API backend fronted by API Gateway.

Wires the shared data/messaging resources into a least-privilege Lambda and exposes
it through a REST API with access logging and X-Ray tracing enabled.
"""
from aws_cdk import RemovalPolicy, Stack
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_lambda_event_sources as sources
from aws_cdk import aws_logs as logs
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sqs as sqs
from constructs import Construct

from fm_constructs import SecureFunction

_API_CODE = """
import json
import os

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "service": "field-engineering-api",
            "table": os.environ.get("TABLE_NAME"),
            "bucket": os.environ.get("BUCKET_NAME"),
        }),
    }
"""


class ComputeApiStack(Stack):
    def __init__(self, scope: Construct, cid: str, *, bucket: s3.IBucket,
                 table: dynamodb.ITable, queue: sqs.IQueue, topic: sns.ITopic,
                 **kwargs):
        super().__init__(scope, cid, **kwargs)

        api_fn = SecureFunction(
            self, "ApiFn",
            code=_API_CODE,
            environment={
                "TABLE_NAME": table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
                "TOPIC_ARN": topic.topic_arn,
            },
        )
        fn = api_fn.function

        # Least-privilege grants (scoped resources, no wildcards).
        table.grant_read_write_data(fn)
        bucket.grant_read_write(fn)
        topic.grant_publish(fn)
        queue.grant_consume_messages(fn)
        fn.add_event_source(sources.SqsEventSource(queue, batch_size=10))

        access_logs = logs.LogGroup(
            self, "ApiAccessLogs",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY,
        )

        self.api = apigw.LambdaRestApi(
            self, "Api",
            handler=fn,
            deploy_options=apigw.StageOptions(
                tracing_enabled=True,
                logging_level=apigw.MethodLoggingLevel.INFO,
                metrics_enabled=True,
                access_log_destination=apigw.LogGroupLogDestination(access_logs),
                access_log_format=apigw.AccessLogFormat.json_with_standard_fields(
                    caller=True, http_method=True, ip=True, protocol=True,
                    request_time=True, resource_path=True, response_length=True,
                    status=True, user=True,
                ),
            ),
        )
