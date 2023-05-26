import os
import json
import boto3
import base64
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):

    bucket_name = os.environ.get('BUCKET_NAME')
    client = boto3.client('s3')
    path = event['path'].replace("/static/", "")
    try:
        client_response = client.get_object(
            Bucket=bucket_name,
            Key=path,
        )
        body = base64.b64encode(client_response['Body'].read())
        content_type = client_response['ContentType']
        logger.info(
            "Got object '%s' from bucket '%s'.",
            path, bucket_name)
        
        response = {
            "statusCode": 200,
            "statusDescription": "200 OK",
            "isBase64Encoded": True,
            "headers": {
                "Content-Type": content_type
            },
            "body": body
        }
    except ClientError:
        logger.exception(
            "Couldn't get object '%s' from bucket '%s'.",
            path, bucket_name)
        raise
    else:
        return response
