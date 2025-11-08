from pydantic_settings import BaseSettings
from typing import Dict, List, Optional
from enum import Enum

class AIProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"

class AIConfig(BaseSettings):
    # Configuración por defecto
    DEFAULT_PROVIDER: AIProvider = AIProvider.DEEPSEEK
    
    # URLs de APIs
    DEEPSEEK_API_URL: str = "https://api.deepseek.com/v1/chat/completions"
    OPENAI_API_URL: str = "https://api.openai.com/v1/chat/completions"
    GEMINI_API_URL: str = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
    CLAUDE_API_URL: str = "https://api.anthropic.com/v1/messages"
    
    # Modelos disponibles por proveedor
    AVAILABLE_MODELS: Dict[AIProvider, List[str]] = {
        AIProvider.DEEPSEEK: ["deepseek-chat", "deepseek-coder"],
        AIProvider.OPENAI: ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
        AIProvider.GEMINI: ["gemini-pro", "gemini-pro-vision"],
        AIProvider.CLAUDE: ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    }
    
    # Configuración de prompts
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7

ai_config = AIConfig()