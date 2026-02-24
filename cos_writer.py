import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

import ibm_boto3
from ibm_botocore.client import Config
from ibm_botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables required:
# - COS_API_KEY: IBM Cloud API key
# - COS_INSTANCE_CRN: Cloud Object Storage instance CRN
# - COS_ENDPOINT: Regional endpoint (e.g., s3.us-south.cloud-object-storage.appdomain.cloud)
# - COS_BUCKET: Target bucket name


def _client():
    """
    Create IBM Cloud Object Storage client.

    GIVEN environment variables with COS credentials
    WHEN _client() is called
    THEN returns configured boto3 S3 client

    Raises:
        KeyError: If required environment variables are missing
    """
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id=os.environ["COS_API_KEY"],
        ibm_service_instance_id=os.environ["COS_INSTANCE_CRN"],
        config=Config(signature_version="oauth"),
        endpoint_url=os.environ["COS_ENDPOINT"],
    )


def write_order_json(order: dict, key: Optional[str] = None) -> str:
    """
    Write order as JSON to IBM Cloud Object Storage.

    GIVEN an order dictionary
    WHEN write_order_json is called
    THEN writes JSON to COS and returns the object key

    Uses Hive-style partitioning: orders/dt=YYYY-MM-DD/orderId=<id>.json
    This enables efficient date-based queries in analytics tools.

    Args:
        order: Order dictionary to write
        key: Optional custom object key. If None, generates key with date partition.

    Returns:
        Object key where the order was written

    Raises:
        KeyError: If required environment variables are missing
        ClientError: If COS write operation fails
    """
    bucket = os.environ["COS_BUCKET"]

    if key is None:
        # Generate Hive-style partitioned key
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        order_id = order.get("id", str(uuid.uuid4()))
        key = f"orders/dt={dt}/orderId={order_id}.json"

    # Compact JSON encoding (no whitespace)
    body = json.dumps(order, separators=(",", ":")).encode("utf-8")

    try:
        s3 = _client()
        s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
        logger.info(f"Successfully wrote order to COS: {key}")
        return key

    except ClientError as e:
        logger.error(f"Failed to write to COS: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error writing to COS: {e}")
        raise


def write_batch(orders: list[dict], prefix: Optional[str] = None) -> list[str]:
    """
    Write multiple orders to COS efficiently.

    GIVEN a list of order dictionaries
    WHEN write_batch is called
    THEN writes all orders and returns list of keys

    Args:
        orders: List of order dictionaries
        prefix: Optional prefix for all keys (e.g., "orders/batch-123/")

    Returns:
        List of object keys where orders were written
    """
    keys = []
    for order in orders:
        if prefix:
            order_id = order.get("id", str(uuid.uuid4()))
            key = f"{prefix}{order_id}.json"
        else:
            key = None

        try:
            written_key = write_order_json(order, key)
            keys.append(written_key)
        except Exception as e:
            logger.error(f"Failed to write order {order.get('id')}: {e}")
            # Continue with remaining orders

    return keys
