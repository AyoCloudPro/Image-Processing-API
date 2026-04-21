resource "google_storage_bucket" "input" {
  name                        = var.input_bucket_name
  project                     = var.project_id
  location                    = var.region
  force_destroy               = var.environment == "dev" ? true : false
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.signed_url_expiry_days
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}


resource "google_storage_bucket" "output" {
  name                        = var.output_bucket_name
  project                     = var.project_id
  location                    = var.region
  force_destroy               = var.environment == "dev" ? true : false
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = var.signed_url_expiry_days
    }
  }

  labels = {
    environment = var.environment
    managed-by  = "terraform"
  }
}


resource "google_storage_bucket_iam_member" "input_writer" {
  bucket = google_storage_bucket.input.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.cloud_run_sa_email}"
}


resource "google_storage_bucket_iam_member" "output_writer" {
  bucket = google_storage_bucket.output.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.cloud_run_sa_email}"
}


resource "google_storage_bucket_iam_member" "output_reader" {
  bucket = google_storage_bucket.output.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.cloud_run_sa_email}"
}
