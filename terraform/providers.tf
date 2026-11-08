# providers.tf
# -----------------------------------------------------------------------------
# This file declares WHICH clouds Terraform will build in. The headline of this
# whole project lives here: TWO cloud providers (AWS + Azure) in ONE config.
# A single `terraform apply` provisions infrastructure across both clouds.
# -----------------------------------------------------------------------------

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# AWS provider — authenticates automatically using the credentials you stored
# with `aws configure` (the pulse-terraform IAM user). No keys live in this file.
provider "aws" {
  region = var.aws_region
}

# Azure provider — authenticates automatically using your `az login` session.
# subscription_id pins it to the exact subscription Terraform should build into.
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

# Used to generate a short random suffix so globally-unique names (S3 bucket,
# Azure storage account) never collide with anyone else's.
provider "random" {}
