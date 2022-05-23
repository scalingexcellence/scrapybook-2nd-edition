import os
import subprocess


def lambda_handler(event, context):
    # Configure subprocesses Env
    env = os.environ
    wd = os.getcwd()
    env["PATH"] += ":" + os.path.join(wd, "bin")
    env["PYTHONPATH"] = wd

    cwd = os.path.join("projects", event["queryStringParameters"]["project"])
    subprocess.run(event["multiValueQueryStringParameters"]["args"], cwd=cwd, env=env)

    return {"statusCode": 200, "body": "ok"}
