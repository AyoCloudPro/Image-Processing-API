variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
}

variable "service_name" {
  description = "Cloud Run service name to monitor"
  type        = string
}

variable "alert_email" {
  description = "Email address to receive alerting notifications"
  type        = string
}

variable "latency_threshold_ms" {
  description = "P99 request latency threshold in milliseconds before alerting"
  type        = number
}

variable "error_rate_threshold" {
  description = "5xx error rate threshold (0.0–1.0) before alerting"
  type        = number
}
