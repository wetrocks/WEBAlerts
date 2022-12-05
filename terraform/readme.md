# Create backend
create config.azurerm.tfbackend 
resource_group_name="rg-tfstate"
storage_account_name="tfstatewebalerts"
container_name="tfstate"
key="webalerts.tfstate"


./create_backend.sh 

# Initialize
terraform init -backend-config=./backend/config.azurerm.tfbackend 