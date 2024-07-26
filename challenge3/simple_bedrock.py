import boto3
import json
bedrock = boto3.client(service_name='bedrock-runtime')



modelId = 'anthropic.claude-v2'
accept = 'application/json'
contentType = 'application/json'

def lambda_handler(event, context):
    prompt = "Tell me about FPT University"

    body = json.dumps({
        "prompt": "\n\nHuman:" + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 100,
        "temperature": 0.1,
        "top_p": 0.9,
    })
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())
    response_text = response_body.get('completion')
    return response_text
    