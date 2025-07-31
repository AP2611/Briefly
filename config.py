import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Discord bot"""
    
    # Discord Bot Token
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Ollama Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'mistral')
    
    # Bot Configuration
    BOT_PREFIX = os.getenv('BOT_PREFIX', '!')
    
    # Summarization Settings
    MAX_MESSAGES_TO_SUMMARIZE = int(os.getenv('MAX_MESSAGES_TO_SUMMARIZE', '50'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))
    
    # Ollama Model Settings
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '500'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.3'))
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set"""
        required_vars = ['DISCORD_TOKEN']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 