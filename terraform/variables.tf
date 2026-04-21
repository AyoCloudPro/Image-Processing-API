variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for all resources"
  type        = string
}

variable "credentials" {
  description = "GCP service acccount key"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment must be either 'dev' or 'prod'."
  }
}

variable "service_name" {
  description = "Base name for the Cloud Run service"
  type        = string
  default     = "image-processing-api"
}

variable "image" {
  description = "Full container image URL to deploy"
  type        = string
}

variable "min_instances" {
  description = "Minimum Cloud Run instances (0 = scale to zero)"
  type        = number
}

variable "max_instances" {
  description = "Maximum Cloud Run instances"
  type        = number
}

variable "concurrency" {
  description = "Max concurrent requests per Cloud Run instance"
  type        = number
}

variable "cpu" {
  description = "vCPU allocation per instance"
  type        = string
}

variable "memory" {
  description = "Memory allocation per instance"
  type        = string
}

variable "signed_url_expiry_days" {
  description = "Days before GCS objects are auto-deleted"
  type        = number
}

variable "alert_email" {
  description = "Email for Cloud Monitoring alert notifications"
  type        = string
}

variable "latency_threshold_ms" {
  description = "P99 latency threshold in milliseconds before alerting"
  type        = number
}

variable "error_rate_threshold" {
  description = "5xx error rate threshold (0.0-1.0) before alerting"
  type        = number
}
