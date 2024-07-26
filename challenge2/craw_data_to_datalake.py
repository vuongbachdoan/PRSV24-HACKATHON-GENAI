# HERE IS SCRIPT TO CRAW TRANSCRIPTION AND SAVE TO DATALAKE

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Amazon DynamoDB
AmazonDynamoDB_node1721581030980 = glueContext.create_dynamic_frame.from_options(connection_type="dynamodb", connection_options={"dynamodb.export": "ddb", "dynamodb.s3.bucket": "aws-glue-assets-884189903498-us-west-2", "dynamodb.s3.prefix": "temporary/ddbexport/", "dynamodb.tableArn": "arn:aws:dynamodb:us-west-2:884189903498:table/dev-connectvoice-transcripts", "dynamodb.unnestDDBJson": True}, transformation_ctx="AmazonDynamoDB_node1721581030980")

# Script generated for node Amazon S3
AmazonS3_node1721581329563 = glueContext.write_dynamic_frame.from_options(frame=AmazonDynamoDB_node1721581030980, connection_type="s3", format="csv", connection_options={"path": "s3://vuongbach-transcribes/text/", "partitionKeys": ["contactId"]}, transformation_ctx="AmazonS3_node1721581329563")

job.commit()