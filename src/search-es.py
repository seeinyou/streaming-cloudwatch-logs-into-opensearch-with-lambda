import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from botocore.exceptions import ClientError
import os

host = os.environ['ES_HOST']
es_index = os.environ['ES_INDEX']
service = os.environ['ES_SERVICE']

session = boto3.Session()
region = session.region_name
credentials = session.get_credentials()
auth = AWSV4SignerAuth(credentials, region)

es_client = OpenSearch(
    hosts = [{'host': host, 'port': 443}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection
)

# Load CloudWatch logs and index into Elasticsearch
def lambda_handler(event, context):
    
    query = event
    print('\n## QUERY:', query)

    response = es_client.search(
        body = query,
        index = es_index
    )
    # print('\n## SEARCH RESULT:', response)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
