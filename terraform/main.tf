terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.28.0"
    }
  }

  cloud {
    
    organization = "digitalmages"

    workspaces {
      tags = [ "image-processing-api" ]
    }
  }
}

provider "google" {
  # Configuration options
  project = var.project_id
  region  = var.region
  credentials = var.credentials
}


# --- Modules ---
module "storage" {
  source = "./modules/storage"

  project_id             = var.project_id
  region                 = var.region
  environment            = var.environment
  input_bucket_name      = "${var.project_id}-img-input-${var.environment}"
  output_bucket_name     = "${var.project_id}-img-output-${var.environment}"
  cloud_run_sa_email     = module.cloud_run.service_account_email
  signed_url_expiry_days = var.signed_url_expiry_days
}

module "cloud_run" {
  source = "./modules/cloud_run"

  project_id         = var.project_id
  region             = var.region
  environment        = var.environment
  service_name       = var.service_name
  image              = var.image
  min_instances      = var.min_instances
  max_instances      = var.max_instances
  concurrency        = var.concurrency
  cpu                = var.cpu
  memory             = var.memory
  input_bucket_name  = module.storage.input_bucket_name
  output_bucket_name = module.storage.output_bucket_name
}

module "monitoring" {
  source = "./modules/monitoring"

  project_id           = var.project_id
  environment          = var.environment
  service_name         = var.service_name
  alert_email          = var.alert_email
  latency_threshold_ms = var.latency_threshold_ms
  error_rate_threshold = var.error_rate_threshold
}