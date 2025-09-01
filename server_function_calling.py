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

# Define function declarations for the model

# Function with 2 arguments
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

# Function without argument
trivia_function = {
    "name": "get_cat_trivia",
    "description": "Returns a random cat trivia fact.",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}

# Function with optional argument (use default)
quiz_function = {
    "name": "get_quiz",
    "description": "Returns a quiz question. If no topic is provided, defaults to 'random'.",
    "parameters": {
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "description": "The quiz topic. Defaults to 'history' if not provided.",
                "enum": ["history", "science"],
            },
        },
        "required": [],
    },
}

# get_weather api handler 
def get_weather(args):
    """
    This is a mock function that returns random weather data.
    """
    print(f"Calling the mock weather API for {args['location']} on {args['date']}")
    # Generate a random temperature
    temperature = random.randint(15, 35) # degrees Celsius
    # Choose a random weather condition from a list
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy", "Windy"]
    condition = random.choice(conditions)
    # Return the randomized data
    return {
        "location": args["location"], 
        "date": args["date"], 
        "temperature": f"{temperature}°C",
        "condition": condition
    }

# get_cat_trivia api handler
def get_cat_trivia(args):
    """
    Returns a random trivia question and answer from a predefined list.
    """
    trivia_list = [
        {
            "question": "What is the term for a group of cats?",
            "answer": "A clowder"
        },
        {
            "question": "Which breed of cat is known for having no tail?",
            "answer": "Manx"
        },
        {
            "question": "What is the name of the cat in the Harry Potter series who belongs to Argus Filch?",
            "answer": "Mrs. Norris"
        },
        {
            "question": "What is the primary source of energy for a cat’s diet?",
            "answer": "Protein (cats are obligate carnivores)"
        },
        {
            "question": "Which ancient civilization revered cats and often mummified them?",
            "answer": "Ancient Egypt"
        },
        {
            "question": "What is the name of the famous cartoon cat who constantly chases Jerry the mouse?",
            "answer": "Tom"
        }
    ]
    # Use random.choice() to select one dictionary from the list
    random_trivia = random.choice(trivia_list)
    # Return the selected trivia
    return random_trivia

# get_quiz api handler
def get_quiz(args):
    """
    Returns a random trivia question and answer based on the specified topic.
    """
    history_trivia = [
        {
            "question": "Who was the first president of the United States?",
            "answer": "George Washington"
        },
        {
            "question": "In which year did Christopher Columbus first sail to the Americas?",
            "answer": "1492"
        },
        {
            "question": "What ancient wonder, located in Egypt, is the only one of the Seven Wonders of the Ancient World still standing?",
            "answer": "The Great Pyramid of Giza"
        },
        {
            "question": "In which year did the United States declare its independence?",
            "answer": "1776"
        },
        {
            "question": "Who was the first emperor of Rome?",
            "answer": "Augustus"
        },
        {
            "question": "The Great Wall of China was built to protect against which invaders?",
            "answer": "The Mongols"
        }
    ]

    science_trivia = [
        {
            "question": "What gas do plants absorb from the air to perform photosynthesis?",
            "answer": "Carbon dioxide"
        },
        {
            "question": "What is the name of the closest planet to the Sun?",
            "answer": "Mercury"
        },
        {
            "question": "What is the primary source of energy for Earth’s climate system?",
            "answer": "The Sun"
        },
        {
            "question": "What is the largest organ in the human body?",
            "answer": "The skin"
        },
        {
            "question": "What is the chemical symbol for gold?",
            "answer": "Au"
        },
        {
            "question": "What force keeps planets in orbit around the sun?",
            "answer": "Gravity"
        }
    ]

    # Use a dictionary to map topic names to their trivia lists
    quiz_topics = {
        "history": history_trivia,
        "science": science_trivia
    }

    # Get the topic from the arguments dictionary
    # topic = args.get("topic", "history") # defaulting to a general topic if not found
    topic = args.get("topic")
    
    # Check if the topic exists and select a random quiz
    if topic in quiz_topics:
        selected_quiz = random.choice(quiz_topics[topic])
        return selected_quiz
    else:
        return {"error": f"Topic '{topic}' not found. Please choose from history or science."}

# Dispatcher calls the function needed
def run_api_tool(name, args):
    """
    A generic function handler that dispatches calls based on the function name.
    """
    # Create a dictionary to map function names (strings) to function objects
    tool_map = {
        "get_weather": get_weather,
        "get_cat_trivia": get_cat_trivia,
        "get_quiz": get_quiz,
        # Add other functions here as you implement them
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
        tools = types.Tool(function_declarations=[weather_function, trivia_function, quiz_function]) # Add tools here
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
