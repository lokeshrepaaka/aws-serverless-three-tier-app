import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


# --------------------------------------------------
# DynamoDB configuration
# --------------------------------------------------

TABLE_NAME = os.environ["TABLE_NAME"]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


# --------------------------------------------------
# Helper functions
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


def get_authenticated_user_id(event):
    """
    Reads the Cognito user's immutable `sub` claim from the JWT
    that API Gateway has already validated.

    Returns None if the request does not contain a verified JWT context.
    """
    return (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
        .get("sub")
    )


def get_user_tasks(user_id):
    """
    Returns only tasks owned by the authenticated Cognito user.

    The current DynamoDB table uses task_id as its partition key,
    so this implementation uses a filtered Scan. This keeps the
    existing table schema unchanged while adding user isolation.
    """
    items = []

    scan_kwargs = {
        "FilterExpression": Attr("owner_id").eq(user_id)
    }

    while True:
        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))

        last_evaluated_key = response.get("LastEvaluatedKey")

        if not last_evaluated_key:
            break

        scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

    return items


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

    Every operation is scoped to the authenticated Cognito user.
    """

    try:
        # API Gateway HTTP API payload v2.0
        http_method = (
            event.get("requestContext", {})
            .get("http", {})
            .get("method")
        )

        # Fallback for older/direct test event formats.
        if not http_method:
            http_method = event.get("httpMethod")


        # --------------------------------------------------
        # Identify authenticated Cognito user
        # --------------------------------------------------

        user_id = get_authenticated_user_id(event)

        if not user_id:
            return build_response(
                401,
                {
                    "message": "Authentication required."
                }
            )


        # --------------------------------------------------
        # GET /tasks
        # --------------------------------------------------

        if http_method == "GET":
            tasks = get_user_tasks(user_id)

            # Newest tasks first for a cleaner frontend experience.
            tasks.sort(
                key=lambda task: task.get("created_at", ""),
                reverse=True
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

            title = str(body.get("title") or "").strip()

            if not title:
                return build_response(
                    400,
                    {
                        "message": "Task title is required."
                    }
                )

            task = {
                "task_id": str(uuid.uuid4()),
                "owner_id": user_id,
                "title": title,
                "completed": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            }

            table.put_item(
                Item=task
            )

            return build_response(
                201,
                {
                    "message": "Task created successfully.",
                    "task": task
                }
            )


        # --------------------------------------------------
        # Read task_id from URL
        # --------------------------------------------------

        path_parameters = event.get("pathParameters") or {}
        task_id = path_parameters.get("task_id")


        # --------------------------------------------------
        # PATCH /tasks/{task_id}
        # --------------------------------------------------

        if http_method == "PATCH":

            if not task_id:
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
                        ":completed": True,
                        ":owner_id": user_id
                    },

                    ConditionExpression=(
                        "attribute_exists(task_id) "
                        "AND owner_id = :owner_id"
                    ),

                    ReturnValues="ALL_NEW"
                )

            except ClientError as error:
                if (
                    error.response["Error"]["Code"]
                    == "ConditionalCheckFailedException"
                ):
                    # Deliberately return the same response for a missing
                    # task and a task owned by another user.
                    return build_response(
                        404,
                        {
                            "message": "Task not found."
                        }
                    )

                raise

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
                return build_response(
                    400,
                    {
                        "message": "Task ID is required."
                    }
                )

            try:
                response = table.delete_item(
                    Key={
                        "task_id": task_id
                    },

                    ExpressionAttributeValues={
                        ":owner_id": user_id
                    },

                    ConditionExpression=(
                        "attribute_exists(task_id) "
                        "AND owner_id = :owner_id"
                    ),

                    ReturnValues="ALL_OLD"
                )

            except ClientError as error:
                if (
                    error.response["Error"]["Code"]
                    == "ConditionalCheckFailedException"
                ):
                    return build_response(
                        404,
                        {
                            "message": "Task not found."
                        }
                    )

                raise

            return build_response(
                200,
                {
                    "message": "Task deleted successfully.",
                    "task": response.get("Attributes")
                }
            )


        # --------------------------------------------------
        # Unsupported HTTP method
        # --------------------------------------------------

        return build_response(
            405,
            {
                "message": "Method not allowed."
            }
        )


    except json.JSONDecodeError:
        return build_response(
            400,
            {
                "message": "Request body must contain valid JSON."
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
