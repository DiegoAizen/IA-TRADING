# backend/app/ai/ai_interface.py - VERSIÓN CORREGIDA
import json
import time
import aiohttp
from typing import Dict, Any
from ..core.logger import logger
from ..core.ai_config import AIProvider, ai_config 
from .prompt_templates import PromptTemplates

class AIInterface:
    
    def __init__(self):
        self.prompt_templates = PromptTemplates()
    
    async def analyze_market(self, symbol: str, user_id: int, market_data: Dict[str, Any], 
                       technical_indicators: Dict[str, Any], news: list,
                       ai_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analizar mercado - VERSIÓN CORREGIDA
        """
        try:
            start_time = time.time()
            
            logger.info(f"🤖 Preparando análisis para {symbol} con {ai_config.get('provider')}")
            
            if not market_data or not technical_indicators:
                logger.error(f"Datos insuficientes para {symbol}")
                return self._get_error_response("Datos de mercado insuficientes")
            
            news_context = news 
            
            # Seleccionar plantilla basada en tipo de análisis
            analysis_type = ai_config.get('analysis_type', 'comprehensive')
            logger.info(f"📝 Usando plantilla de análisis: {analysis_type}")
             
            logger.info(f"📰 Contexto de noticias recibido: {news_context.get('news_count', 0)} noticias, sentimiento: {news_context.get('overall_sentiment', 'neutral')}")
            
            if analysis_type == 'technical':
                prompt = self.prompt_templates.technical_analysis(
                    symbol, market_data, technical_indicators, news_context
                )
            elif analysis_type == 'sentiment':
                prompt = self.prompt_templates.market_sentiment(
                    symbol, [], {}, news_context
                )
            else:
                prompt = self.prompt_templates.comprehensive_analysis(
                     symbol, 
                    market_data, 
                    technical_indicators, 
                    ai_config.get('risk_profile', 'moderate'), 
                    news_context
                )
            
            # Llamar a la IA
            provider_name = ai_config.get('provider', 'deepseek')
            provider = AIProvider(provider_name)
            api_key = ai_config.get('api_key')
            model = ai_config.get('model', 'deepseek-chat')
            
            if not api_key:
                logger.error("No API key configurada")
                return self._get_error_response("API key no configurada")
            
            logger.info(f"🔗 Llamando a {provider_name} para análisis de {symbol}")
            logger.info(f"🔍 DEBUG Enviando prompt a IA (longitud: {len(prompt)} caracteres)")
            
            # Llamar al proveedor de IA
            response = await self._call_ai_provider(provider, api_key, model, prompt, ai_config)
            
            logger.info(f"🔍 DEBUG Respuesta IA CRUDA: {response}")
            
            # Procesar respuesta
            processing_time = time.time() - start_time
            
            result = self._parse_ai_response(response, provider)
            result['processing_time'] = round(processing_time, 2)
            result['tokens_used'] = response.get('usage', {}).get('total_tokens', 0) if isinstance(response, dict) else 0
            
            logger.info(f"🔍 DEBUG Respuesta IA PARSEADA: {result}")
            logger.info(f"✅ Análisis IA completado - {symbol} | Señal: {result.get('signal')} | Confianza: {result.get('confidence')}%")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error en análisis IA para {symbol}: {str(e)}", exc_info=True)
            return self._get_error_response(f"Error en análisis: {str(e)}")

    async def _call_ai_provider(self, provider: AIProvider, api_key: str, model: str, 
                              prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar al proveedor de IA específico"""
        try:
            logger.debug(f"Enviando prompt a {provider} (longitud: {len(prompt)} caracteres)")
            
            if provider == AIProvider.DEEPSEEK:
                return await self._call_deepseek(api_key, model, prompt, config)
            elif provider == AIProvider.OPENAI:
                return await self._call_openai(api_key, model, prompt, config)
            elif provider == AIProvider.GEMINI:
                return await self._call_gemini(api_key, model, prompt, config)
            elif provider == AIProvider.CLAUDE:
                return await self._call_claude(api_key, model, prompt, config)
            else:
                raise ValueError(f"Proveedor no soportado: {provider}")
                
        except Exception as e:
            logger.error(f"Error llamando a {provider}: {str(e)}")
            raise
    
    async def _call_deepseek(self, api_key: str, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a DeepSeek API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', ai_config.MAX_TOKENS),
            "temperature": config.get('temperature', ai_config.TEMPERATURE),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(ai_config.DEEPSEEK_API_URL, headers=headers, json=data, timeout=60) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    raise Exception(f"API error {response.status}: {error_text}")
    
    async def _call_openai(self, api_key: str, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.get('max_tokens', ai_config.MAX_TOKENS),
            "temperature": config.get('temperature', ai_config.TEMPERATURE),
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(ai_config.OPENAI_API_URL, headers=headers, json=data, timeout=60) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"OpenAI API error {response.status}: {error_text}")
                    raise Exception(f"API error {response.status}: {error_text}")
    
    async def _call_gemini(self, api_key: str, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a Gemini API"""
        url = f"{ai_config.GEMINI_API_URL}?key={api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "maxOutputTokens": config.get('max_tokens', ai_config.MAX_TOKENS),
                "temperature": config.get('temperature', ai_config.TEMPERATURE)
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, timeout=60) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API error {response.status}: {error_text}")
                    raise Exception(f"API error {response.status}: {error_text}")
    
    async def _call_claude(self, api_key: str, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Llamar a Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": config.get('max_tokens', ai_config.MAX_TOKENS),
            "temperature": config.get('temperature', ai_config.TEMPERATURE),
            "messages": [{"role": "user", "content": prompt}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(ai_config.CLAUDE_API_URL, headers=headers, json=data, timeout=60) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logger.error(f"Claude API error {response.status}: {error_text}")
                    raise Exception(f"API error {response.status}: {error_text}")
    
    def _parse_ai_response(self, response: Dict[str, Any], provider: AIProvider) -> Dict[str, Any]:
        """Parsear respuesta de la IA a formato estándar"""
        try:
            # Extraer texto de respuesta basado en proveedor
            if provider == AIProvider.DEEPSEEK or provider == AIProvider.OPENAI:
                content = response['choices'][0]['message']['content']
            elif provider == AIProvider.GEMINI:
                content = response['candidates'][0]['content']['parts'][0]['text']
            elif provider == AIProvider.CLAUDE:
                content = response['content'][0]['text']
            else:
                content = str(response)
            
            logger.debug(f"Respuesta IA cruda: {content[:200]}...")
            
            # Intentar parsear JSON
            try:
                # Limpiar contenido
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                parsed = json.loads(content)
                logger.info(f"✅ Respuesta IA parseada correctamente: {parsed.get('signal')} con {parsed.get('confidence')}% confianza")
                return parsed
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON inválido en respuesta IA, usando fallback: {e}")
                return self._extract_signal_from_text(content)
                
        except Exception as e:
            logger.error(f"Error parseando respuesta IA: {str(e)}")
            return self._get_error_response("Error parseando respuesta de IA")
    
    def _extract_signal_from_text(self, text: str) -> Dict[str, Any]:
        """Extraer señal de texto libre (fallback)"""
        text_lower = text.lower()
        
        if 'buy' in text_lower and 'sell' not in text_lower:
            signal = "BUY"
            confidence = 70.0
        elif 'sell' in text_lower and 'buy' not in text_lower:
            signal = "SELL" 
            confidence = 70.0
        else:
            signal = "HOLD"
            confidence = 50.0
        
        return {
            "signal": signal,
            "confidence": confidence,
            "reasoning": f"Señal extraída de texto: {text[:200]}...",
            "parsed_from_text": True
        }
    
    def _get_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Respuesta de error estándar"""
        return {
            "signal": "HOLD",
            "confidence": 0.0,
            "reasoning": error_msg,
            "error": True,
            "processing_time": 0.0,
            "tokens_used": 0
        }

# Instancia global
ai_interface = AIInterface()