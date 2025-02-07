import logging
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
logger = logging.getLogger(__name__)
