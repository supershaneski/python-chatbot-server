from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import socketserver
import os
import random

# Try to import Gemini API modules, but allow the server to run without them
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None
    print("Warning: Google Gemini API module not found. Using mock replies only.")

# In-memory storage for messages (shared across all users, not persistent)
# Note: For a production server, you'd want per-user sessions or a database
messages = []
message_id = 1

def load_env():
    """Load environment variables from .env file."""
    env_file = '.env'
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        try:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                        except ValueError:
                            print(f"Warning: Skipping malformed .env line: {line}")
        except Exception as e:
            print(f"Warning: Failed to read .env file: {e}")

# Initialize Gemini API client if available
def init_gemini():
    """Initialize the Gemini API client or return None if not available."""
    if genai is None:
        return None
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: No Gemini API key found in .env. Using mock replies.")
        return None
    try:
        client = genai.Client(api_key=api_key)
        return {
            'client': client,
            'model': 'gemini-2.5-flash',  # Consistent model name
            'config': types.GenerateContentConfig(
                temperature=0.5,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
        }
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini API: {e}. Using mock replies.")
        return None

# Load environment variables and initialize Gemini
load_env()  # Load .env before initializing Gemini as it contains the Gemini API key
gemini = init_gemini()

class SimpleRESTServer(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for the web interface and message history."""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/':
            # Serve the HTML file for the web interface
            try:
                with open('index.html', 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, 'index.html not found. Please create a basic HTML file.')
        elif path == '/messages':
            # Return the conversation history as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
        else:
            self.send_error(404, 'Not found')

    def do_POST(self):
        """Handle POST requests to send a user message and get a chatbot response."""
        if self.path == '/chat':
            global message_id
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                if 'text' not in data:
                    self.send_error(400, 'Missing "text" field in JSON')
                    return
                if not isinstance(data['text'], str) or not data['text'].strip():
                    self.send_error(400, 'Text must be a non-empty string')
                    return

                # Store user message
                user_message = {'id': message_id, 'role': 'user', 'parts': [{'text': data['text']}]}
                messages.append(user_message)
                message_id += 1

                # Generate a response
                if gemini:
                    try:
                        # Prepare message history for Gemini (exclude IDs)
                        contents = [{k: v for k, v in d.items() if k != 'id'} for d in messages]
                        response = gemini['client'].models.generate_content(
                            model=gemini['model'],
                            contents=contents,
                            config=gemini['config']
                        )
                        model_text = response.text
                    except Exception as e:
                        print(f"Warning: Gemini API call failed: {e}. Using mock reply.")
                        model_text = self.get_mock_reply(data['text'])
                else:
                    # Use mock reply if Gemini is unavailable
                    model_text = self.get_mock_reply(data['text'])

                # Store model response
                model_reply = {'id': message_id, 'role': 'model', 'parts': [{'text': model_text}]}
                messages.append(model_reply)
                message_id += 1

                # Send response back to client
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(model_reply).encode())

            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON format')
        else:
            self.send_error(404, 'Not found')

    def do_DELETE(self):
        """Handle DELETE requests to clear the conversation history."""
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
        """Send an error response with a JSON body."""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

    def get_mock_reply(self, user_text):
        """Generate a simple mock reply based on user input."""
        user_text = user_text.lower().strip()
        responses = {
            'hello': 'Hi there!',
            'how are you': 'Doing great, thanks for asking!',
            'bye': 'See you later!',
            'help': 'What do you need help with?',
        }
        # Return a context-aware response if the input contains a known keyword
        for key, reply in responses.items():
            if key in user_text:
                return reply
        # Fallback to a generic response
        return random.choice(['I see', 'Okay', 'Could you tell me more?', 'Interesting', 'Thanks for sharing'])

def run(server_class=HTTPServer, handler_class=SimpleRESTServer, port=8000):
    """Start the HTTP server."""
    # Get port from environment variable, fallback to default
    port = int(os.environ.get('SERVER_PORT', port))

    socketserver.TCPServer.allow_reuse_address = True
    server_address = ('', port)
    try:
        httpd = server_class(server_address, handler_class)
        print(f'Starting server on http://localhost:{port}/...')
        httpd.serve_forever()
    except OSError as e:
        print(f"Error: Could not start server on port {port}: {e}")
        print("Try a different port by setting SERVER_PORT in the .env file.")
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()
    finally:
        print("Server stopped.")

if __name__ == '__main__':
    run()
