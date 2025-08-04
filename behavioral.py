# behavioral.py
print("Loading behavioral module...")

from derived_metrics import calculate_behavioral_scores

def analyze_behavior(derived_metrics, user_responses):
    """Analyze trader behavior and create personality profile"""
    print("Analyzing trader behavior...")
    
    # Calculate behavioral scores
    behavioral_scores = calculate_behavioral_scores(derived_metrics, user_responses)
    
    # Determine dominant trading style
    style = determine_trading_style(derived_metrics, user_responses)
    
    # Generate persona label
    persona_label = generate_persona_label(derived_metrics, user_responses, behavioral_scores)
    
    # Analyze response patterns
    response_patterns = analyze_response_patterns(user_responses, derived_metrics)
    
    profile_features = {
        "style": style,
        "risk_appetite": derived_metrics.get("risk_appetite", "Medium"),
        "holding_period": derived_metrics.get("holding_period", "Swing"),
        "preferred_tokens": derived_metrics.get("preferred_tokens", []),
        "common_strategies": derived_metrics.get("common_strategies", []),
        "portfolio_diversification": derived_metrics.get("portfolio_diversification", "Moderate"),
        "capital_allocation_pattern": "Conservative",  
        "win_rate": derived_metrics.get("win_rate", 0),
        "average_trade_return": derived_metrics.get("average_trade_return", 0),
        "max_drawdown": derived_metrics.get("max_drawdown", 0),
        "avg_holding_time": derived_metrics.get("avg_holding_time", 0),
        "trade_frequency": derived_metrics.get("trade_frequency", 0),
        "active_hours": "Market Hours",  
        "market_sentiment_alignment": derived_metrics.get("market_sentiment_alignment", 0.5),
        "response_to_loss": response_patterns["loss_response"],
        "response_to_profit": response_patterns["profit_response"],
        "technical_indicator_usage": derived_metrics.get("technical_indicator_usage", 0),
        "volatility_preference": determine_volatility_preference(derived_metrics),
        "news_sensitivity": derived_metrics.get("news_sensitivity", 0),
        "influencer_dependency": response_patterns["influencer_dependency"],
        "journal_or_notes_presence": "No" 
    }
    
    derived_features = {
        "persona_label": persona_label,
        "strategy_consistency_score": behavioral_scores["strategy_consistency_score"],
        "behavioral_volatility_score": behavioral_scores["behavioral_volatility_score"],
        "adaptability_score": behavioral_scores["adaptability_score"],
        "confidence_bias_score": behavioral_scores["confidence_bias_score"],
        "trend_follower_score": behavioral_scores["trend_follower_score"],
        "contrarian_score": behavioral_scores["contrarian_score"]
    }
    
    profile = {
        "profile_features": profile_features,
        "derived_features": derived_features
    }
    
    print(f"✓ Behavioral analysis complete. Persona: {persona_label}")
    return profile

def determine_trading_style(metrics, user_responses):
    """Determine dominant trading style based on metrics and responses"""
    primary_strategy = user_responses.get("primary_strategy", "Technical")
    
    # Weight based on actual trading patterns
    news_sensitivity = metrics.get("news_sensitivity", 0)
    tech_usage = metrics.get("technical_indicator_usage", 0)
    market_alignment = metrics.get("market_sentiment_alignment", 0.5)
    
    if news_sensitivity > 0.3 or "sentiment" in primary_strategy.lower():
        return "Sentiment"
    elif tech_usage > 0.5 or "technical" in primary_strategy.lower():
        return "Technical"
    elif market_alignment > 0.7 or "momentum" in primary_strategy.lower():
        return "Momentum"
    else:
        return "Value"

def generate_persona_label(metrics, user_responses, behavioral_scores):
    """Generate a descriptive persona label"""
    risk = metrics.get("risk_appetite", "Medium").lower()
    style = determine_trading_style(metrics, user_responses).lower()
    
    # Add behavioral modifiers
    if behavioral_scores["trend_follower_score"] > 0.7:
        modifier = "trend-following"
    elif behavioral_scores["contrarian_score"] > 0.7:
        modifier = "contrarian"
    elif behavioral_scores["adaptability_score"] > 0.7:
        modifier = "adaptive"
    else:
        modifier = "systematic"
    
    return f"{risk}-risk {modifier} {style} trader"

def analyze_response_patterns(user_responses, metrics):
    """Analyze user response patterns for behavioral insights"""
    loss_reaction = user_responses.get("loss_reaction", "").lower()
    
    # Analyze loss response pattern
    if any(word in loss_reaction for word in ["cut", "stop", "exit", "careful"]):
        loss_response = "risk-averse"
    elif any(word in loss_reaction for word in ["double", "more", "revenge", "bigger"]):
        loss_response = "revenge trades"
    else:
        loss_response = "analytical"
    
    # Profit response based on risk appetite
    risk_appetite = metrics.get("risk_appetite", "Medium")
    if risk_appetite == "High":
        profit_response = "scaling up"
    elif risk_appetite == "Low":
        profit_response = "taking profits"
    else:
        profit_response = "steady approach"
    
    # Influencer dependency based on news sensitivity
    news_sensitivity = metrics.get("news_sensitivity", 0)
    influencer_dependency = "Yes" if news_sensitivity > 0.4 else "No"
    
    return {
        "loss_response": loss_response,
        "profit_response": profit_response,
        "influencer_dependency": influencer_dependency
    }

def determine_volatility_preference(metrics):
    """Determine volatility preference based on trading patterns"""
    risk_appetite = metrics.get("risk_appetite", "Medium")
    avg_holding_time = metrics.get("avg_holding_time", 0)
    
    if risk_appetite == "High" and avg_holding_time < 2:
        return "volatile"
    else:
        return "stable"

print("✓ Behavioral module loaded successfully")