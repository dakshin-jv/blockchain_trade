# 🤖 Conversational Trade Agent

A sophisticated AI-powered trading assistant that analyzes your trading history and creates a personalized trader personality for natural conversations about your trading decisions, strategies, and market insights.

## 🌟 Features

### **🧠 Intelligent Trader Personality**
- **Behavioral Analysis** - Creates unique trader profiles based on your trading history
- **Personalized Responses** - AI responds as if it's you, referencing your actual trades
- **Real-time Streaming** - See responses generate word-by-word for natural conversations
- **Smart Fallbacks** - Works even when LLM is unavailable with rule-based responses

### **📊 Trading Analytics**
- **Derived Metrics** - Calculates win rate, risk appetite, preferred tokens, and more
- **Pattern Recognition** - Identifies your trading style (Technical, Momentum, Value, Sentiment)
- **Behavioral Scoring** - Analyzes confidence bias, trend following, and adaptability
- **Trade Context** - References specific trades when answering questions

### **💬 Interactive Chat Interface**
- **Natural Conversations** - Ask about strategies, past trades, or market decisions
- **Streaming Responses** - Real-time word-by-word response generation
- **Trader Voice** - AI speaks in first person as your trading persona
- **Trade References** - Mentions actual trades and outcomes in responses


## 📁 Project Structure

```
conversational-trade-agent/
├── main.py                 # FastAPI application with web interface
├── database.py            # MongoDB operations and data storage
├── derived_metrics.py     # Trading metrics calculation
├── behavioral.py          # Trader personality analysis
├── chat.py               # LLM integration and response generation
├── requirements.txt      # Python dependencies
├── sample_trades.csv     # Sample trading data for testing
├── README.md            # This file
```

## 💾 Data Format

### **CSV Upload Requirements**

Your CSV file should contain these columns (minimum required: asset, action, price, trade_outcome):

```csv
user_id,trade_id,asset,action,price,volume,trade_value,trade_date,trade_outcome,tags,trade_duration,capital_used,stop_loss,take_profit,entry_reason,exit_reason,market_condition,indicator_signals_used,news_or_sentiment_reference,trading_platform,trade_type,time_of_trade,day_of_week
```

### **Sample Data**
See `user-001.csv` for a complete example with realistic trading data.

## 🎯 Usage Guide

### **1. Register New User**
- Upload your trading data as CSV
- Answer personality questions
- System analyzes your trading patterns

### **2. Chat with Your Agent**
Ask questions like:
- *"What's my trading strategy?"*
- *"Why did I buy DOGE?"*
- *"How do I handle losses?"*
- *"Tell me about my recent trades"*
- *"What tokens do I prefer?"*

### **3. Get Personalized Responses**
The agent responds in first person, referencing your actual trades and behavioral patterns.

## 🔧 Technical Architecture

### **Agentic AI Framework**
- **Database Agent** - Handles MongoDB operations
- **Derived Metrics Agent** - Calculates trading statistics
- **Behavioral Agent** - Analyzes trader personality
- **Chat Agent** - Generates conversational responses

### **Technologies Used**
- **Backend**: FastAPI, Python
- **Database**: MongoDB
- **AI/LLM**: Ollama with DeepSeek-R1:8b
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Streaming**: Server-Sent Events (SSE)

### **Key Features**
- **Real-time Streaming** - Word-by-word response generation
- **Behavioral Analysis** - Comprehensive trader profiling
- **Fallback Systems** - Works even when LLM is down
- **CSV Processing** - Flexible data import

## 📊 Generated Metrics

The system calculates various trading metrics:

### **Performance Metrics**
- Win rate and trade frequency
- Average holding time
- Risk appetite classification
- Portfolio diversification

### **Behavioral Features**
- Trading style (Technical/Momentum/Value/Sentiment)
- Response to losses and profits
- Market sentiment alignment
- Technical indicator usage

### **Personality Scores**
- Strategy consistency
- Behavioral volatility
- Adaptability score
- Confidence bias
- Trend following vs contrarian tendencies

## 🛠️ Configuration

### **Environment Variables** (Optional)
```bash
MONGODB_URL=mongodb://localhost:27017/
OLLAMA_URL=http://localhost:11434/api/generate
MODEL_NAME=deepseek-r1:8b
```

### **Model Parameters**
```python
{
    "temperature": 0.1,      # Low for focused responses
    "max_tokens": 200,       # Response length limit
    "think": True            # Enable reasoning mode
}
```

## 🔄 API Endpoints

- `GET /` - Landing page
- `GET /new_user` - Registration form
- `GET /login` - Login form
- `POST /register` - Process new user registration
- `POST /authenticate` - User authentication
- `GET /chat/{trader_id}` - Chat interface
- `POST /chat/{trader_id}/message` - Streaming chat endpoint
