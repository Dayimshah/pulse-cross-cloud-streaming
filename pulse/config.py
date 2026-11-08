"""
config.py
Loads all secrets from .env and exposes them as typed settings. Every other
module imports from here, so credentials live in exactly one place and are
never hardcoded. Fails loudly at startup if something required is missing.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the project root


def _require(key: str) -> str:
    val = os.getenv(key)
    if not val or val.startswith("<PASTE"):
        raise RuntimeError(
            f"Missing required env var: {key}. "
            f"Fill it in your .env file before running."
        )
    return val


# ---- Kafka (Confluent Cloud) ----
KAFKA_BOOTSTRAP = _require("KAFKA_BOOTSTRAP")
KAFKA_API_KEY = _require("KAFKA_API_KEY")
KAFKA_API_SECRET = _require("KAFKA_API_SECRET")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "transactions")


def kafka_common_config() -> dict:
    """Connection settings every Kafka client (producer + consumers) shares.
    SASL_SSL + PLAIN is how you authenticate to Confluent Cloud over the
    public internet - the standard, secure managed-Kafka pattern."""
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "security.protocol": "SASL_SSL",
        "sasl.mechanisms": "PLAIN",
        "sasl.username": KAFKA_API_KEY,
        "sasl.password": KAFKA_API_SECRET,
    }


# ---- AWS ----
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BRONZE_BUCKET = os.getenv("S3_BRONZE_BUCKET", "")
DYNAMODB_LEDGER_TABLE = os.getenv("DYNAMODB_LEDGER_TABLE", "")

# ---- Azure ----
AZURE_STORAGE_ACCOUNT = os.getenv("AZURE_STORAGE_ACCOUNT", "")
AZURE_STORAGE_KEY = os.getenv("AZURE_STORAGE_KEY", "")
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT", "")
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "analytics")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "metrics")
