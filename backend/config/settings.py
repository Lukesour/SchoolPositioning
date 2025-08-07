import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Database Configuration
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_USER = os.getenv("DB_USER", "suan")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME_SOURCE = os.getenv("DB_NAME_SOURCE", "compass_cases_details")
    DB_NAME_TARGET = os.getenv("DB_NAME_TARGET", "compass_analytics_preprocessed")
    
    # SiliconFlow API Configuration
    SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
    SILICONFLOW_MODELS_PIPELINE = os.getenv("SILICONFLOW_MODELS_PIPELINE", "").split(",") if os.getenv("SILICONFLOW_MODELS_PIPELINE") else []
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def source_database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME_SOURCE}"
    
    @property
    def target_database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME_TARGET}"

settings = Settings()