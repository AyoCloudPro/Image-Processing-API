output "notification_channel_id" {
  description = "ID of the email notification channel"
  value       = google_monitoring_notification_channel.email.id
}


output "latency_alert_policy_name" {
  description = "Name of the latency alerting policy"
  value       = google_monitoring_alert_policy.high_latency.name
}


output "error_rate_alert_policy_name" {
  description = "Name of the error rate alerting policy"
  value       = google_monitoring_alert_policy.high_error_rate.name
}
