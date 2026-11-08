# outputs.tf
# -----------------------------------------------------------------------------
# After `terraform apply`, these print the names/endpoints the pipeline code
# needs. The `sensitive = true` ones are hidden on screen but readable via
# `terraform output -raw <name>` when we wire up the workers.
# -----------------------------------------------------------------------------

output "aws_bronze_bucket" {
  description = "S3 bucket name for the Bronze (raw) layer."
  value       = aws_s3_bucket.bronze.id
}

output "aws_ledger_table" {
  description = "DynamoDB table name for the transfer ledger."
  value       = aws_dynamodb_table.ledger.name
}

output "azure_storage_account" {
  description = "ADLS Gen2 storage account name (holds silver + gold)."
  value       = azurerm_storage_account.lake.name
}

output "azure_storage_key" {
  description = "Primary access key for the storage account."
  value       = azurerm_storage_account.lake.primary_access_key
  sensitive   = true
}

output "cosmos_endpoint" {
  description = "Cosmos DB endpoint URL (dashboard + consumer read/write here)."
  value       = azurerm_cosmosdb_account.serving.endpoint
}

output "cosmos_key" {
  description = "Cosmos DB primary key."
  value       = azurerm_cosmosdb_account.serving.primary_key
  sensitive   = true
}
