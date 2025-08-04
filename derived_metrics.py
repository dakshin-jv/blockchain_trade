# derived_metrics.py
print("Loading derived_metrics module...")

from collections import Counter
import statistics
from datetime import datetime

def calculate_metrics(trade_data):
    """Calculate derived metrics from raw trade data"""
    print(f"Calculating metrics for {len(trade_data)} trades")
    
    if not trade_data:
        return {}
    
    # Basic calculations
    total_trades = len(trade_data)
    profitable_trades = len([t for t in trade_data if t.get("trade_outcome") == "Profit"])
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    # Asset analysis
    assets = [t.get("asset") for t in trade_data if t.get("asset")]
    asset_counts = Counter(assets)
    preferred_tokens = list(asset_counts.keys())[:3]  # Top 3 traded assets
    
    # Trading style analysis
    entry_reasons = [t.get("entry_reason") for t in trade_data if t.get("entry_reason")]
    common_strategies = list(Counter(entry_reasons).keys())[:3]
    
    # Risk analysis
    trade_values = [float(t.get("trade_value", 0)) for t in trade_data if t.get("trade_value")]
    avg_trade_size = statistics.mean(trade_values) if trade_values else 0
    max_trade_size = max(trade_values) if trade_values else 0
    
    # Time analysis
    durations = [int(t.get("trade_duration", 0)) for t in trade_data if t.get("trade_duration")]
    avg_holding_time = statistics.mean(durations) if durations else 0
    
    # Determine holding period category
    if avg_holding_time < 1:
        holding_period = "Intraday"
    elif avg_holding_time < 7:
        holding_period = "Swing"
    else:
        holding_period = "Long-term"
    
    # Market condition analysis
    market_conditions = [t.get("market_condition") for t in trade_data if t.get("market_condition")]
    bullish_trades = len([c for c in market_conditions if c == "Bullish"])
    market_sentiment_alignment = bullish_trades / len(market_conditions) if market_conditions else 0
    
    # Risk appetite based on stop loss usage
    stop_loss_trades = len([t for t in trade_data if t.get("stop_loss")])
    risk_management_score = stop_loss_trades / total_trades if total_trades > 0 else 0
    
    if risk_management_score > 0.7:
        risk_appetite = "Low"
    elif risk_management_score > 0.4:
        risk_appetite = "Medium"
    else:
        risk_appetite = "High"
    
    # Portfolio diversification
    unique_assets = len(set(assets))
    if unique_assets < 3:
        portfolio_diversification = "Concentrated"
    elif unique_assets < 8:
        portfolio_diversification = "Moderate"
    else:
        portfolio_diversification = "Broad"
    
    # Technical indicator usage
    indicators = [t.get("indicator_signals_used") for t in trade_data if t.get("indicator_signals_used")]
    technical_indicator_usage = len([i for i in indicators if i and i != "None"]) / total_trades if total_trades > 0 else 0
    
    # News sensitivity
    news_trades = len([t for t in trade_data if t.get("news_or_sentiment_reference") and t.get("news_or_sentiment_reference") != "None"])
    news_sensitivity = news_trades / total_trades if total_trades > 0 else 0
    
    metrics = {
        "win_rate": round(win_rate, 3),
        "average_trade_return": 0,  # Would need P&L data to calculate
        "max_drawdown": 0,  # Would need sequential P&L data
        "avg_holding_time": round(avg_holding_time, 2),
        "trade_frequency": total_trades,  # Per dataset period
        "preferred_tokens": preferred_tokens,
        "common_strategies": common_strategies,
        "portfolio_diversification": portfolio_diversification,
        "risk_appetite": risk_appetite,
        "holding_period": holding_period,
        "market_sentiment_alignment": round(market_sentiment_alignment, 3),
        "technical_indicator_usage": round(technical_indicator_usage, 3),
        "news_sensitivity": round(news_sensitivity, 3),
        "avg_trade_size": round(avg_trade_size, 2),
        "max_trade_size": round(max_trade_size, 2)
    }
    
    print(f"✓ Calculated metrics: Win rate {win_rate:.1%}, Risk appetite: {risk_appetite}")
    return metrics

def calculate_behavioral_scores(metrics, user_responses):
    """Calculate behavioral scores for personality analysis"""
    print("Calculating behavioral scores...")
    
    # Strategy consistency score (based on common strategies diversity)
    strategy_diversity = len(metrics.get("common_strategies", []))
    strategy_consistency_score = max(0, 1 - (strategy_diversity - 1) * 0.2)
    
    # Behavioral volatility score (based on risk patterns)
    risk_appetite = metrics.get("risk_appetite", "Medium")
    risk_scores = {"Low": 0.2, "Medium": 0.5, "High": 0.8}
    behavioral_volatility_score = risk_scores.get(risk_appetite, 0.5)
    
    # Trend follower score (based on market sentiment alignment)
    trend_follower_score = metrics.get("market_sentiment_alignment", 0.5)
    
    # Contrarian score (inverse of trend following)
    contrarian_score = 1 - trend_follower_score
    
    # Confidence bias score (based on user responses and win rate)
    win_rate = metrics.get("win_rate", 0)
    confidence_bias_score = min(1.0, win_rate * 1.2)  # Higher win rate = more confidence
    
    # Adaptability score (based on strategy diversity and technical usage)
    tech_usage = metrics.get("technical_indicator_usage", 0)
    adaptability_score = (strategy_diversity * 0.3 + tech_usage * 0.7) / 2
    
    scores = {
        "strategy_consistency_score": round(strategy_consistency_score, 3),
        "behavioral_volatility_score": round(behavioral_volatility_score, 3),
        "adaptability_score": round(adaptability_score, 3),
        "confidence_bias_score": round(confidence_bias_score, 3),
        "trend_follower_score": round(trend_follower_score, 3),
        "contrarian_score": round(contrarian_score, 3)
    }
    
    print("✓ Behavioral scores calculated")
    return scores

print("✓ Derived_metrics module loaded successfully")