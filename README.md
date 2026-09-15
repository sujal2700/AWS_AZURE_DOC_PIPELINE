# AWS & Azure Multi-Cloud Document Intelligence Pipeline

An event-driven, multi-cloud document processing pipeline that automatically ingests files uploaded to **AWS S3**, generates structured AI insights using **Google's Gemini 3.6-Flash API**, and persists structured JSON outputs to **Azure Blob Storage** via **Azure Functions**.

---

## 🏗️ Architecture Diagram

<img width="1408" height="768" alt="multi_cloud_diagram" src="https://github.com/user-attachments/assets/085e00b3-d3fb-4f19-8246-2319d4ee5759" />

### Data Flow Breakdown

1. **Document Ingestion (AWS S3)**: Multi-format files (`.pdf`, `.txt`, `.csv`, `.json`, `.md`) are uploaded to the primary ingestion bucket (`aws-azure-pipeline`).
2. **Compute & Parsing (AWS Lambda)**: An `s3:ObjectCreated` event triggers a Python 3.12 serverless function. Plain text files are decoded via standard UTF-8, while binary documents (`.pdf`) are base64-encoded for multimodal processing.
3. **Generative AI Analysis (Google Gemini 3.6-Flash)**: Lambda invokes the Gemini REST API via `urllib`, passing structured prompts to generate executive summaries, entity extraction, and classification tags.
4. **Cross-Cloud Integration (Azure Function App)**: Lambda formats the insight payload and posts it over HTTP to an Azure Function endpoint (`/api/receiverendpoint`).
5. **Persistence Tier (Azure Blob Storage)**: The Azure Function processes the incoming POST request and writes a timestamped JSON file to the `ai-summaries` container.

---

## 📁 Repository Structure

```text
AWS_AZURE_DOC_PIPELINE/
├── README.md                   # System documentation and execution guide
├── architecture-diagram.png    # High-level architecture pipeline graphic
├── .gitignore                  # Git ignore rules for keys & temporary artifacts
├── aws_lambda/
│   └── lambda_function.py      # S3 handler, format parser, Gemini API & Azure proxy
├── azure_function/
│   ├── function_app.py         # HTTP receiver endpoint & Azure Blob storage writer
│   ├── host.json               # Azure Function host runtime configuration
│   └── requirements.txt        # Python dependencies for Azure Function
└── sample_files/
    ├── sample_contract.pdf     # Binary test payload
    ├── sample_data.json        # JSON test payload
    └── sample_log.txt          # Plain text test log
```
---

## ⚡ Core Features

* **Multi-Cloud Native Mechanics**: Seamlessly bridges AWS compute and storage tiers with Azure serverless execution and persistence services.
* **Dynamic Multi-Format Support**: Handles standard UTF-8 text formats natively (`.txt`, `.json`, `.csv`, `.md`) and binary formats (`.pdf`) via native inline base64 multimodal encoding for Gemini.
* **Zero-Dependency Lambda Deployment**: Implemented using standard Python 3.12 libraries (`urllib`, `base64`, `json`, `os`), eliminating cold-start layer overhead and deployment package bloat.
* **Event-Driven Resilience**: Asynchronous execution model that scales down to zero when idle, minimizing cloud infrastructure operational costs.

---

## 🔧 Environment Variables

### AWS Lambda
| Variable Name | Description | Example / Format |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google AI Studio API Key | `AIzaSy...` |
| `AZURE_RECEIVER_URL` | Azure Function Target HTTP Endpoint | `https://<app_name>.azurewebsites.net/api/receiverendpoint` |

### Azure Function App
| Variable Name | Description |
| :--- | :--- |
| `AzureWebJobsStorage` | Connection string for target Azure Storage Account |

---

## 📸 End-to-End Pipeline Execution & Verification

To demonstrate cross-cloud event processing, the pipeline was verified end-to-end. Below is the step-by-step visual proof captured across each stage:

### Stage 1: Document Upload (AWS S3 Ingestion)
The document (`tech.txt`) is uploaded to the primary AWS S3 bucket, triggering the `s3:ObjectCreated` event notification.

  <img width="940" height="739" alt="image" src="https://github.com/user-attachments/assets/2bafc292-9a02-4fd4-92a4-86f4efa761d4" />
---

### Stage 2: Lambda Trigger & Gemini Processing (AWS CloudWatch Logs)
AWS Lambda captures the S3 event, parses content/binary streams, sends the payload to Gemini 3.6-Flash REST API, and logs a successful `HTTP 200` response from the downstream Azure Function endpoint.

<img width="940" height="688" alt="image" src="https://github.com/user-attachments/assets/bfef5d79-95bb-45f6-ad42-e5e6a410fa81" />

---

### Stage 3: HTTP Endpoint Receiver (Azure Function)
The Azure Function App receives the HTTP POST payload from AWS Lambda containing the AI-generated summary and metadata.

<img width="940" height="696" alt="image" src="https://github.com/user-attachments/assets/022b8550-b371-4f71-a88a-dc034746b5f7" />

---

### Stage 4: Persistent Output Storage (Azure Blob Container)
The structured output JSON file is saved dynamically inside the Azure Storage `ai-summaries` container with a unique timestamp string.

<img width="940" height="600" alt="image" src="https://github.com/user-attachments/assets/2da130c2-98bf-4b52-91c2-d8ebff245484" />

<img width="940" height="676" alt="image" src="https://github.com/user-attachments/assets/e51e52c3-3338-4474-a3e0-251e697ae7e3" />







  

