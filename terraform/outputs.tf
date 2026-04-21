output "cloud_run_url" {
  description = "Public URL of the deployed Cloud Run service"
  value       = module.cloud_run.service_url
}

output "input_bucket_name" {
  description = "GCS input bucket name"
  value       = module.storage.input_bucket_name
  sensitive   = true
}

output "output_bucket_name" {
  description = "GCS output bucket name"
  value       = module.storage.output_bucket_name
  sensitive   = true
}

output "service_account_email" {
  description = "Cloud Run service account email"
  value       = module.cloud_run.service_account_email
  sensitive   = true
}
