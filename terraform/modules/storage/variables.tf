variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for storage buckets"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
}

variable "input_bucket_name" {
  description = "Name of the bucket for original uploaded images"
  type        = string
}

variable "output_bucket_name" {
  description = "Name of the bucket for processed images"
  type        = string
}

variable "cloud_run_sa_email" {
  description = "Service account email used by Cloud Run to access storage buckets"
  type        = string
}

variable "signed_url_expiry_days" {
  description = "Number of days before uploaded objects are deleted"
  type        = number
}
