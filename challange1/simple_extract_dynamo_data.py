import boto3
import csv
import time
import io
import json

def lambda_handler(event, context):
    # Initialize a session using Amazon DynamoDB
    session = boto3.Session()
    dynamodb = session.resource('dynamodb')

    # Define the DynamoDB table
    table = dynamodb.Table('dev-connectvoice-messages')

    # Initialize S3 client
    s3_client = session.client('s3')

    # S3 bucket and path
    bucket_name = 'minhbear-challange1'
    # Get the current timestamp
    timestamp = time.strftime('%Y%m%d%H%M%S')
    s3_key = f"conversation/{timestamp}_conversation.csv"

    # Scan the entire table (consider using pagination for large datasets)
    response = table.scan()
    items = response['Items']

    # Dictionary to hold grouped data
    grouped_data = {}

    # Group data by contactId
    for item in items:
        contact_id = item.get('contactId', '')
        raw_content = item.get('content', '')
        role = item.get('role', '')
        content = raw_content
        topic = ""

        if contact_id not in grouped_data:
            grouped_data[contact_id] = {
                'content': [],
                'topic': ''
            }

        if role == 'assistant':
            # Find the start and end tags for <Argument>
            start_tag_arg = "<Argument>"
            end_tag_arg = "</Argument>"

            # Get the index positions of the start and end tags
            start_index_arg = raw_content.find(start_tag_arg) + len(start_tag_arg)
            end_index_arg = raw_content.find(end_tag_arg)

            # Extract the text within the <Argument> tags
            content = raw_content[start_index_arg:end_index_arg].strip()

            # Find the start and end tags for <Tool>
            start_tag_topic = "<Tool>"
            end_tag_topic = "</Tool>"

            # Get the index positions of the start and end tags
            start_index_topic = raw_content.find(start_tag_topic) + len(start_tag_topic)
            end_index_topic = raw_content.find(end_tag_topic)

            # Extract the text within the <Tool> tags
            topic = raw_content[start_index_topic:end_index_topic].strip()
            
            grouped_data[contact_id]['topic'] = topic

        formatted_content = f"{role}: {content}"
        grouped_data[contact_id]['content'].append(formatted_content)

    # Prepare CSV data
    csv_output = io.StringIO()
    csv_writer = csv.writer(csv_output)
    
    # Write the CSV header
    csv_writer.writerow(['contactId', 'content', 'topic'])
    
    # Write the data rows
    for contact_id, data in grouped_data.items():
        combined_content = "\n".join(data['content'])
        csv_writer.writerow([contact_id, combined_content, data['topic']])
    
    # Get the CSV content as bytes
    csv_bytes = csv_output.getvalue().encode('utf-8')

    # Upload CSV data directly to S3
    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=csv_bytes)

    print(f"Data saved to s3://{bucket_name}/{s3_key}")
    return {
        'statusCode': 200,
        'body': json.dumps('Data successfully saved to S3!')
    }
