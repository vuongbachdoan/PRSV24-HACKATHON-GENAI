import boto3
import json
from io import StringIO
from datetime import datetime

# Initialize DynamoDB and S3 clients
session = boto3.Session()
dynamodb = session.resource('dynamodb')
s3_client = session.client('s3')

# Define the DynamoDB table and S3 bucket
table = dynamodb.Table('dev-connectvoice-messages')
bucket_name = 'vuongbach-transcribes'
s3_key_prefix = 'report/'

def lambda_handler(event, context):
    # Scan the entire table (consider using pagination for large datasets)
    response = table.scan()
    items = response['Items']

    # Dictionary to hold grouped data
    grouped_data = {}

    # Group data by contactId and date
    for item in items:
        contact_id = item.get('contactId', '')
        when = item.get('when', '')
        content = item.get('content', '')
        role = item.get('role', '')

        # Convert the 'when' timestamp to a datetime object
        date_obj = datetime.utcfromtimestamp(int(when) / 1000)
        date_str = date_obj.strftime('%Y-%m-%d')

        if date_str not in grouped_data:
            grouped_data[date_str] = {}
        if contact_id not in grouped_data[date_str]:
            grouped_data[date_str][contact_id] = []

        formatted_content = f"{role}: {content}"
        grouped_data[date_str][contact_id].append(formatted_content)

    # Generate reports by date
    for date_str, contacts in grouped_data.items():
        # Create a text report
        report_lines = [f"Date: {date_str}\n"]
        for contact_id, contents in contacts.items():
            report_lines.append(f"Contact ID: {contact_id}\n")
            report_lines.append("\n".join(contents))
            report_lines.append("\n\n")

        # Join all lines to form the report content
        report_content = "\n".join(report_lines)

        # Save the report content to a StringIO object
        report_stream = StringIO(report_content)
        report_stream.seek(0)
        s3_key_final = f"{s3_key_prefix}{date_str}.txt"
        s3_client.put_object(Bucket=bucket_name, Key=s3_key_final, Body=report_stream.getvalue())

    return {
        'statusCode': 200,
        'body': json.dumps('Reports successfully saved to S3 as text files!')
    }
