import os
import json
import base64
import urllib.parse
import urllib.request
import boto3

s3_client = boto3.client('s3')

MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.json': 'application/json',
    '.csv': 'text/csv',
    '.md': 'text/markdown'
}

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(record['s3']['object']['key'], encoding='utf-8')
        
        print(f"Processing object '{object_key}' from bucket '{bucket_name}'")
        
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        raw_body = s3_response['Body'].read()
        file_ext = os.path.splitext(object_key)[1].lower()
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        prompt_text = (
            "Analyze the attached document content. Provide a concise summary, "
            "extract key entities/topics, and provide an executive classification tag."
        )

        if file_ext in ['.pdf']:
            base64_data = base64.b64encode(raw_body).decode('utf-8')
            mime_type = MIME_TYPES.get(file_ext, 'application/pdf')
            parts = [
                {"text": prompt_text},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_data
                    }
                }
            ]
        else:
            file_content = raw_body.decode('utf-8')
            parts = [
                {"text": f"{prompt_text}\n\nDocument Content:\n{file_content[:4000]}"}
            ]

        gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"
        
        payload = {"contents": [{"parts": parts}]}
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        
        req = urllib.request.Request(
            gemini_url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers=headers, 
            method='POST'
        )
        
        with urllib.request.urlopen(req) as response:
            res_body = json.loads(response.read().decode('utf-8'))
            ai_insight = res_body['candidates'][0]['content']['parts'][0]['text']
        
        print(f"Gemini Analysis successful for: {object_key}")
        
        downstream_payload = {
            "source_bucket": bucket_name,
            "source_key": object_key,
            "file_type": file_ext,
            "file_size": s3_response.get('ContentLength'),
            "ai_summary": ai_insight,
            "status": "SUCCESS"
        }

        azure_endpoint = os.environ.get(
            'AZURE_RECEIVER_URL', 
            'https://func-aws-azure-receiver-6957.azurewebsites.net/api/receiverendpoint'
        )

        azure_req = urllib.request.Request(
            azure_endpoint,
            data=json.dumps(downstream_payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(azure_req) as azure_response:
            azure_reply = azure_response.read().decode('utf-8')
            print(f"Azure Response ({azure_response.status}): {azure_reply}")

        return {"statusCode": 200, "body": json.dumps(downstream_payload)}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        print(f"HTTPError {e.code} on URL: {e.filename} | Body: {error_body}")
        raise e
    except Exception as e:
        print(f"Error processing pipeline event: {str(e)}")
        raise e
