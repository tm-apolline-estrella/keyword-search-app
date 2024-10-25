# Import standard library modules
import os
import re
from enum import Enum

# Import third-party library modules
from dotenv import load_dotenv

load_dotenv()

APIM_SUB_KEY = os.getenv("APIM_SUB_KEY")
APIM_END_POINT = os.getenv("APIM_END_POINT")

AZURITE_ACCOUNT_NAME = os.environ.get("AZURITE_ACCOUNT_NAME")
AZURITE_ACCOUNT_KEY = os.environ.get("AZURITE_ACCOUNT_KEY")
STORAGE_ACCOUNT_KEY = os.environ.get("STORAGE_ACCOUNT_KEY")
PROJECT_NAME = os.environ.get("PROJECT_NAME")
ENV = os.environ.get("ENV", "prod")

AZURE_SPEECH_SERVICE_KEY = os.environ.get("AZURE_SPEECH_SERVICE_KEY")
AZURE_SPEECH_SERVICE_REGION = os.environ.get("AZURE_SPEECH_SERVICE_REGION")

OPENAI_API_DEPLOYMENT_NAME = os.getenv("OPENAI_API_DEPLOYMENT_NAME")
OPENAI_API_TYPE = "azure"
OPENAI_API_VERSION = "2023-05-15"

# Number of tries to check avaibility for openai endpoint
# Since the APIM is not round robin, we need to randomly try to check availability
NUM_AVAIL_CHECK = 10

NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET")
NEXTAUTH_URL = os.getenv("NEXTAUTH_URL", "http://localhost:3000")

ROUTES = ["customer", "product", "spiel"]

MODEL_NAME_CHAT = OPENAI_API_DEPLOYMENT_NAME
MODEL_NAME_EMBEDDINGS = "text-embedding-ada-002"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

ACS_ADMIN_KEY = os.environ.get("ACS_ADMIN_KEY", "")
ACS_SERVICE_NAME = os.environ.get("ACS_SERVICE_NAME", "")

AD_TENANT_ID = os.environ.get("AD_TENANT_ID", "")
AD_CLIENT_ID = os.environ.get("AD_CLIENT_ID", "")
AD_CLIENT_SECRET = os.environ.get("AD_CLIENT_SECRET", "")

# Database connection parameters
DATABASE_URL = os.environ.get("DATABASE_URL")


def parse_database_url(db_url):
    # Regex pattern to capture the relevant database connection fields
    pattern = re.compile(
        r"sqlserver://(?P<server>[^:]+):?[^;]*;database=(?P<database>[^;]+);user=(?P<user>[^;]+);password=(?P<password>[^;]+);"
    )

    # Search for patterns in the URL with the regex
    match = pattern.search(db_url)

    # Extracting the details
    params = match.groupdict()
    return params


database_connection_params = parse_database_url(DATABASE_URL)

DATABASE_URL_SQLALCHEMY = f"mssql+pymssql://{database_connection_params['user']}:{database_connection_params['password']}@{database_connection_params['server']}/{database_connection_params['database']}?charset=utf8"

# Blob Storage Names
STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER_NAME = os.environ.get("STORAGE_CONTAINER_NAME")
SOURCE_CONTAINER_NAME = os.environ.get("SOURCE_CONTAINER_NAME")


class ModuleStoragePath(Enum):
    LIBRARIAN = "research/"
    RELATIONSHIP_MANAGER = "coach/"


class ModuleIndex(Enum):
    LIBRARIAN = "research-wilson-2"
    RELATIONSHIP_MANAGER = "coach"


MAX_RETRIES_JSON_ERROR = 5
