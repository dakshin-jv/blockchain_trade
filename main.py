# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
import csv
import io
import uvicorn
import json
import requests
from database import store_user_data, authenticate_user, store_derived_metrics, store_behavioral_profile, get_trader_profile
from derived_metrics import calculate_metrics
from behavioral import analyze_behavior
from chat import generate_response, build_trader_context, create_prompt, fallback_response

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trade Agent</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .btn { padding: 15px 30px; margin: 10px; font-size: 18px; cursor: pointer; 
                   background: #007bff; color: white; border: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Conversational Trade Agent</h1>
        <p>Welcome! Are you a new or existing user?</p>
        <button class="btn" onclick="location.href='/new_user'">New User</button>
        <button class="btn" onclick="location.href='/login'">Existing User</button>
    </body>
    </html>
    """

@app.get("/new_user", response_class=HTMLResponse)
def new_user():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Register</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; max-width: 600px; margin: 0 auto; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            .btn { padding: 12px 24px; background: #007bff; color: white; border: none; 
                   border-radius: 5px; cursor: pointer; font-size: 16px; }
            .btn:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <h2>New User Registration</h2>
        <form action="/register" method="post" enctype="multipart/form-data">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            
            <div class="form-group">
                <label>Upload Trade Data (CSV file):</label>
                <input type="file" name="trade_file" accept=".csv" required>
            </div>
            
            <div class="form-group">
                <label>Primary Trading Strategy:</label>
                <select name="primary_strategy">
                    <option value="Technical">Technical</option>
                    <option value="Momentum">Momentum</option>
                    <option value="Value">Value</option>
                    <option value="Sentiment">Sentiment</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>How do you react to losses?</label>
                <textarea name="loss_reaction" rows="3" placeholder="Describe your typical response..."></textarea>
            </div>
            
            <div class="form-group">
                <label>Risk Tolerance:</label>
                <select name="risk_tolerance">
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Low">Low</option>
                </select>
            </div>
            
            <button type="submit" class="btn">Register</button>
        </form>
    </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
def login():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; max-width: 400px; margin: 0 auto; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
            .btn { padding: 12px 24px; background: #007bff; color: white; border: none; 
                   border-radius: 5px; cursor: pointer; font-size: 16px; }
        </style>
    </head>
    <body>
        <h2>Login</h2>
        <form action="/authenticate" method="post">
            <div class="form-group">
                <label>Username:</label>
                <input type="text" name="username" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </body>
    </html>
    """

@app.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    trade_file: UploadFile = File(...),
    primary_strategy: str = Form(...),
    loss_reaction: str = Form(...),
    risk_tolerance: str = Form(...)
):
    # Read and parse CSV file
    content = trade_file.file.read().decode('utf-8')
    csv_data = list(csv.DictReader(io.StringIO(content)))
    
    # Convert numeric fields
    for row in csv_data:
        for field in ['price', 'volume', 'trade_value']:
            if field in row:
                try:
                    row[field] = float(row[field])
                except:
                    row[field] = 0
        
        # Handle tags
        if 'tags' in row and row['tags']:
            row['tags'] = [tag.strip() for tag in row['tags'].split(',')]
        else:
            row['tags'] = []
    
    # Create user data
    user_data = {
        "username": username,
        "password": password,
        "primary_strategy": primary_strategy,
        "loss_reaction": loss_reaction,
        "risk_tolerance": risk_tolerance
    }
    
    # Process data through agents
    trader_id = store_user_data(user_data, csv_data)
    metrics = calculate_metrics(csv_data)
    store_derived_metrics(trader_id, metrics)
    profile = analyze_behavior(metrics, user_data)
    store_behavioral_profile(trader_id, profile)
    
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Success</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; }}
            .success {{ background: #d4edda; padding: 20px; border-radius: 5px; margin: 20px 0; }}
            .btn {{ padding: 12px 24px; background: #007bff; color: white; text-decoration: none; 
                   border-radius: 5px; display: inline-block; margin: 10px; }}
        </style>
    </head>
    <body>
        <div class="success">
            <h2>Registration Successful!</h2>
            <p>Processed {len(csv_data)} trades</p>
            <p>Trader ID: {trader_id}</p>
        </div>
        <a href="/chat/{trader_id}" class="btn">Start Chatting</a>
    </body>
    </html>
    """)

@app.post("/authenticate")
def auth(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if user:
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head><title>Welcome</title></head>
        <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
            <h2>Welcome back, {username}!</h2>
            <a href="/chat/{user['trader_id']}" style="padding: 12px 24px; background: #007bff; 
               color: white; text-decoration: none; border-radius: 5px;">Continue to Chat</a>
        </body>
        </html>
        """)
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/chat/{trader_id}", response_class=HTMLResponse)
def chat(trader_id: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trade Agent Chat</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .chat-box {{ height: 400px; border: 2px solid #ccc; padding: 15px; 
                        overflow-y: scroll; margin-bottom: 15px; border-radius: 10px; 
                        background: #f9f9f9; }}
            .input-area {{ display: flex; gap: 10px; }}
            input {{ flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 5px; }}
            button {{ padding: 12px 20px; background: #007bff; color: white; 
                     border: none; border-radius: 5px; cursor: pointer; }}
            .message {{ margin: 10px 0; padding: 12px; border-radius: 8px; }}
            .user {{ background: #007bff; color: white; text-align: right; }}
            .agent {{ background: #e9ecef; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>💬 Chat with Your Trade Agent</h2>
            <div id="chatBox" class="chat-box"></div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Ask about my trading strategy, past trades, preferences..." 
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <script>
            let currentMessageDiv = null;
            
            function sendMessage() {{
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                addMessage(message, 'user');
                input.value = '';
                
                // Create agent message div for streaming
                currentMessageDiv = createAgentMessage();
                
                // Start streaming
                startStreaming(message);
            }}
            
            function createAgentMessage() {{
                const box = document.getElementById('chatBox');
                const div = document.createElement('div');
                div.className = 'message agent';
                div.innerHTML = '<strong>🤖 Agent:</strong> <span class="content"></span>';
                box.appendChild(div);
                box.scrollTop = box.scrollHeight;
                return div.querySelector('.content');
            }}
            
            function startStreaming(message) {{
                fetch('/chat/{trader_id}/message', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{'message': message}})
                }})
                .then(response => {{
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    
                    function readStream() {{
                        return reader.read().then(function(result) {{
                            if (result.done) return;
                            
                            const chunk = decoder.decode(result.value, {{stream: true}});
                            const lines = chunk.split('\\n');
                            
                            for (let line of lines) {{
                                if (line.startsWith('data: ')) {{
                                    try {{
                                        const data = JSON.parse(line.slice(6));
                                        if (data.token) {{
                                            currentMessageDiv.textContent += data.token;
                                            document.getElementById('chatBox').scrollTop = document.getElementById('chatBox').scrollHeight;
                                        }}
                                        if (data.done) {{
                                            return; // Stream completed
                                        }}
                                    }} catch (e) {{
                                        // Ignore parsing errors
                                    }}
                                }}
                            }}
                            
                            return readStream();
                        }});
                    }}
                    
                    return readStream();
                }})
                .catch(error => {{
                    if (currentMessageDiv) {{
                        currentMessageDiv.textContent = 'Error: ' + error.message;
                    }}
                }});
            }}
            
            function addMessage(text, sender) {{
                const box = document.getElementById('chatBox');
                const div = document.createElement('div');
                div.className = `message ${{sender}}`;
                div.innerHTML = `<strong>${{sender === 'user' ? 'You' : '🤖 Agent'}}:</strong> ${{text}}`;
                box.appendChild(div);
                box.scrollTop = box.scrollHeight;
            }}
            
            addMessage("Hello! I'm your trading agent. Ask me about my strategy, trades, or decisions!", 'agent');
        </script>
    </body>
    </html>
    """

@app.post("/chat/{trader_id}/message")
def chat_message(trader_id: str, message: dict):
    """Handle streaming chat messages"""
    def generate_stream():
        try:
            trader_data = get_trader_profile(trader_id)
            user_message = message["message"]
            
            if not trader_data:
                yield f"data: {json.dumps({'token': 'Sorry, I could not find your trader profile.'})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
                return
            
            # Extract trader information
            profile = trader_data.get("behavioral_profile", {})
            profile_features = profile.get("profile_features", {})
            derived_features = profile.get("derived_features", {})
            trade_history = trader_data.get("trade_history", [])
            user_responses = trader_data.get("user_responses", {})
            
            # Build context and create prompt
            context = build_trader_context(profile_features, derived_features, trade_history, user_responses)
            prompt = create_prompt(user_message, context)
            
            # Try Ollama streaming
            try:
                # Ollama streaming request
                payload = {
                    "model": "deepseek-r1:8b",
                    "prompt": prompt,
                    "stream": True,
                    "think": True,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 200
                    }
                }
                
                response = requests.post(
                    "http://localhost:11434/api/generate", 
                    json=payload, 
                    stream=True
                )
                
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            try:
                                chunk = line.decode('utf-8')
                                data = json.loads(chunk)
                                if 'response' in data and data['response']:
                                    # Send each token/word
                                    yield f"data: {json.dumps({'token': data['response']})}\n\n"
                                if data.get('done', False):
                                    yield f"data: {json.dumps({'done': True})}\n\n"
                                    return
                            except:
                                continue
                else:
                    raise Exception("Ollama API error")
                    
            except Exception as e:
                # Fallback to rule-based response
                fallback_resp = fallback_response(user_message, profile_features, trade_history)
                
                # Simulate streaming for fallback response
                words = fallback_resp.split()
                for word in words:
                    yield f"data: {json.dumps({'token': word + ' '})}\n\n"
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
        except Exception as e:
            yield f"data: {json.dumps({'token': f'Error: {str(e)}'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

if __name__ == "__main__":
    port = 8000
    print(f"🚀 Starting Trade Agent on http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")