import boto3
import json

sqs = "FIXME: SQS queue name"
bucket = "FIXME: S3 bucket name"

queue = boto3.resource("sqs").get_queue_by_name(QueueName=sqs)

response = queue.send_messages(
    Entries=[
        {
            "Id": category,
            "MessageBody": json.dumps(
                {
                    "queryStringParameters": {"project": "quotes"},
                    "multiValueQueryStringParameters": {
                        "args": [
                            "scrapy",
                            "crawl",
                            "example",
                            "-L",
                            "INFO",
                            "-a",
                            f"category={category}",
                            "-o",
                            f"s3://{bucket}/bulk-%(name)s-{category}-%(time)s.jl:jl",
                        ]
                    },
                }
            ),
        }
        for category in [
            "love",
            "inspirational",
            "life",
            "humor",
            "books",
            "reading",
            "friendship",
            "friends",
            "truth",
            "simile",
        ]
    ]
)

for r in response:
    print(r)
