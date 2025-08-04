# test_server.py - Minimal test to check if FastAPI works
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

print("Creating minimal FastAPI test server...")

app = FastAPI()

@app.get("/")
def read_root():
    print("Root endpoint accessed!")
    return {"message": "Hello World", "status": "Server is working!"}

@app.get("/test", response_class=HTMLResponse)
def test_page():
    print("Test page accessed!")
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>FastAPI Test Server is Working!</h1>
        <p>If you can see this, the server is running correctly.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    print("Starting test server on http://localhost:8001")
    print("Try opening: http://localhost:8001")
    print("Or try: http://localhost:8001/test")
    print("Press CTRL+C to stop the server")
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")