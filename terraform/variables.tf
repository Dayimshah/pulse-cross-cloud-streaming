# variables.tf
# -----------------------------------------------------------------------------
# Inputs to the config. Declaring them here (instead of hardcoding values in the
# resources) is what makes the config reusable: change a value in one place and
# everything downstream updates. Actual values go in terraform.tfvars (gitignored).
# -----------------------------------------------------------------------------

variable "name_prefix" {
  description = "Short, lowercase prefix for all resource names (keeps them grouped + unique)."
  type        = string
  default     = "pulse-dayim"
}

variable "aws_region" {
  description = "AWS region where S3 + DynamoDB are created."
  type        = string
  default     = "ap-south-1" # Mumbai
}

variable "azure_subscription_id" {
  description = "The Azure subscription Terraform builds into (from `az account show`)."
  type        = string
}

variable "azure_location" {
  description = "Azure region for the resource group + storage + Cosmos."
  type        = string
  default     = "centralindia"
}
