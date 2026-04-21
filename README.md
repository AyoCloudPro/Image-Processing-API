# Image Processing API

![CI/CD](https://github.com/AyoCloudPro/Image-Processing-API/actions/workflows/deploy.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Terraform](https://img.shields.io/badge/terraform-%3E%3D1.7-purple.svg)
![GCP](https://img.shields.io/badge/cloud-GCP-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A production-ready image processing REST API built with **FastAPI** and deployed on **GCP Cloud Run**. Supports image resizing, compression, and format conversion. Infrastructure is fully defined as code using **Terraform** with separate dev and prod environments, automated via a **GitHub Actions** CI/CD pipeline.

---

## Features

- **Image processing** — resize, compress, and convert images (JPEG, PNG, WebP)
- **Auto-scaling** — Cloud Run scales instances up under load and down to zero when idle
- **Secure storage** — processed images stored in GCS with time-limited signed URLs
- **API Gateway** — authentication and rate limiting at the infrastructure level
- **Infrastructure as code** — all GCP resources managed via modular Terraform
- **CI/CD pipeline** — automated linting, testing, and deployment via GitHub Actions
- **Observability** — Cloud Monitoring dashboards, alerting policies, and structured logging
- **Load tested** — verified with Locust under concurrent user simulation

---

## Architecture

![Architecture Diagram](assets/architecture.png)

**CI/CD Flow:**
```
Push to develop  →  Lint + Test  →  Build Image  →  Deploy to Dev
Push to main     →  Lint + Test  →  Build Image  →  Deploy to Prod
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI (Python 3.13) |
| Image processing | Pillow |
| Compute | GCP Cloud Run |
| Storage | GCP Cloud Storage |
| Auth + Rate limiting | GCP API Gateway |
| Observability | GCP Cloud Monitoring |
| Infrastructure | Terraform (modular) |
| CI/CD | GitHub Actions |
| Load testing | Locust |
| Container registry | Google Container Registry |

---

## Project Structure

```
image-processing-api/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment-based config
│   ├── routers/
│   │   └── images.py           # Image processing endpoints
│   ├── services/
│   │   ├── image_processor.py  # Pillow processing logic
│   │   └── storage.py          # GCS upload + signed URLs
│
├── terraform/
│   ├── main.tf                 # Root config + Terraform Cloud backend
│   ├── variables.tf            # Input variable definitions
│   ├── outputs.tf              # Output values
│   ├── environments/
│   │   ├── dev.tfvars          # Dev variable reference
│   │   └── prod.tfvars         # Prod variable reference
│   └── modules/
│       ├── cloud_run/          # Cloud Run service + service account
│       ├── storage/            # GCS buckets + IAM bindings
│       └── monitoring/         # Alert policies + notification channels
├── tests/
│   ├── unit/
│   │   └── test_image_processor.py
│   └── integration/
│       └── test_api.py
├── load_testing/
│   └── locustfile.py           # Locust load test scenarios
├── Dockerfile                  # Multi-stage production build
├── requirements.txt
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.13
- Docker
- Terraform >= 1.7
- GCP project with billing enabled
- Terraform Cloud account

### Local Development

**1. Clone the repository**
```bash
git clone https://github.com/AyoCloudPro/Image-Processing-API.git
cd image-processing-api
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
pip install pytest httpx
```

**3. Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your values
```

**4. Run the app locally**
```bash
uvicorn app.main:app --reload --port 8080
```

Open `http://localhost:8080/docs` to explore the API interactively.

**5. Run tests**
```bash
python -m pytest tests/ -v
```

---

## Deployment

### Infrastructure Setup

All infrastructure is managed via Terraform Cloud. Before deploying:

**1. Create two Terraform Cloud workspaces** tagged `image-processing-api`:
- `image-processing-api-dev`
- `image-processing-api-prod`

**2. Set variables in each workspace** (refer to `terraform/environments/dev.tfvars` and `prod.tfvars` for the full list). Mark sensitive values accordingly.

**3. Add `GOOGLE_CREDENTIALS`** as an environment variable in each workspace containing your GCP service account JSON.

**4. Update `terraform/main.tf`** with your Terraform Cloud organisation name.

### GitHub Actions Setup

Add the following secrets to your GitHub repository:

| Secret | Description |
|---|---|
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_SA_KEY` | GCP service account JSON key |
| `TF_API_TOKEN` | Terraform Cloud API token |

### GCP Service Account Roles

The Terraform service account requires the following roles:

| Role | Purpose |
|---|---|
| `roles/run.admin` | Manage Cloud Run services |
| `roles/storage.admin` | Create and manage GCS buckets |
| `roles/monitoring.admin` | Create alert policies |
| `roles/iam.serviceAccountAdmin` | Create Cloud Run service account |
| `roles/iam.serviceAccountUser` | Assign service account to Cloud Run |
| `roles/resourcemanager.projectIamAdmin` | Grant IAM roles |
| `roles/artifactregistry.admin` | Manage container images |

### Deploy

```bash
# Deploy to dev (push to develop branch)
git push origin develop

# Deploy to prod (push to main branch)
git push origin main

# Destroy infrastructure (GitHub Actions → Run workflow)
# Select destroy-dev or destroy-prod from the dropdown
```

---

## API Reference

### Base URL
```
https://YOUR-API-GATEWAY-URL
```

### Authentication
All requests require an API key passed as a header:
```
X-API-Key: your-api-key
```

---

### Health Check

```http
GET /health
```

**Response**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### Process Image

```http
POST /images/process
```

**Query Parameters**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `width` | integer | No | — | Target width in pixels (max 8000) |
| `height` | integer | No | — | Target height in pixels (max 8000) |
| `quality` | integer | No | 85 | Output quality 1–95 (JPEG/WebP only) |
| `output_format` | string | No | `jpeg` | Output format: `jpeg`, `png`, `webp` |

**Request**
```bash
curl -X POST "https://YOUR-API-GATEWAY-URL/images/process?width=800&height=600&quality=85&output_format=webp" \
  -H "X-API-Key: your-api-key" \
  -F "file=@photo.jpg"
```

**Response**
```json
{
  "message": "Image processed successfully.",
  "download_url": "https://storage.googleapis.com/...",
  "original_filename": "photo.jpg",
  "output_format": "webp",
  "width": 800,
  "height": 600,
  "quality": 85
}
```

**Error Responses**

| Status | Description |
|---|---|
| `413` | File exceeds 10MB limit |
| `415` | Unsupported file type |
| `422` | Invalid parameters |
| `502` | Storage service unavailable |

---

## Load Testing

Install Locust:
```bash
pip install locust
```

Run against your deployed API:
```bash
locust -f load_testing/locustfile.py --host=https://YOUR-CLOUD-RUN-URL
```

Open `http://localhost:8089` and configure:
- **Users:** 50
- **Spawn rate:** 5
- **Duration:** 2–3 minutes

The test simulates a realistic mix of requests — small resizes, medium resizes, compression, format conversion, and health checks — weighted by typical usage frequency.

### Results

> _Add your Locust screenshot here showing requests/sec and response times_

> _Add your Cloud Monitoring screenshot here showing instance count scaling up under load_

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GCP_PROJECT_ID` | Yes | — | GCP project ID |
| `GCS_INPUT_BUCKET` | Yes | — | GCS bucket for original uploads |
| `GCS_OUTPUT_BUCKET` | Yes | — | GCS bucket for processed images |
| `MAX_UPLOAD_SIZE_MB` | No | `10` | Maximum upload size in MB |
| `SIGNED_URL_EXPIRY_MINUTES` | No | `60` | Signed URL validity in minutes |

---

## Dev vs Prod Environments

| Setting | Dev | Prod |
|---|---|---|
| Min instances | 0 (scale to zero) | 1 (always warm) |
| Max instances | 3 | 10 |
| CPU | 1 vCPU | 2 vCPU |
| Memory | 512Mi | 1Gi |
| Concurrency | 40 | 80 |
| Latency alert | > 5000ms | > 3000ms |
| Error rate alert | > 10% | > 5% |

---

## License

MIT