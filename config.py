import os
from dotenv import load_dotenv

load_dotenv()

# Application Configuration
APP_NAME = "Log File Data Access and Analysis API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "REST API for reading, parsing, and analyzing log files"

# Log Configuration
LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "50"))
MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", "200"))

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
