from os import environ
from typing import Any, Dict
from boto3 import resource
import base64
from aws_lambda_powertools.utilities.data_classes import ALBEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import validator
import logging

logger = logging.getLogger(__name__)

# Import the schema for the Lambda Powertools Validator
from schemas import INPUT_SCHEMA, OUTPUT_SCHEMA

# [1] Globally scoped resources
# Initialize the resources once per Lambda execution environment by using global scope.
_LAMBDA_S3_RESOURCE = { "resource" : resource('s3'), 
                        "bucket_name" : environ.get("BUCKET_NAME","NONE") }

# [2] Define a Global class an AWS Resource: Amazon S3 bucket.
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

# [3] Validate the event schema and return schema using Lambda Powertools
@validator(inbound_schema=INPUT_SCHEMA, outbound_schema=OUTPUT_SCHEMA)
def lambda_handler(event: ALBEvent, context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda Entry Point
    """
    # [4] Use the Global variables to optimize AWS resource connections
    global _LAMBDA_S3_RESOURCE

    s3_resource_class = LambdaS3Class(_LAMBDA_S3_RESOURCE)

    # [5] Explicitly pass the global resource to subsequent functions
    return get_data_from_s3(s3 = s3_resource_class,
            s3_file_key = event['path'].split('/static/', 1)[1])

def get_data_from_s3( s3: LambdaS3Class,
                         s3_file_key: str) -> dict:

    try:
        client_response = s3.bucket.get_object(Key=s3_file_key)
        body = base64.b64encode(client_response['Body'].read())
        content_type = client_response['ContentType']
        content_length = client_response['ResponseMetadata']['HTTPHeaders']['content-length']
        logger.info(
            "Got object '%s' from Bucket '%s'.", s3_file_key, s3.bucket_name)
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

    except KeyError as index_error:
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
        logger.info("Return Response is '%s'", response)
        return response
