import json
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import boto3
from botocore.exceptions import ClientError
import os

import base64
import zlib

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

# Convert base64 encoded gzip string to JSON
def gzip_to_json(gzip_str):
    # Convert base64 encoded string back to bytes
    base64decoded_str = base64.b64decode(gzip_str.encode('utf-8'))

    # Decompress bytes to bytes
    decompressed_data=zlib.decompress(base64decoded_str, 16+zlib.MAX_WBITS)

    if decompressed_data:
        json_data = json.loads(decompressed_data)

    return json_data


# Post a line of log to Elasticsearch
def post_log_to_elasticsearch(document):
    print('### EVENT:', document)

    # Check whether the index exists in Elasticsearch
    indices_exists_response = es_client.indices.exists(es_index)
    print('### ES INDEX EXISTS:', indices_exists_response)
    
    # Create an index if it doesn't exist. If the index exists, do not create it again
    if not indices_exists_response:
        # create an index
        create_response = es_client.indices.create(
            es_index
        )
    
        print('\nCreating index:')
        print(create_response)

    # Index a document - use log timestamp + 3 digits random int  as the document ID
    response = es_client.index(
        index = es_index,
        body = document,
        id = document['timestamp'],
        refresh = False
    )
    print('\n INDEX DOCUMENT:', response)

    # Check the response from OpenSearch
    if response['result'] == 'created' or response['result'] == 'updated':
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Document indexed successfully."})
        } 
    else:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error indexing document.", "error": response})
        }

# Log filter algorithm
def log_filter(log_json):
  # Filter logs here.
  # ...

  return log_json


# Load CloudWatch logs and index into Elasticsearch
def lambda_handler(event, context):
    # Get CloudWatch logs and run base64 decoding and unzip
    log_json = gzip_to_json(event['awslogs']['data'])
    
    for log_obj in log_json['logEvents']:
      # Filter based on log messages
      aes_log = log_filter(log_obj)

      # Add the aes_log as a document into Elasticsearch index.
      es_result = post_log_to_elasticsearch(aes_log)
    
    return {
        'statusCode': 200,
        'body': json.dumps(es_result)
    }
