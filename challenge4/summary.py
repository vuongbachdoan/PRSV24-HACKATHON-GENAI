import boto3
import json

def lambda_handler(event, context):
    # Initialize DynamoDB and S3 clients
    session = boto3.Session()
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table('dev-connectvoice-messages')
    s3_client = session.client('s3')
    bucket_name = 'vuongbach-transcribes'
    s3_key = 'full-text-lambda/grouped_messages.json'

    # Initialize Bedrock client
    bedrock = boto3.client(service_name='bedrock-runtime')
    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    # Scan DynamoDB table
    response = table.scan()
    items = response['Items']

    # Group data by contactId and generate summaries
    grouped_data_with_summary = {}
    for item in items:
        contact_id = item.get('contactId', '')
        content = item.get('content', '')
        role = item.get('role', '')
        when = item.get('when', '')

        if contact_id not in grouped_data_with_summary:
            grouped_data_with_summary[contact_id] = []

        formatted_content = f"{role}: {content}"
        grouped_data_with_summary[contact_id].append(formatted_content)

    for contact_id, contents in grouped_data_with_summary.items():
        combined_content = "\n".join(contents)

        # Call Bedrock to generate summary
        prompt = f"Summarize the following conversation:\n{combined_content}"
        body = json.dumps({
            "prompt": f"\n\nHuman:{prompt}\n\nAssistant:",
            "max_tokens_to_sample": 100,
            "temperature": 0.1,
            "top_p": 0.9,
        })
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())
        summary = response_body.get('completion')

        grouped_data_with_summary[contact_id] = {
            'content': combined_content,
            'summary': summary
        }

    # Prepare data for JSON
    json_data = [
        {'contactId': contact_id, 'content': data['content'], 'summary': data['summary']}
        for contact_id, data in grouped_data_with_summary.items()
    ]

    # Convert JSON data to bytes
    json_bytes = json.dumps(json_data, ensure_ascii=False, indent=4).encode('utf-8')

    # Upload JSON data to S3
    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=json_bytes)

    print(f"Data saved to s3://{bucket_name}/{s3_key}")
    return {
        'statusCode': 200,
        'body': json.dumps('Data successfully saved to S3!')
    }
