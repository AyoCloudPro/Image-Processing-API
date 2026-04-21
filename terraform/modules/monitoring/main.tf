resource "google_monitoring_notification_channel" "email" {
  project      = var.project_id
  display_name = "Email Alerts (${var.environment})"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}


resource "google_monitoring_alert_policy" "high_latency" {
  project      = var.project_id
  display_name = "[${var.environment}] High P99 Latency — ${var.service_name}"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "P99 latency > ${var.latency_threshold_ms}ms"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.service_name}-${var.environment}\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.latency_threshold_ms

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_99"
        cross_series_reducer = "REDUCE_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  documentation {
    content   = "P99 request latency for ${var.service_name} (${var.environment}) has exceeded ${var.latency_threshold_ms}ms. Check Cloud Run logs for slow processing jobs."
    mime_type = "text/markdown"
  }
}


resource "google_monitoring_alert_policy" "high_error_rate" {
  project      = var.project_id
  display_name = "[${var.environment}] High Error Rate — ${var.service_name}"
  combiner     = "OR"
  enabled      = true

  conditions {
    display_name = "5xx error rate > ${var.error_rate_threshold * 100}%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.service_name}-${var.environment}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.error_rate_threshold

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  documentation {
    content   = "5xx error rate for ${var.service_name} (${var.environment}) has exceeded ${var.error_rate_threshold * 100}%. Check Cloud Run logs immediately."
    mime_type = "text/markdown"
  }
}


resource "google_monitoring_alert_policy" "scaling_ceiling" {
  project      = var.project_id
  display_name = "[${var.environment}] Scaling Ceiling Warning — ${var.service_name}"
  combiner     = "OR"
  enabled      = var.environment == "prod" ? true : false

  conditions {
    display_name = "Active instances > 8"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.service_name}-${var.environment}\" AND metric.type=\"run.googleapis.com/container/instance_count\""
      duration        = "120s"
      comparison      = "COMPARISON_GT"
      threshold_value = 8

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_MEAN"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  documentation {
    content   = "Cloud Run instance count for ${var.service_name} is approaching the maximum. Consider increasing max_instances or investigating the traffic spike."
    mime_type = "text/markdown"
  }
}
