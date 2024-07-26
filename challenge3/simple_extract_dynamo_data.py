import boto3
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
    bucket_name = 'vuongbach-transcribes'
    s3_key = 'full-text-lambda/grouped_messages.json'

    # Scan the entire table (consider using pagination for large datasets)
    response = table.scan()
    items = response['Items']

    # Dictionary to hold grouped data
    grouped_data = {}

    # Group data by contactId
    for item in items:
        contact_id = item.get('contactId', '')
        content = item.get('content', '')
        role = item.get('role', '')
        when = item.get('when', '')

        if contact_id not in grouped_data:
            grouped_data[contact_id] = []

        formatted_content = f"{role}: {content}"
        grouped_data[contact_id].append(formatted_content)

    # Prepare data for JSON
    json_data = []
    for contact_id, contents in grouped_data.items():
        combined_content = "\n".join(contents)
        json_data.append({
            'contactId': contact_id,
            'content': combined_content
        })

    # Convert JSON data to bytes
    json_bytes = json.dumps(json_data, ensure_ascii=False, indent=4).encode('utf-8')

    # Upload JSON data directly to S3
    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=json_bytes)

    print(f"Data saved to s3://{bucket_name}/{s3_key}")
    return {
        'statusCode': 200,
        'body': json.dumps('Data successfully saved to S3!')
    }
