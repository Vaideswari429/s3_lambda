import sys
import os
import json
from unittest import TestCase
from unittest.mock import MagicMock, patch
from boto3 import resource, client
import moto

# [0] Import the Globals, Classes, Schemas, and Functions from the Lambda Handler
sys.path.append('./src/services')
from src.services.app import LambdaS3Class   # pylint: disable=wrong-import-position
from src.services.app import lambda_handler, get_data_from_s3  # pylint: disable=wrong-import-position

# [1] Mock all AWS Services in use
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

        # [2] Mock environment & override resources
        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["BUCKET_NAME"] = self.test_s3_bucket_name


        # [3] Set up the services: construct a (mocked!) S3 Bucket table
        s3_client = client('s3', region_name="us-east-1")
        s3_client.create_bucket(Bucket = self.test_s3_bucket_name )

        # [4] Establish the "GLOBAL" environment for use in tests.
        mocked_s3_resource = resource("s3")
        mocked_s3_resource = { "resource" : resource('s3'),
                               "bucket_name" : self.test_s3_bucket_name }
        self.mocked_s3_class = LambdaS3Class(mocked_s3_resource)
        self.bucket_key = "sample.txt"
        self.mocked_s3_class.bucket
        s3_file_key = "sample.txt"
        some_binary_data = b'Here we have some data'
        obj = mocked_s3_resource.Object(self.bucket_key).get()
        obj.put(Body=f"Hello World".encode('utf-8'),
                        ServerSideEncryption='AES256')


    def test_get_data_from_s3(self) -> None:
        """
        Verify given correct parameters, the document will be written to S3 with proper contents.
        """


        # [5] Run S3 file function to get S3 Object
        test_return_value = get_data_from_s3(
                        self.mocked_s3_class,
                        self.bucket_key
                        )

        # [6] Ensure the data was written to S3 correctly, with correct contents
        body = self.mocked_s3_class.bucket.Object(self.bucket_key).get()['Body'].read()

        # Test
        self.assertEqual(test_return_value["statusCode"], 200)
        self.assertIn("sample.txt", test_return_value["body"])
        self.assertEqual(body.decode('ascii'),"Hello World")


    def test_get_data_from_s3_doc_notfound_404(self) -> None:
        """
        Verify given a document type not present in the S3, a 404 error is returned.
        """
        # [7] Run S3 file function
        test_return_value = get_data_from_s3(
                              self.mocked_s3_class,
                              "sample1.txt"
                            )

        # Test
        self.assertEqual(test_return_value["statusCode"], 404)
        self.assertIn("Not Found", test_return_value["body"])


    # [8] Patch the Global Class and any function calls
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

        # [9] Test setup - Return a mock for the global variables and resources
        patch_lambda_s3_class.return_value = self.mocked_s3_class

        return_value_200 = {
               "headers": {
                  "Content-Type": "plain/text",
                  "Content-Length": 28664,
                  "Access-Control-Allow-Origin": "*",
                  "Cache-Control": "no-store"
               },
               "isBase64Encoded": True,
               "statusCode": 200,
               "body": "JVBERi0xLjcNCiW1tbW1D"
               }
        patch_get_data_from_s3.return_value = return_value_200

        # [10] Run Test using a test event from /tests/events/*.json
        test_event = self.load_sample_event_from_file("event")
        test_return_value = lambda_handler(event=test_event, context=None)

        # [11] Validate the function was called with the mocked globals
        # and event values
        patch_get_data_from_s3.assert_called_once_with(
                                        s3=self.mocked_s3_class,
                                        s3_file_key="sample.txt"
                                        )

        self.assertEqual(test_return_value, return_value_200)
    
    # [12] Load and validate test events from the file system
    def load_sample_event_from_file(self, test_event_file_name: str) ->  dict:
        """
        Loads and validate test events from the file system
        """
        event_file_name = f"tests/events/{test_event_file_name}.json"
        with open(event_file_name, "r", encoding='UTF-8') as file_handle:
            event = json.load(file_handle)
            return event

    def tearDown(self) -> None:

        # [12] Remove (mocked!) S3 Objects and Bucket
        s3_resource = resource("s3",region_name="us-east-1")
        s3_bucket = s3_resource.Bucket( self.test_s3_bucket_name )
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()

# End of unit test code