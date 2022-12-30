terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "3.34.0"
    }

    azapi = {
      source  = "Azure/azapi"
      version = "1.1.0"
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

resource "azurerm_cosmosdb_sql_container" "leases" {
  name                = "leases"
  resource_group_name = azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.webalerts.name
  database_name       = azurerm_cosmosdb_sql_database.webalerts.name

  partition_key_path = "/id"
}


resource "azurerm_log_analytics_workspace" "webalerts" {
  name                = var.loganalytics_workspace_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
}

resource "azurerm_application_insights" "webalerts" {
  name                = var.appinsights_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  workspace_id        = azurerm_log_analytics_workspace.webalerts.id
  application_type    = "web"
}

resource "azapi_resource" "webalerts-containerappenv" {
  name      = "caenv-webalerts-dev"
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id
  type      = "Microsoft.App/managedEnvironments@2022-03-01"

  body = jsonencode({
    properties = {
      daprAIInstrumentationKey = azurerm_application_insights.webalerts.instrumentation_key
      appLogsConfiguration = {
        destination = "log-analytics"
        logAnalyticsConfiguration = {
          customerId = azurerm_log_analytics_workspace.webalerts.workspace_id
          sharedKey  = azurerm_log_analytics_workspace.webalerts.primary_shared_key
        }
      }
    }
  })

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azapi_resource" "dapr_components" {
  name      = "alertqueue"
  parent_id = azapi_resource.webalerts-containerappenv.id
  type      = "Microsoft.App/managedEnvironments/daprComponents@2022-03-01"

  body = jsonencode({
    properties = {
      componentType = "bindings.azure.servicebusqueues"
      version       = "v1"
      metadata = [
        {
          name : "namespaceName"
          value : format("%s.servicebus.windows.net", azurerm_servicebus_namespace.webalerts.name)
        },
        {
          name  = "queueName",
          value = azurerm_servicebus_queue.alert.name
        }
      ]
      scopes = ["scraper", "notifier"]
    }
  })
}

resource "azapi_resource" "container_app" {
  name      = "webalerts-dev-scraper"
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id
  type      = "Microsoft.App/containerApps@2022-03-01"
  identity {
    type = "SystemAssigned"
  }

  body = jsonencode({
    properties : {
      managedEnvironmentId = azapi_resource.webalerts-containerappenv.id
      configuration = {
        activeRevisionsMode : "Single"
        dapr = {
          enabled = true
          appId   = "scraper"
        },
        secrets = [
          {
            name  = "db-conn-str",
            value = azurerm_cosmosdb_account.webalerts.connection_strings[0]
          }
        ]
      }
      template = {
        containers = [{
          image = "ghcr.io/wetrocks/webalerts/scraper:latest"
          name  = "webalerts-scraper"
          resources = {
            cpu    = 0.25
            memory = "0.5Gi"
          }
          env = [
            { name = "DB_ENDPOINT", secretRef = "db-conn-str" },
            { name = "DB_NAME", value = azurerm_cosmosdb_sql_database.webalerts.name },
            { name = "URL", value = var.scrape_url }
          ]
        }],
        scale = {
          maxReplicas = 1
          minReplicas = 0
          rules = [
            {
              name = "noon"
              custom = {
                type = "cron"
                metadata = {
                  timezone        = "America/Kralendijk"
                  start           = "0 12 * * *"
                  end             = "5 12 * * *"
                  desiredReplicas = "1"
                }
              }
            }
          ]
        }
      }
    }
  })

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azapi_resource" "notifier_containerapp" {
  name      = "webalerts-dev-notifier"
  location  = azurerm_resource_group.rg.location
  parent_id = azurerm_resource_group.rg.id
  type      = "Microsoft.App/containerApps@2022-03-01"
  identity {
    type = "SystemAssigned"
  }

  body = jsonencode({
    properties : {
      managedEnvironmentId = azapi_resource.webalerts-containerappenv.id
      configuration = {
        activeRevisionsMode : "Single"
        dapr = {
          enabled     = true
          appId       = "notifier"
          appPort     = 8000
          appProtocol = "http"
        },
        secrets = [
          {
            name  = "db-conn-str",
            value = azurerm_cosmosdb_account.webalerts.connection_strings[0]
          },
          {
            name  = "sb-conn-str",
            value = azurerm_servicebus_namespace.webalerts.default_primary_connection_string
          },
          {
            name  = "sendgrid-api-key",
            value = var.sendgrid_api_key
          }
        ]
      }
      template = {
        containers = [{
          image = "ghcr.io/wetrocks/webalerts/notifier:latest"
          name  = "webalerts-notifier"
          resources = {
            cpu    = 0.25
            memory = "0.5Gi"
          }
          env = [
            { name = "DB_ENDPOINT", secretRef = "db-conn-str" },
            { name = "DB_NAME", value = azurerm_cosmosdb_sql_database.webalerts.name },
            { name = "SENDGRID_API_KEY", secretRef = "sendgrid-api-key" },
            { name = "SENDGRID_SENDER_ID", value = var.sendgrid_sender_id },
            { name = "SENDGRID_SUPPGRP_ID", value = var.sendgrid_suppgroup_id },
            { name = "SENDGRID_LIST_ID", value = var.sendgrid_list_id }
          ]
        }],
        scale = {
          maxReplicas = 1
          minReplicas = 0
          rules = [
            {
              name = "alert-queue-msg"
              custom = {
                type = "azure-servicebus"
                metadata = {
                  queueName              = azurerm_servicebus_queue.alert.name
                  activationMessageCount = 1
                }
                auth = [
                  {
                    secretRef        = "sb-conn-str"
                    triggerParameter = "connection"
                  }
                ]
              }
            }
          ]
        }
      }
    }
  })

  lifecycle {
    ignore_changes = [
      tags
    ]
  }
}

resource "azurerm_role_assignment" "scraper_to_sb" {
  scope                = azurerm_servicebus_namespace.webalerts.id
  role_definition_name = "Azure Service Bus Data Owner"
  principal_id         = azapi_resource.container_app.identity[0].principal_id
}

resource "azurerm_role_assignment" "notifier_to_sb" {
  scope                = azurerm_servicebus_namespace.webalerts.id
  role_definition_name = "Azure Service Bus Data Receiver"
  principal_id         = azapi_resource.notifier_containerapp.identity[0].principal_id
}