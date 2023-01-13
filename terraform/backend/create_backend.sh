#!/bin/bash

source ./config.azurerm.tfbackend

# Create resource group
az group create --name $resource_group_name --location eastus

# Create storage account
az storage account create --resource-group $resource_group_name --name $storage_account_name --sku Standard_LRS \
--access-tier Cool \
--encryption-services blob \
--allow-blob-public-access false \
--allow-shared-key-access

# Create blob container
az storage container create --name $container_name --account-name $storage_account_name

