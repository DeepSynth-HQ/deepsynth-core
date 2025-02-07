from psycopg_pool import ConnectionPool
from config import settings

pool = ConnectionPool(settings.POSTGRES_URL)
