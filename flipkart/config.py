import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for Flipkart Recommender application."""
    
    def __init__(self):
        # API Keys
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self.HF_TOKEN = os.getenv("HF_TOKEN")
        
        # Database Configuration
        self.ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")

        # Models
        self.EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"
        self.LLM_MODEL = "openai/gpt-oss-20b"

        # Data paths
        self.CSV_FILE_PATH = "data/flipkart_product_review.csv"
    
    def validate(self):
        """Validate that all required environment variables are set."""
        required_vars = [
            "GROQ_API_KEY",
            "HUGGINGFACEHUB_API_TOKEN",
            "HF_TOKEN",
            "ASTRA_DB_API_ENDPOINT",
            "ASTRA_DB_APPLICATION_TOKEN",
            "ASTRA_DB_KEYSPACE"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(self, var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        
        return True


# Singleton instance for easy importing
config = Config()