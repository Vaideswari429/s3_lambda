URL to download
View and download PDF - URL, Base64.

Code: https://codesandbox.io/s/view-download-example-url-base64-embed-0pgmrh

Demo App: https://0pgmrh.csb.app

View and download PDF if getting base64 pdf in API response.
Did some R&D and found we don’t require Print-js now attaching link for 
demo app: https://react-zx3gjt.stackblitz.io

code: https://stackblitz.com/edit/react-zx3gjt?file=src/App.js


sample event.json
{
  "requestContext": {
    "elb": {
      "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:503930535803:targetgroup/ALB-LambdaTG/c409f0b9b32330cd"
    }
  },
  "httpMethod": "GET",
  "path": "/static/hello_world.pdf",
  "queryStringParameters": {},
  "headers": {
    "accept": "text/html,application/xhtml+xml",
    "accept-language": "en-US,en;q=0.8",
    "content-type": "text/plain",
    "cookie": "cookies",
    "host": "lambda-846800462-us-east-2.elb.amazonaws.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)",
    "x-amzn-trace-id": "Root=1-5bdb40ca-556d8b0c50dc66f0511bf520",
    "x-forwarded-for": "72.21.198.66",
    "x-forwarded-port": "443",
    "x-forwarded-proto": "https"
  },
  "isBase64Encoded": false,
  "body": "request_body"
}
