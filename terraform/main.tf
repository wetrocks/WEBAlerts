terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.34.0"
    }
  }

  required_version = ">= 1.3.6"

  backend "azurerm" {
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location

  tags = {
  }
}

resource "azurerm_servicebus_namespace" "webalerts" {
  name                = var.servicebus_namespace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Basic"

  tags = {
  }
}

resource "azurerm_servicebus_queue" "deadletter" {
  name         = var.servicebus_deadletter_queue_name
  namespace_id = azurerm_servicebus_namespace.webalerts.id
}

resource "azurerm_servicebus_queue" "alert" {
  name                              = var.servicebus_alert_queue_name
  namespace_id                      = azurerm_servicebus_namespace.webalerts.id
  forward_dead_lettered_messages_to = azurerm_servicebus_queue.deadletter.name
}

resource "azurerm_user_assigned_identity" "webalerts" {
  name                = var.userassigned_id
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_role_assignment" "example" {
  scope                = azurerm_servicebus_namespace.webalerts.id
  role_definition_name = "Azure Service Bus Data Owner"
  principal_id         = azurerm_user_assigned_identity.webalerts.principal_id
}

resource "azurerm_cosmosdb_account" "webalerts" {
  name                = var.cosmos_acct_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  enable_automatic_failover = false

  capabilities {
    name = "EnableServerless"
  }

  consistency_policy {
    consistency_level       = "Session"
    max_interval_in_seconds = 5
    max_staleness_prefix    = 100
  }

  geo_location {
    location          = azurerm_resource_group.rg.location
    failover_priority = 0
    zone_redundant    = false
  }
}

resource "azurerm_cosmosdb_sql_database" "webalerts" {
  name                = var.cosmos_db_name
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.webalerts.name
}

resource "azurerm_cosmosdb_sql_container" "notifications" {
  name                = var.cosmos_alert_container_name
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.webalerts.name
  database_name       = azurerm_cosmosdb_sql_database.webalerts.name

  partition_key_path = "/notificationType"
}


resource "azurerm_log_analytics_workspace" "webalerts" {
  name                       = var.loganalytics_workspace_name
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  sku                        = "PerGB2018"
}

resource "azurerm_application_insights" "webalerts" {
  name                = var.appinsights_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.webalerts.id
  application_type    = "web"
}
