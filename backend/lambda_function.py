import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logger = logging.getLogger()
logger.setLevel(logging.INFO)


# --------------------------------------------------
# DynamoDB configuration
# --------------------------------------------------

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

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


# --------------------------------------------------
# Lambda handler
# --------------------------------------------------

def lambda_handler(event, context):
    """
    Main Lambda entry point.

    Supported operations:

    GET    /tasks
    POST   /tasks
    PATCH  /tasks/{task_id}
    DELETE /tasks/{task_id}
    """

    try:
        # API Gateway HTTP API payload v2.0
        http_method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
        )

        # Allows us to test the Lambda directly as well.
        if not http_method:
            http_method = event.get("httpMethod")


        # --------------------------------------------------
        # Read task_id from URL
        # --------------------------------------------------

        path_parameters = event.get("pathParameters") or {}

        task_id = path_parameters.get("task_id")


        # --------------------------------------------------
        # Request logging
        # --------------------------------------------------

        logger.info(
            "Request received: method=%s task_id=%s request_id=%s",
            http_method,
            task_id,
            context.aws_request_id if context else "unknown"
        )


        # --------------------------------------------------
        # GET /tasks
        # --------------------------------------------------

        if http_method == "GET":
            response = table.scan()

            tasks = response.get("Items", [])

            logger.info(
                "Tasks retrieved successfully: count=%s",
                len(tasks)
            )

            return build_response(
                200,
                {
                    "tasks": tasks
                }
            )


        # --------------------------------------------------
        # POST /tasks
        # --------------------------------------------------

        if http_method == "POST":
            body = json.loads(event.get("body") or "{}")

            title = body.get("title")

            if not title:
                logger.warning(
                    "Task creation rejected: title is missing"
                )

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

            table.put_item(
                Item=task
            )

            logger.info(
                "Task created successfully: task_id=%s",
                task["task_id"]
            )

            return build_response(
                201,
                {
                    "message": "Task created successfully.",
                    "task": task
                }
            )


        # --------------------------------------------------
        # PATCH /tasks/{task_id}
        # --------------------------------------------------

        if http_method == "PATCH":

            if not task_id:
                logger.warning(
                    "Task update rejected: task_id is missing"
                )

                return build_response(
                    400,
                    {
                        "message": "Task ID is required."
                    }
                )

            try:
                response = table.update_item(
                    Key={
                        "task_id": task_id
                    },

                    UpdateExpression="SET completed = :completed",

                    ExpressionAttributeValues={
                        ":completed": True
                    },

                    ConditionExpression="attribute_exists(task_id)",

                    ReturnValues="ALL_NEW"
                )

            except ClientError as error:
                if (
                    error.response["Error"]["Code"]
                    == "ConditionalCheckFailedException"
                ):
                    logger.warning(
                        "Task update failed: task not found task_id=%s",
                        task_id
                    )

                    return build_response(
                        404,
                        {
                            "message": "Task not found."
                        }
                    )

                raise

            logger.info(
                "Task marked as completed: task_id=%s",
                task_id
            )

            return build_response(
                200,
                {
                    "message": "Task marked as completed.",
                    "task": response.get("Attributes")
                }
            )


        # --------------------------------------------------
        # DELETE /tasks/{task_id}
        # --------------------------------------------------

        if http_method == "DELETE":

            if not task_id:
                logger.warning(
                    "Task deletion rejected: task_id is missing"
                )

                return build_response(
                    400,
                    {
                        "message": "Task ID is required."
                    }
                )

            response = table.delete_item(
                Key={
                    "task_id": task_id
                },

                ReturnValues="ALL_OLD"
            )

            deleted_task = response.get("Attributes")

            if not deleted_task:
                logger.warning(
                    "Task deletion failed: task not found task_id=%s",
                    task_id
                )

                return build_response(
                    404,
                    {
                        "message": "Task not found."
                    }
                )

            logger.info(
                "Task deleted successfully: task_id=%s",
                task_id
            )

            return build_response(
                200,
                {
                    "message": "Task deleted successfully.",
                    "task": deleted_task
                }
            )


        # --------------------------------------------------
        # Unsupported HTTP method
        # --------------------------------------------------

        logger.warning(
            "Unsupported HTTP method: method=%s",
            http_method
        )

        return build_response(
            405,
            {
                "message": "Method not allowed."
            }
        )


    except Exception:
        logger.exception(
            "Unhandled error while processing request"
        )

        return build_response(
            500,
            {
                "message": "Internal server error."
            }
        )