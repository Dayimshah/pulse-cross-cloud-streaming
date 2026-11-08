# azure.tf
# -----------------------------------------------------------------------------
# The Azure side = the ANALYTICS / SERVING cloud. Resources:
#   1. Resource group   -> container holding everything (clean teardown)
#   2. Storage account  -> ADLS Gen2 (Blob + Hierarchical Namespace) for Silver/Gold
#   3. Blob containers  -> silver, gold
#   4. Cosmos DB (free) -> the fast serving layer the dashboard reads
# -----------------------------------------------------------------------------

# --- RESOURCE GROUP -----------------------------------------------------------
# Everything Azure lives inside this. `terraform destroy` removes it all at once.
resource "azurerm_resource_group" "pulse" {
  name     = "${var.name_prefix}-rg"
  location = var.azure_location
}

# --- ADLS GEN2 STORAGE --------------------------------------------------------
# Storage account names: globally unique, 3-24 chars, lowercase + digits ONLY
# (no hyphens). So we strip hyphens from the prefix and append the suffix.
resource "azurerm_storage_account" "lake" {
  name                     = substr("${replace(var.name_prefix, "-", "")}${random_string.suffix.result}", 0, 24)
  resource_group_name      = azurerm_resource_group.pulse.name
  location                 = azurerm_resource_group.pulse.location
  account_tier             = "Standard"
  account_replication_type = "LRS" # locally redundant = cheapest, fine for a demo

  # THE KEY LINE: Hierarchical Namespace on = this is ADLS Gen2, not flat Blob.
  is_hns_enabled = true
}

# Silver = cleaned/validated events. Gold = computed windowed analytics.
resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.lake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.lake.name
  container_access_type = "private"
}

# --- COSMOS DB (FREE TIER) ----------------------------------------------------
# The serving layer. enable_free_tier = true gives 1000 RU/s + 25GB free forever.
# NOTE: Azure allows only ONE free-tier Cosmos account per subscription.
resource "azurerm_cosmosdb_account" "serving" {
  name                = "${var.name_prefix}-cosmos-${random_string.suffix.result}"
  resource_group_name = azurerm_resource_group.pulse.name
  location            = azurerm_resource_group.pulse.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  free_tier_enabled = true

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = azurerm_resource_group.pulse.location
    failover_priority = 0
  }
}

# A SQL (core) database + container to hold the latest Gold aggregates.
resource "azurerm_cosmosdb_sql_database" "analytics" {
  name                = "analytics"
  resource_group_name = azurerm_resource_group.pulse.name
  account_name        = azurerm_cosmosdb_account.serving.name
  # Throughput shared across the DB, within the free 1000 RU/s.
  throughput = 400
}

resource "azurerm_cosmosdb_sql_container" "metrics" {
  name                = "metrics"
  resource_group_name = azurerm_resource_group.pulse.name
  account_name        = azurerm_cosmosdb_account.serving.name
  database_name       = azurerm_cosmosdb_sql_database.analytics.name
  partition_key_paths = ["/metric_type"]
}
