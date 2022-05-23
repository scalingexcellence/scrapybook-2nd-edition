import json
import os
import subprocess


def lambda_handler(event, context):
    # Configure subprocesses Env
    env = os.environ
    wd = os.getcwd()
    env["PATH"] += ":" + os.path.join(wd, "bin")
    env["PYTHONPATH"] = wd

    # Make a non-SQS event to look like a SQS event
    if "Records" not in event:
        event = {"Records": [{"body": json.dumps(event)}]}

    for record in event["Records"]:
        body = json.loads(record["body"])
        cwd = os.path.join("projects",
          body["queryStringParameters"]["project"])
        args = (body["multiValueQueryStringParameters"]
                ["args"])
        subprocess.run(args, cwd=cwd, env=env)

    return {"statusCode": 200, "body": "ok"}
