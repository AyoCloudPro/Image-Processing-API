output "service_url" {
  description = "The URL of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.app.uri
}


output "service_account_email" {
  description = "Email of the Cloud Run service account"
  value       = google_service_account.cloud_run_sa.email
}


output "service_name" {
  description = "Full name of the deployed Cloud Run service"
  value       = google_cloud_run_v2_service.app.name
}
