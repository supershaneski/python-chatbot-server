from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import socketserver
import os
import random

from google import genai
from google.genai import types


def load_env():
    """Load environment variables from .env file."""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

try:
    load_env()
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )
    model = "gemini-2.5-flash-lite"
    generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
    )
    gemini_mode = True
except (ImportError, KeyError, Exception) as e:
    print(f"Warning: Failed to initialize Gemini API: {e}. Using mock replies.")
    gemini_mode = None

# In-memory storage for messages
messages = []
message_id = 1

class SimpleRESTServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/':
            # Serve the HTML file
            try:
                with open('index.html', 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, 'HTML file not found')
        elif path == '/messages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
        else:
            self.send_error(404, 'Not found')

    def do_POST(self):
        if self.path == '/chat':
            global message_id
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                if 'text' not in data:
                    self.send_error(400, 'Text is required')
                    return
                
                user_message = {'id': message_id, 'role': 'user', 'parts': [{ 'text': data['text'] }]}
                messages.append(user_message)
                
                message_id += 1

                # Sample mock replies
                responses = ['I see', 'Okay', 'Could you tell me more?', 'Interesting', 'Thanks for sharing', 'Alright', 'Got it']
                
                if gemini_mode:
                    # Generate model reply
                    try:
                        contents = [{k: v for k, v in d.items() if k != 'id'} for d in messages]
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=contents
                        )
                        model_text = response.text
                    except Exception as e:
                        print(f"Warning: Gemini API call failed: {e}. Using mock reply.")
                        model_text = random.choice(responses)
                else:
                    # Mocking model reply
                    model_text = random.choice(responses)

                model_reply = {'id': message_id, 'role': 'model', 'parts': [{ 'text': model_text }]}
                messages.append(model_reply)
                
                message_id += 1
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(model_reply).encode())

            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
        else:
            self.send_error(404, 'Not found')
    
    def do_DELETE(self):
        if self.path == '/messages':
            global messages, message_id
            messages = []  # Clear all messages
            message_id = 1  # Reset message ID
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Chat history cleared'}).encode())
        else:
            self.send_error(404, 'Not found')

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

def run(server_class=HTTPServer, handler_class=SimpleRESTServer, port=8000):
    # Load .env file
    load_env()
    # Get port from environment variable, fallback to default
    port = int(os.environ.get('SERVER_PORT', port))

    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
    finally:
        print("Server stopped.")

if __name__ == '__main__':
    run()