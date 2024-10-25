# Import standard library modules
import urllib.parse
from datetime import datetime, timedelta, timezone
from functools import lru_cache

# Import third-party library modules
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas

# Import local modules
from src.components.coach_ai.settings import (
    PROJECT_NAME,
    SOURCE_CONTAINER_NAME,
    STORAGE_ACCOUNT_KEY,
    STORAGE_ACCOUNT_NAME,
    STORAGE_CONTAINER_NAME,
)

source_container_name = SOURCE_CONTAINER_NAME
storage_container_name = STORAGE_CONTAINER_NAME


def generate_blob_url(blob_name: str, container_name):
    html_blob_name = urllib.parse.quote(blob_name)
    sas_token = generate_blob_sas(
        account_name=STORAGE_ACCOUNT_NAME,
        account_key=STORAGE_ACCOUNT_KEY,
        container_name=container_name,
        blob_name=blob_name,
        permission=BlobSasPermissions(read=True),  # Adjust permissions as needed
        expiry=(
            datetime.now(timezone.utc)
            + timedelta(hours=1)  # SAS token will expire in 1 hour
        ),
    )
    blob_url_with_sas = f"https://{PROJECT_NAME}private.blob.core.windows.net/{container_name}/{html_blob_name}?{sas_token}"

    return blob_url_with_sas


@lru_cache()
def get_storage_clients():
    source_account_name = storage_account_name = STORAGE_ACCOUNT_NAME

    source_account_url = f"https://{source_account_name}.blob.core.windows.net"
    storage_account_url = f"https://{storage_account_name}.blob.core.windows.net"

    default_credential = STORAGE_ACCOUNT_KEY

    connection_string = f"DefaultEndpointsProtocol=https;AccountName={source_account_name};AccountKey={STORAGE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"

    source_blob_service_client = BlobServiceClient(
        source_account_url, credential=default_credential
    )
    storage_blob_service_client = BlobServiceClient(
        storage_account_url, credential=default_credential
    )

    source_container_client = source_blob_service_client.get_container_client(
        container=source_container_name
    )
    storage_container_client = storage_blob_service_client.get_container_client(
        container=storage_container_name
    )

    return (
        source_container_client,
        storage_container_client,
        source_container_name,
        storage_container_name,
        connection_string,
    )


(
    source_container_client,
    storage_container_client,
    source_container_name,
    storage_container_name,
    connection_string,
) = get_storage_clients()
