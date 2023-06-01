import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
from boto3 import resource, client
import moto

sys.path.append('./src/services')
from src.services.app import LambdaS3Class
from src.services.app import lambda_handler, get_data_from_s3

@moto.mock_s3
class TestSampleLambda(TestCase):
    """
    Test class for the application sample AWS Lambda Function
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """

        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["BUCKET_NAME"] = self.test_s3_bucket_name

        s3_client = client('s3', region_name="us-east-1")
        s3_client.create_bucket(Bucket = self.test_s3_bucket_name )
        
        self.mocked_s3_class = LambdaS3Class()
        self.bucket_key = "sample.txt"
        s3_client.put_object(
            Body=f"Hello World".encode('utf-8'),
            Bucket=self.test_s3_bucket_name,
            Key='sample.txt',
            ServerSideEncryption='AES256',
            StorageClass='STANDARD_IA',
        )


    def test_get_data_from_s3(self) -> None:
        """
        Verify given correct parameters, the document will be retrieved from S3 with proper contents.
        """

        test_return_value = get_data_from_s3(
                        self.mocked_s3_class,
                        self.bucket_key
                        )

        body = self.mocked_s3_class.bucket.Object(self.bucket_key).get()['Body'].read()
        self.assertEqual(test_return_value["statusCode"], 200)


    def test_get_data_from_s3_doc_notfound_404(self) -> None:
        """
        Verify given a document type not present in the S3, a 404 error is returned.
        """
        test_return_value = get_data_from_s3(
                              self.mocked_s3_class,
                              "sample1.txt"
                            )
        print(self.mocked_s3_class.bucket)
        self.assertEqual(test_return_value["statusCode"], 404)
        self.assertIn("Not Found", test_return_value["body"])


    @patch("src.services.app.LambdaS3Class")
    @patch("src.services.app.get_data_from_s3")
    def test_lambda_handler_valid_event_returns_200(self,
                            patch_get_data_from_s3 : MagicMock,
                            patch_lambda_s3_class : MagicMock
                            ):
        """
        Verify the event is parsed, AWS resources are passed, the 
        get_data_from_s3 function is called, and a 200 is returned.
        """

        patch_lambda_s3_class.return_value = self.mocked_s3_class

        return_value_200 = {
               "headers": {
                  "Content-Type": "plain/text",
                  "Access-Control-Allow-Origin": "*",
                  "Cache-Control": "no-store"
               },
               "isBase64Encoded": True,
               "statusCode": 200,
               "body": "JVBERi0xLjcNCiW1tbW1D"
               }
        patch_get_data_from_s3.return_value = return_value_200

        test_event = self.load_sample_event_from_file("event")
        test_return_value = lambda_handler(event=test_event, context=None)

        patch_get_data_from_s3.assert_called_once_with(
                                        s3=self.mocked_s3_class,
                                        s3_file_key="sample.txt"
                                        )

        self.assertEqual(test_return_value, return_value_200)
    
    def load_sample_event_from_file(self, test_event_file_name: str) ->  dict:
        """
        Loads and validate test events from the file system
        """
        event_file_name = f"tests/events/{test_event_file_name}.json"
        with open(event_file_name, "r", encoding='UTF-8') as file_handle:
            event = json.load(file_handle)
            return event

    def tearDown(self) -> None:

        s3_resource = resource("s3",region_name="us-east-1")
        s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()