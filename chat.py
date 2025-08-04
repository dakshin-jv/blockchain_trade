# chat.py
print("Loading chat module...")

import requests
import json
import random

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "deepseek-r1:8b"  # Changed from llama3.2

def generate_response(user_message, trader_data):
    """Generate conversational response using Ollama LLM (non-streaming fallback)"""
    print(f"Generating response for message: {user_message}")
    
    if not trader_data:
        return "I'm sorry, I couldn't find your trader profile. Please try registering again."
    
    # Extract relevant trader information
    profile = trader_data.get("behavioral_profile", {})
    profile_features = profile.get("profile_features", {})
    derived_features = profile.get("derived_features", {})
    trade_history = trader_data.get("trade_history", [])
    user_responses = trader_data.get("user_responses", {})
    
    # Create context for the LLM
    context = build_trader_context(profile_features, derived_features, trade_history, user_responses)
    
    # Create prompt
    prompt = create_prompt(user_message, context)
    
    try:
        # Call Ollama API (non-streaming for fallback)
        print("Attempting to call Ollama API...")
        response = call_ollama_non_streaming(prompt)
        print("✓ Ollama response received")
        return response
    except Exception as e:
        # Fallback to rule-based response
        print(f"Ollama failed ({e}), using fallback response")
        return fallback_response(user_message, profile_features, trade_history)

def build_trader_context(profile_features, derived_features, trade_history, user_responses):
    """Build context about the trader for the LLM"""
    
    # Sample some recent trades for context
    recent_trades = trade_history[-5:] if len(trade_history) > 5 else trade_history
    
    context = {
        "persona": derived_features.get("persona_label", "systematic trader"),
        "trading_style": profile_features.get("style", "Technical"),
        "risk_appetite": profile_features.get("risk_appetite", "Medium"),
        "win_rate": profile_features.get("win_rate", 0),
        "preferred_tokens": profile_features.get("preferred_tokens", []),
        "common_strategies": profile_features.get("common_strategies", []),
        "loss_reaction": user_responses.get("loss_reaction", ""),
        "recent_trades": recent_trades,
        "total_trades": len(trade_history),
        "holding_period": profile_features.get("holding_period", "Swing"),
        "volatility_preference": profile_features.get("volatility_preference", "stable")
    }
    
    return context

def create_prompt(user_message, context):
    """Create a detailed prompt for the LLM"""
    
    prompt = f"""
You are a cryptocurrency trader with a distinct personality. 
Respond to questions as if you are this trader talking about your own trading experience and decisions.

Your Profile:
- You are a {context['persona']}
- Your primary trading style is {context['trading_style']}
- Your risk appetite is {context['risk_appetite']}
- You prefer {context['holding_period'].lower()} trading
- Your win rate is {context['win_rate']:.1%}
- You have made {context['total_trades']} trades total
- Your preferred tokens are: {', '.join(context['preferred_tokens'][:3])}
- Your common strategies include: {', '.join(context['common_strategies'][:3])}

Your Trading Philosophy:
- When you face losses: {context['loss_reaction']}
- You prefer {context['volatility_preference']} market conditions

Some of your recent trades:
{format_recent_trades(context['recent_trades'])}

User Question: {user_message}

Respond as the trader in first person, being conversational and specific about your trading decisions and philosophy. 
Reference your actual trades when relevant. Keep the response under 150 words and maintain your trader personality.
"""

    return prompt

def format_recent_trades(trades):
    """Format recent trades for the prompt"""
    if not trades:
        return "No recent trades to reference."
    
    formatted = []
    for trade in trades:
        formatted.append(f"- {trade.get('action', 'Unknown')} {trade.get('asset', 'Unknown')} at ${trade.get('price', 0):.2f} - {trade.get('outcome', 'Unknown')}")
    
    return "\n".join(formatted)

def call_ollama_non_streaming(prompt):
    """Call Ollama API to generate non-streaming response"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "max_tokens": 200,
            "think": True
        }
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=None)
    
    if response.status_code == 200:
        result = response.json()
        return result.get("response", "I'm having trouble expressing my thoughts right now.")
    else:
        raise Exception(f"Ollama API error: {response.status_code}")

def fallback_response(user_message, profile_features, trade_history):
    """Fallback rule-based response when LLM is unavailable"""
    
    message_lower = user_message.lower()
    
    # Response templates based on common questions
    if any(word in message_lower for word in ["strategy", "approach", "method"]):
        style = profile_features.get("style", "Technical")
        strategies = profile_features.get("common_strategies", ["technical analysis"])
        return f"My primary trading style is {style}. I typically use {', '.join(strategies[:2])} as my main strategies. I've found this approach works well with my {profile_features.get('risk_appetite', 'medium').lower()} risk tolerance."
    
    elif any(word in message_lower for word in ["loss", "losses", "losing"]):
        loss_response = profile_features.get("response_to_loss", "analytical")
        return f"When I face losses, I tend to be {loss_response}. It's part of trading - I've learned that managing losses is just as important as capturing gains. My current win rate is {profile_features.get('win_rate', 0):.1%}."
    
    elif any(word in message_lower for word in ["token", "coin", "crypto", "prefer"]):
        preferred = profile_features.get("preferred_tokens", ["BTC", "ETH"])
        return f"I tend to focus on {', '.join(preferred[:3])} based on my trading history. These tokens align well with my {profile_features.get('style', 'technical').lower()} approach and {profile_features.get('volatility_preference', 'stable')} market preference."
    
    elif any(word in message_lower for word in ["buy", "bought", "purchase"]):
        recent_buys = [t for t in trade_history[-10:] if t.get("action") == "Buy"]
        if recent_buys:
            recent = recent_buys[-1]
            return f"One of my recent buys was {recent.get('asset')} at ${recent.get('price', 0):.2f}. I entered because of {recent.get('tags', ['market conditions'])[0]} - it turned out to be a {recent.get('outcome', 'learning experience').lower()}."
        return "I look for good entry points based on my technical analysis and market sentiment alignment."
    
    elif any(word in message_lower for word in ["sell", "sold", "exit"]):
        recent_sells = [t for t in trade_history[-10:] if t.get("action") == "Sell"]
        if recent_sells:
            recent = recent_sells[-1]
            return f"Recently sold {recent.get('asset')} at ${recent.get('price', 0):.2f}. My exit was driven by {recent.get('tags', ['profit taking'])[0]} - ended up being a {recent.get('outcome', 'neutral').lower()}."
        return "I typically exit positions based on my predetermined targets or when market conditions change."
    
    elif any(word in message_lower for word in ["risk", "risky", "safe"]):
        risk_appetite = profile_features.get("risk_appetite", "Medium")
        return f"I'd describe myself as having a {risk_appetite.lower()} risk appetite. I use {profile_features.get('portfolio_diversification', 'moderate').lower()} diversification and typically hold positions for {profile_features.get('holding_period', 'swing').lower()} periods."
    
    else:
        # Generic response
        persona = profile_features.get("persona_label", "systematic trader")
        return f"As a {persona}, I focus on consistent execution of my strategy. I've made {len(trade_history)} trades with a {profile_features.get('win_rate', 0):.1%} success rate. What specific aspect of my trading would you like to know more about?"

print("✓ Chat module loaded successfully")