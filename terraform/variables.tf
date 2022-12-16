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

variable "scrape_url" {
  description = "URL to scrape"
  type        = string
  nullable    = false
}