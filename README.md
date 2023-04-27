# streaming-cloudwatch-logs-into-opensearch-with-lambda
The project contains AWS Lambda code to streaming CloudWatch logs into Amazon OpenSearch

## Deployment
Use AWS SAM to deploy the stack into your AWS account.

sam package --region [REGION_NAME] --template-file template.yaml --output-template-file packaged.yaml --s3-bucket [S3_BUCKET_NAME]

sam deploy --region [REGION_NAME] --template-file packaged.yaml --stack-name [STACK-NAME] --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM