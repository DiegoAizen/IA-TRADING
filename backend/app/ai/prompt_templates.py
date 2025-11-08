# backend/app/ai/prompt_templates.py - CORREGIR
from typing import Dict, Any

class PromptTemplates:
    
    @staticmethod
    def technical_analysis(symbol: str, market_data: Dict[str, Any], indicators: Dict[str, Any], news_context: Dict[str, Any] = None) -> str:
        """Plantilla para análisis técnico CON NOTICIAS INTEGRADAS - CORREGIDA"""
        
        # Sección de noticias
        news_section = ""
        if news_context and news_context.get("has_news", False):
            news_section = f"""
CONTEXTO DE NOTICIAS FUNDAMENTALES:
{news_context.get('market_context', 'No hay contexto de noticias disponible.')}

SENTIMIENTO GENERAL DEL MERCADO: {news_context.get('overall_sentiment', 'neutral').upper()}
NOTICIAS CONSIDERADAS: {news_context.get('news_count', 0)}
NOTICIAS DE ALTO IMPACTO: {news_context.get('high_impact_count', 0)}
"""
        else:
            news_section = "CONTEXTO FUNDAMENTAL: No hay noticias recientes relevantes disponibles."
        
        return f"""
Eres un experto analista de trading algorítmico. Analiza el mercado y proporciona una señal de trading EJECUTABLE integrando análisis técnico y contexto fundamental.

INFORMACIÓN DEL MERCADO - {symbol}:
- Precio Actual (Bid): {market_data.get('bid', 'N/A')}
- Precio Actual (Ask): {market_data.get('ask', 'N/A')} 
- Spread: {market_data.get('spread', 'N/A')} pips
- Tendencia: {market_data.get('trend', 'N/A')}
- Volatilidad: {market_data.get('volatility', 'N/A')}
- Alto Reciente: {market_data.get('high', 'N/A')}
- Bajo Reciente: {market_data.get('low', 'N/A')}

INDICADORES TÉCNICOS:
- RSI: {indicators.get('rsi', 'N/A')} (Sobrecompra >70, Sobreventa <30)
- MACD: {indicators.get('macd', 'N/A')}
- Media Móvil 20: {indicators.get('ma_20', 'N/A')}
- Media Móvil 50: {indicators.get('ma_50', 'N/A')}
- Soporte Inmediato: {indicators.get('support', 'N/A')}
- Resistencia Inmediata: {indicators.get('resistance', 'N/A')}
- Bollinger Upper: {indicators.get('bollinger_upper', 'N/A')}
- Bollinger Lower: {indicators.get('bollinger_lower', 'N/A')}

{news_section}

INSTRUCCIONES CRÍTICAS:
1. COMBINA análisis técnico con contexto fundamental de noticias
2. Si hay noticias de ALTO IMPACTO, dales mayor peso en tu análisis
3. SI la señal es BUY o SELL, DEBES proporcionar niveles específicos de stop loss y take profit
4. Los stops deben basarse en niveles técnicos REALES considerando la volatilidad del contexto de noticias
5. Ratio riesgo/beneficio mínimo 1:1.5
6. Ajusta la confianza según la CONVERGENCIA entre señales técnicas y contexto fundamental

RESPONDE EXCLUSIVAMENTE EN FORMATO JSON:
{{
    "signal": "BUY|SELL|HOLD",
    "confidence": 0.0-100.0,
    "reasoning": "Explicación que combine análisis técnico y contexto de noticias",
    "stop_loss": "precio_absoluto",
    "take_profit": "precio_absoluto",
    "risk_level": "LOW|MEDIUM|HIGH",
    "timeframe": "M5|M15|H1|H4",
    "price_target": "precio_objetivo",
    "news_influence": "POSITIVE|NEGATIVE|NEUTRAL|MIXED"
}}
"""

    @staticmethod
    def market_sentiment(symbol: str, news: list, social_sentiment: Dict[str, Any], news_context: Dict[str, Any] = None) -> str:
        """Plantilla para análisis de sentimiento MEJORADA con noticias"""
        
        news_content = ""
        if news_context and news_context.get("has_news", False):
            news_content = news_context.get('market_context', '')
        else:
            news_content = chr(10).join([f"- {item}" for item in news]) if news else "No hay noticias disponibles"
        
        return f"""
Analiza el sentimiento del mercado para {symbol} basado PRINCIPALMENTE en noticias fundamentales y proporciona parámetros ejecutables.

CONTEXTO DE NOTICIAS Y MERCADO:
{news_content}

RESPONDE EN FORMATO JSON:
{{
    "signal": "BUY|SELL|HOLD",
    "confidence": 0.0-100.0,
    "reasoning": "Análisis de sentimiento basado en noticias fundamentales",
    "stop_loss": "precio_o_nivel",
    "take_profit": "precio_o_nivel", 
    "sentiment_score": -10 to 10,
    "impact_level": "LOW|MEDIUM|HIGH|CRITICAL"
}}
"""

    @staticmethod
    def comprehensive_analysis(symbol: str, market_data: Dict, technical_indicators: Dict, risk_profile: str, news_context: Dict[str, Any] = None) -> str:
        """Plantilla para análisis completo MEJORADA con noticias integradas - CORREGIDA"""
        
        # Sección de noticias
        news_section = ""
        if news_context and news_context.get("has_news", False):
            news_section = f"""
CONTEXTO FUNDAMENTAL Y NOTICIAS:
{news_context.get('market_context', 'No hay contexto de noticias disponible.')}

SENTIMIENTO DE MERCADO: {news_context.get('overall_sentiment', 'neutral').upper()}
"""
        else:
            news_section = "CONTEXTO FUNDAMENTAL: Sin noticias recientes relevantes."
        
        return f"""
ANÁLISIS COMPLETO DE TRADING - {symbol}
Integra análisis TÉCNICO, gestión de RIESGO y contexto FUNDAMENTAL de noticias.

DATOS EN TIEMPO REAL:
- Precio Bid/Ask: {market_data.get('bid', 'N/A')}/{market_data.get('ask', 'N/A')}
- Tendencia: {market_data.get('trend', 'N/A')}
- Volatilidad: {market_data.get('volatility', 'N/A')}

ANÁLISIS TÉCNICO:
- RSI: {technical_indicators.get('rsi', 'N/A')}
- MACD: {technical_indicators.get('macd', 'N/A')} 
- Soporte: {technical_indicators.get('support', 'N/A')}
- Resistencia: {technical_indicators.get('resistance', 'N/A')}
- MA20/MA50: {technical_indicators.get('ma_20', 'N/A')}/{technical_indicators.get('ma_50', 'N/A')}

{news_section}

PERFIL DE RIESGO: {risk_profile}

INSTRUCCIONES EJECUTABLES:
1. COMBINA análisis técnico con contexto fundamental de noticias
2. Si hay CONFLICTO entre señales técnicas y noticias, prioriza la gestión de riesgo
3. Proporciona stops ESPECÍFICOS si hay señal
4. Ajusta confianza según CONVERGENCIA entre análisis técnico y fundamental

RESPONDE EN FORMATO JSON:
{{
    "signal": "BUY|SELL|HOLD",
    "confidence": 0.0-100.0,
    "reasoning": "Análisis integrado técnico-fundamental-riesgo",
    "stop_loss": "precio_absoluto",
    "take_profit": "precio_absoluto",
    "position_size": "SMALL|MEDIUM|LARGE",
    "risk_adjustment": "AGGRESSIVE|MODERATE|CONSERVATIVE",
    "timeframe": "M5|M15|H1|H4|D1"
}}
"""

    @staticmethod
    def reanalysis_template(symbol: str, position_data: Dict, market_data: Dict, indicators: Dict, news_context: Dict[str, Any] = None) -> str:
        """Plantilla específica para REANÁLISIS con noticias"""
        
        news_section = ""
        if news_context and news_context.get("has_news", False):
            news_section = f"""
CONTEXTO ACTUAL DE NOTICIAS:
{news_context.get('market_context', 'No hay noticias recientes.')}

SENTIMIENTO ACTUAL: {news_context.get('overall_sentiment', 'neutral').upper()}
"""
        else:
            news_section = "CONTEXTO ACTUAL: Sin noticias recientes relevantes."
        
        return f"""
REANÁLISIS DE POSICIÓN ABIERTA - {symbol}
Considera cambios en el CONTEXTO FUNDAMENTAL desde la apertura.

POSICIÓN ACTUAL:
- Tipo: {position_data.get('type', 'N/A')}
- Precio Entrada: {position_data.get('entry_price', 'N/A')}
- Profit Actual: {position_data.get('profit', 'N/A')}
- Stop Loss Actual: {position_data.get('sl', 'N/A')}
- Take Profit Actual: {position_data.get('tp', 'N/A')}

MERCADO ACTUAL:
- Precio: {market_data.get('bid', 'N/A')}
- Tendencia: {market_data.get('trend', 'N/A')}
- RSI: {indicators.get('rsi', 'N/A')}
- MACD: {indicators.get('macd', 'N/A')}

{news_section}

RESPONDE EN FORMATO JSON:
{{
    "action": "HOLD|CLOSE|ADJUST",
    "signal": "BUY|SELL|HOLD",
    "confidence": 0.0-100.0,
    "reasoning": "Análisis que considere cambios en contexto de noticias",
    "new_stop_loss": "nuevo_precio_sl",
    "new_take_profit": "nuevo_precio_tp",
    "adjustment_reason": "PROFIT_PROTECTION|RISK_MANAGEMENT|TREND_CHANGE|NEWS_IMPACT"
}}
"""