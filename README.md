python-sample-server
=====

A sample HTTP server using python.

## Endpoints

- `POST /chat`: Send message
- `GET /messages`: List all messages
- `DELETE /messages`: Delete all messages (reset chat)

## Web Interface

A simple web interface is available at `http://localhost:8000/`:
- Type a message and click **Send** or press Enter to send a message to the chatbot.
- View the conversation history in the chat window.
- Click **Reset Chat** to clear the conversation history.

> [!NOTE] 
> You can also use your actual IP address instead of `localhost`.
> This is useful if you want to load the web interface using remote devices (i.e. smartphone, tablet) connected to your WIFI/LAN.

## Setup

Clone repository

```sh
git clone <your-repo-url>

cb projectname
```

Setup virtual environment

```sh
python3 -m venv venv
```

> [!NOTE] 
> For all python commands, you can use `python` instead of `python3`.

Enter the virtual environment

```sh
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

Install dependencies

```sh
pip install -r requirements.txt
```

Now, to run the server

```sh
python3 server.py
```

To exit the virtual environment

```sh
deactivate
```
