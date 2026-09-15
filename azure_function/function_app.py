import azure.functions as func
import logging
import json
import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="receiverendpoint", methods=["POST"])
def receiverendpoint(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing incoming multi-format payload from AWS Lambda.')

    try:
        req_body = req.get_json()
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        blob_name = f"summary_{timestamp}.json"
        
        connect_str = os.environ.get('AzureWebJobsStorage')
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client("ai-summaries")
        
        if not container_client.exists():
            container_client.create_container()
            
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(json.dumps(req_body, indent=2), overwrite=True)

        return func.HttpResponse(
            json.dumps({"status": "success", "file": blob_name}),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error saving blob: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
