import os
from typing import Any

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Export Kafka configuration variables
bootstrap = os.environ["ES_BOOTSTRAP"]
username = os.environ["ES_USERNAME"]
password = os.environ["ES_PASSWORD"]
topic = os.environ.get('ES_TOPIC', 'orders.v1')


def get_base_config() -> dict[str, Any]:
    """Returns the base Kafka configuration dictionary for SASL_SSL authentication."""
    return {
        "bootstrap.servers": bootstrap,
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": 'PLAIN',
        "sasl.username": username,
        "sasl.password": password,
    }
