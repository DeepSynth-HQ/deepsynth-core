import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    POSTGRES_URL = os.getenv("POSTGRES_URL")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    BASE_URL = os.getenv("BASE_URL")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    ############################
    #     Auth Settings       #
    ############################
    @property
    def origins(self):
        return os.getenv("ALLOWED_ORIGINS", "*")

    X_CLIENT_ID = os.getenv("X_CLIENT_ID")
    X_CLIENT_SECRET = os.getenv("X_CLIENT_SECRET")
    X_REDIRECT_URI = os.getenv("X_REDIRECT_URI")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION = int(os.getenv("JWT_EXPIRATION", 86400))  # in seconds

    ############################
    #     Redis Settings      #
    ############################
    REDIS_URI = os.getenv("REDIS_URI")
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 60))
    RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 5))

    ############################
    #     File Settings       #
    ############################
    FILE_PREFIX = os.getenv("FILE_PREFIX", "deepsynth_")

    ############################
    #     Service Settings    #
    ############################
    SEARXNG_HOST = os.getenv("SEARXNG_HOST")
    SERVICE_ONCHAIN_BASE_URL = os.getenv("SERVICE_ONCHAIN_BASE_URL")
    WALLET_API_URL = os.getenv("WALLET_API_URL")

    #############################
    #     Prompt Engineering    #
    #############################
    DEEPSYNTH_INSTRUCTION_PROMPT = os.getenv("DEEP_SYNTH_INSTRUCTION_PROMPT")
    DEEPSYNTH_DESCRIPTION_PROMPT = os.getenv("DEEP_SYNTH_DESCRIPTION_PROMPT")
    DEEPSYNTH_SYSTEM_PROMPT = os.getenv("DEEP_SYNTH_SYSTEM_PROMPT")
    DEEPSYNTH_IMAGE_ANALYSIS_SYSTEM_PROMPT = os.getenv(
        "DEEP_SYNTH_IMAGE_ANALYSIS_SYSTEM_PROMPT"
    )
    #############################
    #     LLM Settings         #
    #############################
    ATOMA_BASE_URL = os.getenv("ATOMA_BASE_URL", "https://api.atoma.network/v1")
    ATOMA_API_KEY = os.getenv("ATOMA_API_KEY")
    ATOMA_LLAMA_3_3_70B_INSTRUCT = "meta-llama/Llama-3.3-70B-Instruct"
    ATOMA_DEEPSEEK_R1 = "deepseek-ai/DeepSeek-R1"

    #############################
    #     AWS Settings          #
    #############################
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")
    AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")


settings = Settings()
