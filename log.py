import logging
import os
from rich.logging import RichHandler

# Get environment, default to 'production' if not set
ENV = os.getenv("ENV", "production")

# Set log level based on environment
if ENV == "development":
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    handlers=[RichHandler(rich_tracebacks=True)],
    format="%(message)s",  # Simplified format for production
)
logger = logging.getLogger(__name__)
