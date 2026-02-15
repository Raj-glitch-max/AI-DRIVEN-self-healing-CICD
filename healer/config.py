"""
Configuration management for the AI Healer
"""
import os
from pathlib import Path
from typing import Optional
import logging

class Config:
    """Configuration class for the AI Healer"""
    
    def __init__(self):
        self.load_env_file()
        self.validate_required_config()
        
    def load_env_file(self):
        """Load environment variables from .env file if it exists"""
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
    
    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4")
    
    @property
    def github_token(self) -> str:
        return os.getenv("GITHUB_TOKEN", "")
    
    @property
    def github_repository(self) -> str:
        return os.getenv("GITHUB_REPOSITORY", "")
    
    @property
    def github_base_branch(self) -> str:
        return os.getenv("GITHUB_BASE_BRANCH", "main")
    
    @property
    def max_retry_attempts(self) -> int:
        return int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    
    @property
    def healing_timeout(self) -> int:
        return int(os.getenv("HEALING_TIMEOUT", "300"))
    
    @property
    def branch_prefix(self) -> str:
        return os.getenv("BRANCH_PREFIX", "fix/ai-heal")
    
    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def log_file(self) -> str:
        return os.getenv("LOG_FILE", "healer.log")
    
    def validate_required_config(self):
        """Validate that required configuration is present"""
        required_vars = [
            ("OPENAI_API_KEY", self.openai_api_key),
            ("GITHUB_TOKEN", self.github_token),
            ("GITHUB_REPOSITORY", self.github_repository)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file or environment configuration."
            )
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

# Global config instance
config = Config()