# python-sample-server

A sample HTTP server using Python, serving as a chatbot backend with a web interface.

## Endpoints

- `POST /chat`: Send a user message and get a mock model reply.
  - Example: `curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello"}' http://localhost:8000/chat`
- `GET /messages`: Retrieve the full conversation history.
  - Example: `curl http://localhost:8000/messages`
- `DELETE /messages`: Delete all messages to reset the chat.
  - Example: `curl -X DELETE http://localhost:8000/messages`

> [!NOTE] 
> You can run the `GET /messages` endpoint directly in your browser.
> - Type this in the address bar: `http://localhost:8000/messages`.

## Web Interface

A simple web interface is available at `http://localhost:8000/`:
- Type a message and click **Send** or press Enter to send a message to the chatbot.
- View the conversation history in the chat window.
- Click **Reset Chat** to clear the conversation history.

> [!NOTE]
> You can use your actual IP address instead of `localhost` to access the web interface from remote devices (e.g., smartphone, tablet) on the same Wi-Fi/LAN. To find your IP address:
> - Linux/macOS: Run `ifconfig` or `ip addr`.
> - Windows: Run `ipconfig` in Command Prompt.
> Ensure port 8000 is open in your firewall settings.

## Setup

Clone repository:

```sh
git clone <your-repo-url>

cb projectname
```

Setup virtual environment (optional, works with any Python 3 version):

```sh
python3 -m venv venv
```

> [!NOTE] 
> For all python commands, you can use `python` instead of `python3` depending on your system.

Enter the virtual environment:

```sh
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

Install dependencies

```sh
pip install -r requirements.txt
```

Copy the `.env.example` file to `.env`:

```sh
cp .env.example .env  # Linux/macOS

copy .env.example .env  # Windows
```

(Optional) Edit .env to set a custom port (e.g., SERVER_PORT=8080).

Example `.env`:

```
SERVER_PORT=8080
```

The server defaults to port 8000 if no .env file or SERVER_PORT is set.

If you use a custom port, access the web interface at http://localhost:<port> (e.g., http://localhost:8080).


Now, to run the server

```sh
python3 server.py
```

To stop the server, press `Ctrl+C` in the terminal.

To exit the virtual environment

```sh
deactivate
```

