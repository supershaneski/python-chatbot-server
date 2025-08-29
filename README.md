# python-sample-server

A sample HTTP server written in Python, serving as a chatbot backend with a simple web interface. It's powered by [Google’s Gemini API](https://ai.google.dev/gemini-api/docs) for generating responses. If no Gemini API key is provided, the server falls back to mock replies, allowing beginners to test and explore the code without needing an API key right away.

## Endpoints

- `POST /chat`: Send a user message to the chatbot.
  - Example: `curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello"}' http://localhost:8000/chat`
- `GET /messages`: Retrieve the full conversation history.
  - Example: `curl http://localhost:8000/messages`
- `DELETE /messages`: Delete all messages to reset the chat.
  - Example: `curl -X DELETE http://localhost:8000/messages`

> [!NOTE]  
> You can run the `GET /messages` endpoint directly in your browser by typing this in the address bar: `http://localhost:8000/messages`.

## Web Interface

A simple web interface is available at `http://localhost:8000/`:
- Type a message in the input field and click **Send** (or press Enter) to chat with the bot.
- View the full conversation history in the chat window.
- Click **Reset Chat** to clear the conversation history.

> [!NOTE]  
> To access the web interface from other devices (e.g., a smartphone or tablet) on the same Wi-Fi or local network, replace `localhost` with your computer's actual IP address (e.g., `http://192.168.1.100:8000/`).  
> To find your IP address:  
> - On Linux/macOS: Run `ifconfig` or `ip addr` in the terminal.  
> - On Windows: Run `ipconfig` in Command Prompt.  
> Make sure port 8000 is allowed through your firewall settings.

## Gemini API

This project uses Gemini's basic [text generation](https://ai.google.dev/gemini-api/docs/text-generation) feature. The SDK also supports [multi-turn conversations (chat)](https://ai.google.dev/gemini-api/docs/text-generation#multi-turn-conversations), but we're not using it here to keep things simple and focused on core concepts.

You can generate your own Gemini API key for free from [Google's AI Studio](https://aistudio.google.com/apikey). This key gives access to all available models, but it's [rate-limited](https://ai.google.dev/gemini-api/docs/rate-limits)—which should be plenty for testing and learning.  

If you don't have an API key (or prefer not to use one yet), the server will automatically use mock responses. This lets you see the chatbot in action and experiment with the code immediately.

## Setup

Clone the repository:

```sh
git clone <your-repo-url>

cd python-sample-server
```

Set up a virtual environment (optional but recommended to avoid conflicts with your system's Python; works with any Python 3 version):

```sh
python3 -m venv venv
```

> [!NOTE]  
> Depending on your system, you can use `python` instead of `python3` for all commands.

Activate the virtual environment:

```sh
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

Install dependencies (required only for the Gemini API integration):

```sh
pip install -r requirements.txt
```

Copy the example environment file:

```sh
cp .env.example .env  # Linux/macOS
# or
copy .env.example .env  # Windows
```

Edit the `.env` file with your details (use a text editor like Notepad or VS Code). Replace `your_actual_api_key_here` with your [Gemini API key](https://aistudio.google.com/apikey) if you have one—otherwise, leave it blank to use mock responses:

```txt
SERVER_PORT=8000
GEMINI_API_KEY=your_actual_api_key_here
```

Run the server:

```sh
python3 server.py
```

The server will start on `http://localhost:8000/`. To stop it, press `Ctrl+C` in the terminal.

To exit the virtual environment:

```sh
deactivate
```
