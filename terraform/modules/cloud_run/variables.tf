variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region to deploy Cloud Run service"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service"
  type        = string
}

variable "image" {
  description = "Full container image URL (e.g. gcr.io/project/image:tag)"
  type        = string
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances (0 = scale to zero)"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
}

variable "concurrency" {
  description = "Maximum number of concurrent requests per instance"
  type        = number
}

variable "cpu" {
  description = "CPU allocated per instance (e.g. '1' or '2')"
  type        = string
}

variable "memory" {
  description = "Memory allocated per instance (e.g. '512Mi' or '1Gi')"
  type        = string
}

variable "input_bucket_name" {
  description = "GCS input bucket name passed as env var to the service"
  type        = string
}

variable "output_bucket_name" {
  description = "GCS output bucket name passed as env var to the service"
  type        = string
}
