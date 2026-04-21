output "input_bucket_name" {
  description = "Name of the input GCS bucket"
  value       = google_storage_bucket.input.name
}


output "output_bucket_name" {
  description = "Name of the output GCS bucket"
  value       = google_storage_bucket.output.name
}
