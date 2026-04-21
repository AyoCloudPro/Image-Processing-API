# Dedicated service account for Cloud Run — follows least-privilege principle
resource "google_service_account" "cloud_run_sa" {
  project      = var.project_id
  account_id   = "${var.service_name}-sa"
  display_name = "Service Account for ${var.service_name} (${var.environment})"
}

resource "google_cloud_run_v2_service" "app" {
  deletion_protection = false
  name     = "${var.service_name}-${var.environment}"
  project  = var.project_id
  location = var.region

  template {
    service_account = google_service_account.cloud_run_sa.email

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    max_instance_request_concurrency = var.concurrency

    containers {
      image = var.image

      resources {
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
        # CPU is only allocated during request processing (cost-efficient)
        cpu_idle = false
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_INPUT_BUCKET"
        value = var.input_bucket_name
      }

      env {
        name  = "GCS_OUTPUT_BUCKET"
        value = var.output_bucket_name
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      # Health check — Cloud Run uses this to verify the instance is ready
      startup_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        initial_delay_seconds = 2
        period_seconds        = 5
        failure_threshold     = 3
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8080
        }
        period_seconds    = 30
        failure_threshold = 3
      }
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}

# Allow unauthenticated requests — API Gateway sits in front and handles auth
# So Cloud Run itself is open, but only reachable via the gateway
resource "google_cloud_run_v2_service_iam_member" "allow_unauthenticated" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.app.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow the service account to sign its own tokens
# Required for generating signed GCS URLs from Cloud Run
resource "google_service_account_iam_member" "token_creator" {
  service_account_id = google_service_account.cloud_run_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
