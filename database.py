# database.py
print("Loading database module...")

try:
    from pymongo import MongoClient
    print("✓ PyMongo imported successfully")
except ImportError as e:
    print(f"✗ Error importing PyMongo: {e}")
    print("Please install pymongo: pip install pymongo")
    exit(1)

import uuid
from datetime import datetime

# Global MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["trade_agent_db"]
    traders_collection = db["traders"]
    users_collection = db["users"]
    print("✓ MongoDB connection established")
except Exception as e:
    print(f"Warning: MongoDB connection failed: {e}")
    print("Make sure MongoDB is running on localhost:27017")

def store_user_data(user_data, trade_data):
    """Store user registration data and trade history"""
    print(f"Storing user data for: {user_data['username']}")
    print(f"Trade data type: {type(trade_data)}")
    print(f"Trade data length: {len(trade_data) if hasattr(trade_data, '__len__') else 'N/A'}")
    
    if not isinstance(trade_data, list):
        raise ValueError(f"Expected list, got {type(trade_data)}")
    
    trader_id = str(uuid.uuid4())
    
    # Transform trade data to match the desired schema
    trade_history = []
    for i, trade in enumerate(trade_data):
        print(f"Processing trade {i+1}: {type(trade)}")
        
        if not isinstance(trade, dict):
            raise ValueError(f"Trade {i+1} is not a dictionary: {type(trade)}")
        
        # Handle both CSV and JSON field names
        transformed_trade = {
            "trade_id": trade.get("trade_id"),
            "asset": trade.get("asset"),
            "action": trade.get("action"),
            "price": trade.get("price"),
            "volume": trade.get("volume"),
            "trade_value": trade.get("trade_value"),
            "date": trade.get("trade_date"),  
            "outcome": trade.get("trade_outcome"),  
            "tags": trade.get("tags", []),
            "trade_duration": trade.get("trade_duration"),
            "capital_used": trade.get("capital_used"),
            "stop_loss": trade.get("stop_loss"),
            "take_profit": trade.get("take_profit"),
            "entry_reason": trade.get("entry_reason"),
            "exit_reason": trade.get("exit_reason"),
            "market_condition": trade.get("market_condition"),
            "indicator_signals_used": trade.get("indicator_signals_used"),
            "news_or_sentiment_reference": trade.get("news_or_sentiment_reference"),
            "trading_platform": trade.get("trading_platform"),
            "trade_type": trade.get("trade_type"),
            "time_of_trade": trade.get("time_of_trade"),
            "day_of_week": trade.get("day_of_week")
        }
        trade_history.append(transformed_trade)
    
    trader_document = {
        "trader_id": trader_id,
        "username": user_data["username"],
        "trade_history": trade_history,
        "user_responses": {
            "primary_strategy": user_data["primary_strategy"],
            "loss_reaction": user_data["loss_reaction"],
            "risk_tolerance": user_data["risk_tolerance"]
        },
        "created_at": datetime.now()
    }
    
    try:
        # Store user credentials separately
        users_collection.insert_one({
            "username": user_data["username"],
            "password": user_data["password"],
            "trader_id": trader_id
        })
        
        traders_collection.insert_one(trader_document)
        print(f"✓ User data stored successfully with trader_id: {trader_id}")
        return trader_id
    except Exception as e:
        print(f"✗ Error storing user data: {e}")
        raise

def authenticate_user(username, password):
    """Authenticate user and return trader data"""
    print(f"Authenticating user: {username}")
    try:
        user = users_collection.find_one({
            "username": username,
            "password": password
        })
        if user:
            print(f"✓ User authenticated: {username}")
        else:
            print(f"✗ Authentication failed for: {username}")
        return user
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        return None

def store_derived_metrics(trader_id, metrics):
    """Store calculated derived metrics"""
    print(f"Storing derived metrics for trader: {trader_id}")
    try:
        traders_collection.update_one(
            {"trader_id": trader_id},
            {"$set": {"derived_metrics": metrics}}
        )
        print("✓ Derived metrics stored successfully")
    except Exception as e:
        print(f"✗ Error storing derived metrics: {e}")
        raise

def store_behavioral_profile(trader_id, profile):
    """Store behavioral analysis profile"""
    print(f"Storing behavioral profile for trader: {trader_id}")
    try:
        traders_collection.update_one(
            {"trader_id": trader_id},
            {"$set": {"behavioral_profile": profile}}
        )
        print("✓ Behavioral profile stored successfully")
    except Exception as e:
        print(f"✗ Error storing behavioral profile: {e}")
        raise

def get_trader_profile(trader_id):
    """Retrieve complete trader profile"""
    print(f"Retrieving trader profile: {trader_id}")
    try:
        trader = traders_collection.find_one({"trader_id": trader_id})
        if trader:
            print("✓ Trader profile retrieved successfully")
        else:
            print("✗ Trader profile not found")
        return trader
    except Exception as e:
        print(f"✗ Error retrieving trader profile: {e}")
        return None

def get_trade_history(trader_id):
    """Get trader's trade history"""
    trader = traders_collection.find_one({"trader_id": trader_id})
    return trader.get("trade_history", []) if trader else []

def get_trader_stats(trader_id):
    """Get trader statistics"""
    trader = traders_collection.find_one({"trader_id": trader_id})
    if not trader:
        return None
    
    trades = trader.get("trade_history", [])
    if not trades:
        return None
    
    total_trades = len(trades)
    profitable_trades = len([t for t in trades if t["outcome"] == "Profit"])
    win_rate = profitable_trades / total_trades if total_trades > 0 else 0
    
    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profitable_trades": profitable_trades,
        "loss_trades": total_trades - profitable_trades
    }

print("✓ Database module loaded successfully")