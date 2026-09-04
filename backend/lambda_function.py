import json
import os
import uuid
from datetime import datetime, timezone

import boto3


# Read the DynamoDB table name from the Lambda environment variable.
TABLE_NAME = os.environ["TABLE_NAME"]

# Create a DynamoDB resource and reference our Tasks table.
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def build_response(status_code, body):
    """
    Creates a consistent HTTP response for API Gateway.
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Main Lambda entry point.

    API Gateway will eventually send requests here.
    We inspect the HTTP method and perform the appropriate
    DynamoDB operation.
    """

    try:
        http_method = event.get("requestContext", {}).get("http", {}).get("method")

        # Temporary direct-Lambda testing support.
        if not http_method:
            http_method = event.get("httpMethod")

        # -----------------------------
        # GET /tasks
        # Return all tasks
        # -----------------------------
        if http_method == "GET":
            response = table.scan()

            return build_response(
                200,
                {
                    "tasks": response.get("Items", [])
                }
            )

        # -----------------------------
        # POST /tasks
        # Create a new task
        # -----------------------------
        if http_method == "POST":
            body = json.loads(event.get("body") or "{}")

            title = body.get("title")

            if not title:
                return build_response(
                    400,
                    {
                        "message": "Task title is required."
                    }
                )

            task = {
                "task_id": str(uuid.uuid4()),
                "title": title,
                "completed": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            table.put_item(Item=task)

            return build_response(
                201,
                {
                    "message": "Task created successfully.",
                    "task": task
                }
            )

        return build_response(
            405,
            {
                "message": "Method not allowed."
            }
        )

    except Exception as error:
        print(f"Error: {error}")

        return build_response(
            500,
            {
                "message": "Internal server error."
            }
        )