from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import socketserver
import os
import random
from datetime import datetime

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

# Define function declaration for the model
weather_function = {
    "name": "get_weather",
    "description": "Gets the weather forecast for a given location and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. San Francisco",
            },
            "date": {
                "type": "string",
                "description": "The daye in YYYY-MM-DD format",
            },
        },
        "required": ["location", "date"],
    },
}

# get_weather api handler 
def get_weather(args):
    """
    This is a mock function for demonstration purposes.
    In a real application, you would implement the logic to
    call a weather API with the provided arguments.
    """
    print(f"Calling the weather API for {args['location']} on {args['date']}")
    return {"location": args["location"], "date": args["date"], "temperature": "15°C", "condition": "Cloudy"}

# Dispatcher calls the function needed
def run_api_tool(name, args):
    """
    A generic function handler that dispatches calls based on the function name.
    """
    # Create a dictionary to map function names (strings) to function objects
    tool_map = {
        "get_weather": get_weather,
        # Add other functions here as you implement them
        # "get_location": get_location,
        # "get_directions": get_directions,
    }
    # Check if the function name exists in our map
    if name in tool_map:
        # Get the function object and call it with the arguments
        function_to_call = tool_map[name]
        return function_to_call(args)
    else:
        # Handle the case where the tool is not found
        return {
            "error": "Tool not found",
            "tool_name": name,
            "arguments": args
        }

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
        # Get the current date and time
        current_datetime = datetime.now()

        # Create the system instruction with the current date that the model can use as reference.
        # It can now understand the date for today, tomorrow, yesterday, next Monday, etc.
        system_instruction_text = (
            f"""You are a friendly cat assistant. You communicate in a clear and concise way while keeping a light cat-like personality—curious, playful, and helpful. Today is {current_datetime}."""
        )

        print(system_instruction_text)

        client = genai.Client(api_key=api_key)
        tools = types.Tool(function_declarations=[weather_function])
        return {
            'client': client,
            'model': 'gemini-2.5-flash-lite',  # Consistent model name
            'config': types.GenerateContentConfig(
                temperature=0.5,
                tools=[tools],
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                system_instruction=[
                    types.Part.from_text(text=system_instruction_text)
                ],
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

                print(f"User message: {data['text']}")

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
                        
                        # Call the gemini response function to process the response
                        model_text = self.process_gemini_response(response, message_id, messages, gemini, call_count=0)

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
    
    # Process Gemini response to handle function calling.
    # It can process parallel function calls and subsequent function calls until only text is received.
    def process_gemini_response(self, response, message_id, messages, gemini, call_count=0):
        """
        Processes a Gemini API response and handles function calls or text replies.
        Includes a guard to prevent excessive function calls.
        Returns the final reply text.
        """

        print(f"call-count: {call_count}")

        # Define a maximum number of allowed calls
        MAX_CALLS = 7

        if call_count >= MAX_CALLS:
            raise Exception("Too many function calls. Conversation terminated.")
            
        if response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_call = part.function_call
                    print(f"Function to call: {function_call.name}")
                    print(f"Arguments: {function_call.args}")

                    # ... (your existing code to add tool_call to messages)
                    tool_call = {
                        'id': message_id, 
                        'role': 'model', 
                        'parts': [{
                            'functionCall': {
                                'name': function_call.name,
                                'args': function_call.args
                            }
                        }]
                    }
                    messages.append(tool_call)
                    message_id += 1

                    result = run_api_tool(function_call.name, function_call.args)

                    # ... (your existing code to add tool_response to messages)
                    tool_response = {
                        'id': message_id, 
                        'role': 'model', 
                        'parts': [{
                            'functionResponse': {
                                'name': function_call.name,
                                'response': result
                            }
                        }]
                    }

                    print(f"tool-response: {tool_response}")

                    messages.append(tool_response)
                    message_id += 1

                    # Now, send everything back to Gemini again
                    contents = [{k: v for k, v in d.items() if k != 'id'} for d in messages]
                    next_response = gemini['client'].models.generate_content(
                        model=gemini['model'],
                        contents=contents,
                        config=gemini['config']
                    )

                    # Increment the call counter for the next recursive call
                    return self.process_gemini_response(next_response, message_id, messages, gemini, call_count + 1)
                
                else:
                    # Handle text-only replies
                    print(f"part-text: {part.text}")
                    return part.text
        else:
            # Handle cases where there are no parts at all
            print(f"response-text: {response.text}")
            return response.text

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
        print(f'Starting server (with function calling) on http://localhost:{port}/...')
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
