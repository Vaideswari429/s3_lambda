import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
from boto3 import resource, client
from botocore.stub import Stubber

sys.path.append('./src/services')
from src.services.app import LambdaS3Class
from src.services.app import lambda_handler, get_data_from_s3

class TestSampleLambda(TestCase):
    """
    Test class for the application sample AWS Lambda Function
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """
        s3_resource = resource('s3')
        stubber = Stubber(s3_resource)


    def test_get_data_from_s3(self) -> None:
        """
        Verify given correct parameters, the document will be retrieved from S3 with proper contents.
        """
        get_object_response = {
            "ResponseMetadata": {
                "RequestId": "HNQWGMEFC29SMV4N",
                "HostId": "fmJLwzpHgtbaZnWUzl3FSUEiIetIOIw46cduQ3cc3bI+mAqbdbrcoxID71dqRAyGbO4JVhQ/gtI=",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                "x-amz-id-2": "fmJLwzpHgtbaZnWUzl3FSUEiIetIOIw46cduQ3cc3bI+mAqbdbrcoxID71dqRAyGbO4JVhQ/gtI=",
                "x-amz-request-id": "HNQWGMEFC29SMV4N",
                "date": "Thu, 01 Jun 2023 05:32:59 GMT",
                "last-modified": "Tue, 30 May 2023 10:47:07 GMT",
                "etag": "77c89b2dd77a78a3f5e58400dc4bd00e",
                "x-amz-server-side-encryption": "AES256",
                "x-amz-version-id": "null",
                "accept-ranges": "bytes",
                "content-type": "application/pdf",
                "server": "AmazonS3",
                "content-length": "28713"
                },
                "RetryAttempts": 0
            },
            "AcceptRanges": "bytes",
            "LastModified": "datetime.datetime(2023, 5, 30, 10, 47, 7, tzinfo=tzutc())",
            "ContentLength": 28713,
            "ETag": "77c89b2dd77a78a3f5e58400dc4bd00e",
            "VersionId": "null",
            "ContentType": "application/pdf",
            "ServerSideEncryption": "AES256",
            "Metadata": {},
            "Body": "<botocore.response.StreamingBody object at 0x7f7e345e72e0>"
        }
        self.stubber.add_response('Object', get_object_response, {})
        self.stubber.activate()
        test_return_value = get_data_from_s3(
                        self.mocked_s3_class,
                        self.bucket_key
                        )

        self.assertEqual(test_return_value["statusCode"], 200)


    # def test_get_data_from_s3_doc_notfound_404(self) -> None:
    #     """
    #     Verify given a document type not present in the S3, a 404 error is returned.
    #     """
    #     test_return_value = get_data_from_s3(
    #                           self.mocked_s3_class,
    #                           "sample1.txt"
    #                         )

    #     self.assertEqual(test_return_value["statusCode"], 404)
    #     self.assertIn("Not Found", test_return_value["body"])


    # @patch("src.services.app.LambdaS3Class")
    # @patch("src.services.app.get_data_from_s3")
    # def test_lambda_handler_valid_event_returns_200(self,
    #                         patch_get_data_from_s3 : MagicMock,
    #                         patch_lambda_s3_class : MagicMock
    #                         ):
    #     """
    #     Verify the event is parsed, AWS resources are passed, the 
    #     get_data_from_s3 function is called, and a 200 is returned.
    #     """

    #     patch_lambda_s3_class.return_value = self.mocked_s3_class

    #     return_value_200 = {
    #            "headers": {
    #               "Content-Type": "plain/text",
    #               "Access-Control-Allow-Origin": "*",
    #               "Cache-Control": "no-store"
    #            },
    #            "isBase64Encoded": True,
    #            "statusCode": 200,
    #            "body": "JVBERi0xLjcNCiW1tbW1D"
    #            }
    #     patch_get_data_from_s3.return_value = return_value_200

    #     test_event = self.load_sample_event_from_file("event")
    #     test_return_value = lambda_handler(event=test_event, context=None)

    #     patch_get_data_from_s3.assert_called_once_with(
    #                                     s3=self.mocked_s3_class,
    #                                     s3_file_key="sample.txt"
    #                                     )

    #     self.assertEqual(test_return_value, return_value_200)
    
    # def load_sample_event_from_file(self, test_event_file_name: str) ->  dict:
    #     """
    #     Loads and validate test events from the file system
    #     """
    #     event_file_name = f"tests/events/{test_event_file_name}.json"
    #     with open(event_file_name, "r", encoding='UTF-8') as file_handle:
    #         event = json.load(file_handle)
    #         return event

    # def tearDown(self) -> None:

    #     s3_resource = resource("s3",region_name="us-east-1")
    #     s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
    #     for key in s3_bucket.objects.all():
    #         key.delete()
    #     s3_bucket.delete()