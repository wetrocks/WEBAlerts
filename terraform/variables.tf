variable "resource_group_name" {
  description = "Resource group for all resources"
  type        = string
  nullable    = false
}

variable "location" {
  description = "Location for all resources"
  type        = string
  nullable    = false
  default     = "eastus"
}

variable "servicebus_namespace_name" {
  description = "Service Bus Namespace name"
  type        = string
  nullable    = false
}

variable "servicebus_alert_queue_name" {
  description = "Service Bus Queue name for alerts"
  type        = string
  nullable    = false
  default     = "sbq-alerts"
}

variable "servicebus_deadletter_queue_name" {
  description = "Service Bus Queue name for undelivered alerts"
  type        = string
  nullable    = false
  default     = "sbq-deadletter"
}

variable "cosmos_acct_name" {
  description = "CosmosDB account name"
  type        = string
  nullable    = false
}

variable "cosmos_db_name" {
  description = "Cosmos database name"
  type        = string
  nullable    = false
  default     = "cosmos-notificationdb"
}

variable "cosmos_alert_container_name" {
  description = "DB Container for storing alert data"
  type        = string
  nullable    = false
  default     = "notifications"
}

variable "loganalytics_workspace_name" {
  description = "Log Analyics workspace name"
  type        = string
  nullable    = false
}

variable "appinsights_name" {
  description = "Application insights resource name"
  type        = string
  nullable    = false
}

variable "containerappenv_name" {
  description = "Name of container apps instance"
  type        = string
  nullable    = false
}

variable "scraper_app_name" {
  description = "Name of scraper container app"
  type        = string
  nullable    = false
}

variable "notifier_app_name" {
  description = "Name of notifier container app"
  type        = string
  nullable    = false
}

variable "scrape_url" {
  description = "URL to scrape"
  type        = string
  nullable    = false
}

variable "sendgrid_api_key" {
  description = "SendGrid API key"
  type        = string
  nullable    = false
  sensitive   = true
}

variable "sendgrid_sender_id" {
  description = "SendGrid sender id"
  type        = string
  nullable    = false
}

variable "sendgrid_suppgroup_id" {
  description = "SendGrid suppression group id"
  type        = string
  nullable    = false
}

variable "sendgrid_list_id" {
  description = "SendGrid list id"
  type        = string
  nullable    = false
}
