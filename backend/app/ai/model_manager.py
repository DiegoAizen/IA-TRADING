# En ai/model_manager.py
# Cómo se interpreta la confianza (0-100%) en decisiones
# Cómo el nivel de riesgo afecta el tamaño de posición
# Validación de señales antes de ejecutar

import requests
import json
import time
from typing import Dict, Any, Optional
from enum import Enum
from ..core.logger import logger
from ..core.ai_config import AIProvider, ai_config

class ModelManager:
    def __init__(self):
        self.active_models = {}
    
    def validate_api_key(self, provider: AIProvider, api_key: str) -> bool:
        """Validar que la API key funciona"""
        try:
            test_prompt = "Responde con 'OK' si estás funcionando."
            
            if provider == AIProvider.DEEPSEEK:
                return self._test_deepseek(api_key, test_prompt)
            elif provider == AIProvider.OPENAI:
                return self._test_openai(api_key, test_prompt)
            elif provider == AIProvider.GEMINI:
                return self._test_gemini(api_key, test_prompt)
            elif provider == AIProvider.CLAUDE:
                return self._test_claude(api_key, test_prompt)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error validando API key para {provider}: {str(e)}")
            return False
    
    def _test_deepseek(self, api_key: str, prompt: str) -> bool:
        """Test DeepSeek API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        response = requests.post(ai_config.DEEPSEEK_API_URL, headers=headers, json=data, timeout=30)
        return response.status_code == 200
    
    def _test_openai(self, api_key: str, prompt: str) -> bool:
        """Test OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        response = requests.post(ai_config.OPENAI_API_URL, headers=headers, json=data, timeout=30)
        return response.status_code == 200
    
    def _test_gemini(self, api_key: str, prompt: str) -> bool:
        """Test Gemini API"""
        url = f"{ai_config.GEMINI_API_URL}?key={api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": 10,
                "temperature": 0.1
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        return response.status_code == 200
    
    def _test_claude(self, api_key: str, prompt: str) -> bool:
        """Test Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(ai_config.CLAUDE_API_URL, headers=headers, json=data, timeout=30)
        return response.status_code == 200

# Instancia global
model_manager = ModelManager()