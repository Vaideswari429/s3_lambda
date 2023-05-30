from os import environ
from typing import Any, Dict
from boto3 import resource
import base64
import logging
from botocore.exceptions import ClientError

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger()

# Initialize the resources once per Lambda execution environment by using global scope.
_LAMBDA_S3_RESOURCE = { "resource" : resource('s3'), 
                        "bucket_name" : environ.get('BUCKET_NAME') }

class LambdaS3Class:
    """
    AWS S3 Resource Class
    """
    def __init__(self, lambda_s3_resource):
        """
        Initialize an S3 Resource
        """
        self.resource = lambda_s3_resource["resource"]
        self.bucket_name = lambda_s3_resource["bucket_name"]
        self.bucket = self.resource.Bucket(self.bucket_name)

def lambda_handler(event, context):
    """
    Lambda Entry Point
    """
    global _LAMBDA_S3_RESOURCE
    s3_resource_class = LambdaS3Class(_LAMBDA_S3_RESOURCE)
    logger.debug("Event Path is '%s'", event['path'])
    
    return get_data_from_s3(s3 = s3_resource_class,
            s3_file_key = event['path'].split('/static/', 1)[1])

def get_data_from_s3( s3: LambdaS3Class,
                         s3_file_key: str):
    response = {}
    try:
        client_response = s3.resource.Object(s3.bucket_name, s3_file_key)
        logger.debug("Response from S3 '%s' : ", client_response.get())
        body = base64.b64encode(client_response.get()['Body'].read())
        content_type = client_response.get()['ContentType']
        content_length = client_response.get()['ContentLength']
        logger.info(
            "Successfully retreived object '%s' from Bucket '%s'.", s3_file_key, s3.bucket_name)
        response = {
            "headers": {
                "Content-Type": content_type,
                'Access-Control-Allow-Origin': '*',
                'Cache-Control': 'no-store'
            },
            "isBase64Encoded": True,
            "statusCode": 200,
            "body": body
        }

    except ClientError as index_error:
        logger.exception("Exception is thrown for object '%s' from Bucket '%s': '%s'.", 
                         s3_file_key, s3.bucket_name, str(index_error))
        response['body'] = "Not Found: " + str(index_error)
        response['statusCode'] = 404
    except Exception as other_error:               
        logger.exception("Exception is thrown for object '%s' from Bucket '%s' : '%s'.", 
                         s3_file_key, s3.bucket_name, str(other_error))
        response['body'] = "ERROR: " + str(other_error)
        response['statusCode'] = 500
    finally:
        logger.debug("Return Response is '%s'", response)
        return response