# aws.tf
# -----------------------------------------------------------------------------
# The AWS side = the SOURCE cloud. Two resources:
#   1. S3 bucket    -> the Bronze layer (permanent raw-event archive)
#   2. DynamoDB     -> the ledger (the brain of exactly-once + reconciliation)
# -----------------------------------------------------------------------------

# A short random suffix so the S3 bucket name is globally unique across all AWS.
resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# --- BRONZE LAYER -------------------------------------------------------------
# Every raw event the AWS consumer reads from Kafka is written here as-is.
# This is the durable source of truth; it's why Kafka only needs short retention.
resource "aws_s3_bucket" "bronze" {
  bucket = "${var.name_prefix}-bronze-${random_string.suffix.result}"
}

# Keep the bucket private — no public access. Security hygiene.
resource "aws_s3_bucket_public_access_block" "bronze" {
  bucket                  = aws_s3_bucket.bronze.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning on Bronze: if the same object key is ever rewritten, S3 keeps
# history. Cheap insurance for an archive layer.
resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- THE LEDGER ---------------------------------------------------------------
# This is the correctness engine. Each processed batch gets one item:
#   batch_id (PK) -> partition, start_offset, end_offset, content_hash,
#                    event_count, revenue_total, status
# The consumer checks this table on replay to avoid double-counting, and the
# Azure side reads it to reconcile before publishing analytics.
# PAY_PER_REQUEST = on-demand billing = free-tier friendly, no capacity to manage.
resource "aws_dynamodb_table" "ledger" {
  name         = "${var.name_prefix}-ledger"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "batch_id"

  attribute {
    name = "batch_id"
    type = "S"
  }
}
