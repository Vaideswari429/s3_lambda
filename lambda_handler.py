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
    # path = event['path'].replace("/lambda/", "")
    path = event['path'].split('/lambda/', 1)[1]
    print(path)
    try:
        client_response = client.get_object(
            Bucket=bucket_name,
            Key=path
        )
        
        body = base64.b64encode(client_response['Body'].read())
        content_type = client_response['ContentType']
        content_length = client_response['ResponseMetadata']['HTTPHeaders']['content-length']
        logger.info(
            "Got object '%s' from bucket '%s'.",
            path, bucket_name)
        
        response = {
            "headers": {
                "Content-Type": content_type,
                'Content-Length': content_length,
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-store'
            },
            "statusCode": 200,
            "isBase64Encoded": True,
            "body": body
        }
    except ClientError:
        logger.exception(
            "Couldn't get object '%s' from bucket '%s'.",
            path, bucket_name)
        raise
    else:
        return response
