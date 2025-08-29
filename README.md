# python-chatbot-server

A Python-based **RESTful chatbot API server** powered by [Google’s Gemini API](https://ai.google.dev/gemini-api/docs). The API is designed for flexible integration with any frontend, including web apps built with React or mobile apps with Flutter.

To allow for quick testing and exploration, a simple web interface is provided. For developers who may not have an API key, the server includes a fallback to mock responses.

---

**RESTful Chatbot APIサーバー**。[Google Gemini API](https://ai.google.dev/gemini-api/docs) を活用した、Python 製のサーバーです。React の Web アプリや Flutter のモバイルアプリなど、あらゆるフロントエンドと連携できるよう設計されています。

テストとコードの確認をスムーズに行えるよう、シンプルな Web インターフェースも用意しました。API キーがなくても動作するよう、モック応答にフォールバックする機能も備わっています。

## Get Started

Follow these steps to run the chatbot server and try it out:

1. **Clone the repository**:
  ```sh
  git clone https://github.com/supershaneski/python-chatbot-server.git

  cd python-chatbot-server
  ```

2. **Set up a virtual environment** (optional but recommended):
  ```sh
  python3 -m venv venv
  ```
  Activate it:
  ```sh
  source venv/bin/activate  # Linux/macOS
  # or
  venv\Scripts\activate     # Windows
  ```
  > [!NOTE]  
  > Depending on your system, you can use `python` instead of `python3` for all commands.

3. **Install dependencies** (only needed for Gemini API integration):
  ```sh
  pip install -r requirements.txt
  ```
  > [!NOTE]  
  > The `requirements.txt` specifies `google-genai==1.32.0` to ensure compatibility with the [Gemini API](https://ai.google.dev/gemini-api/docs/quickstart#install-gemini-library). Other dependencies are installed automatically by `pip`.

4. **Set up the environment file**:
   Copy the example file:
   ```sh
   cp .env.example .env  # Linux/macOS
   # or
   copy .env.example .env  # Windows
   ```
   Edit `.env` with a text editor and add your Gemini API key (optional):
   ```txt
   SERVER_PORT=8000
   GEMINI_API_KEY=your_actual_api_key_here
   ```
   If you don’t have an API key, leave `GEMINI_API_KEY` blank to use mock responses.

5. **Run the server**:
   ```sh
   python3 server.py
   ```

6. **Try it out**:
   - Open your browser to `http://localhost:8000/` to use the web interface.
   - Type a message (e.g., “Hello”) and press Enter or click **Send**.
   - Click **Reset Chat** to clear the conversation.
   - Alternatively, use `curl` to test the API:
     ```sh
     curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello"}' http://localhost:8000/chat
     curl http://localhost:8000/messages
     ```

7. **Stop the server**:
   Press `Ctrl+C` in the terminal.

8. **Exit the virtual environment** (if used):
   ```sh
   deactivate
   ```

## Endpoints

- `POST /chat`: Send a user message to the chatbot.
  - Example: `curl -X POST -H "Content-Type: application/json" -d '{"text":"Hello"}' http://localhost:8000/chat`
- `GET /messages`: Retrieve the full conversation history.
  - Example: `curl http://localhost:8000/messages`
- `DELETE /messages`: Delete all messages to reset the chat.
  - Example: `curl -X DELETE http://localhost:8000/messages`

> [!TIP]  
> You can view the conversation history by typing `http://localhost:8000/messages` in your browser’s address bar.

This server acts as a RESTful API backend, allowing you to integrate the chatbot with various applications, such as web apps, mobile apps, or desktop clients. We provide a simple web interface at `http://localhost:8000/` to get you started, but you can build your own frontend using any technology that supports HTTP requests (e.g., JavaScript, React, Vue, Angular, Flutter, or React Native + Expo). 

For example:
- Create a web app with React or Vue to send messages to `/chat` and display responses from `/messages`.
- Build a mobile app with Flutter or React Native to interact with the chatbot.
- Use tools like Postman or `curl` to test the API directly.

To integrate with your app, make HTTP requests to the endpoints above using your preferred programming language or framework. The server handles the chatbot logic, so your app only needs to send and receive JSON data.

### Usage

Below are JavaScript examples showing how to interact with the API. These work in a browser (e.g., with a React or Vue app) or in Node.js (using a package like `node-fetch`). Use `http://localhost:8000` for local testing or replace it with your server’s IP address (e.g., `http://192.168.1.100:8000`) for access from other devices. See the [Web Interface](#web-interface) section for how to find your IP address.

```javascript
// Send a message to the chatbot
async function sendMessage(text) {
  try {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text })
    });
    if (!response.ok) {
      throw new Error(`Failed to send message: HTTP ${response.status}`);
    }
    const result = await response.json();
    console.log(result); // Model reply: { id: 2, role: "model", parts: [{ text: "..." }] }
  } catch (e) {
    console.error('Error sending message to /chat:', e);
  }
}

// Get all conversation messages
async function getAllMessages() {
  try {
    const response = await fetch('http://localhost:8000/messages');
    if (!response.ok) {
      throw new Error(`Failed to fetch messages: HTTP ${response.status}`);
    }
    const result = await response.json();
    console.log(result); // Array of messages: [{ id: 1, role: "user", parts: [...] }, ...]
  } catch (e) {
    console.error('Error fetching messages from /messages:', e);
  }
}

// Reset the chat history
async function resetChat() {
  try {
    const response = await fetch('http://localhost:8000/messages', {
      method: 'DELETE'
    });
    if (!response.ok) {
      throw new Error(`Failed to reset chat: HTTP ${response.status}`);
    }
    const result = await response.json();
    console.log(result); // { message: "Chat history cleared" }
  } catch (e) {
    console.error('Error resetting chat at /messages:', e);
  }
}
```

## Web Interface

A simple web interface is available at `http://localhost:8000/`:
- Type a message in the input field and click **Send** (or press Enter) to chat with the bot.
- View the conversation history in the chat window.
- Click **Reset Chat** to clear the conversation history.

> [!NOTE]  
> To access the web interface from other devices (e.g., a smartphone or tablet) on the same Wi-Fi or local network, replace `localhost` with your computer’s IP address (e.g., `http://192.168.1.100:8000/`).  
> To find your IP address:  
> - On Linux/macOS: Run `ifconfig` or `ip addr` in the terminal.  
> - On Windows: Run `ipconfig` in Command Prompt.  
> Ensure port 8000 is allowed through your firewall settings.

## Gemini API

This project uses Gemini's basic [text generation](https://ai.google.dev/gemini-api/docs/text-generation) feature. The SDK also supports [multi-turn conversations (chat)](https://ai.google.dev/gemini-api/docs/text-generation#multi-turn-conversations), but we're not using it here to keep things simple and focused on core concepts.

### API Key Setup
You can generate a free Gemini API key from [Google's AI Studio](https://aistudio.google.com/apikey). The key gives access to all available models with [rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), which are sufficient for testing. If you don’t have an API key, the server uses mock responses, so you can still try the chatbot.

### Configuration Details
The project uses the following configuration for the Gemini API:

- **Model**: `gemini-2.5-flash` (select from [available models](https://ai.google.dev/gemini-api/docs/models)).
- **Temperature**: `0.5` — Controls response randomness. A lower value (e.g., `0.1`) makes responses deterministic (same prompt, same reply), while a higher value adds variety, enhancing the chatbot's conversational feel.
- **Thinking Budget**: `0` — Disabled, as advanced reasoning isn't required for this use case.
- **System Instruction**: Defines the chatbot's personality as a "friendly cat assistant" with a clear, concise, and playful tone. Customize this to adjust the chatbot's behavior.

Example configuration in Python:

```python
client = genai.Client(api_key=api_key)
return {
    'client': client,
    'model': 'gemini-2.5-flash',
    'config': types.GenerateContentConfig(
        temperature=0.5,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        system_instruction=[
            types.Part.from_text(
                text="You are a friendly cat assistant. You communicate in a clear and concise way while keeping a light cat-like personality—curious, playful, and helpful."
            ),
        ],
}
```

## Thread Safety Note

The server stores messages in memory, shared across all users. This means multiple users accessing the server simultaneously may see each other’s messages. For a production server, you’d need per-user sessions or a database, but this is kept simple for learning purposes. To explore thread safety, you can look into Python’s `threading.Lock` or external storage solutions.

## Troubleshooting

- **Server won’t start**: If port 8000 is in use, edit `.env` to set a different `SERVER_PORT` (e.g., `SERVER_PORT=8001`) and restart.
- **No Gemini responses**: Ensure `GEMINI_API_KEY` is set in `.env`. If left blank, the server uses mock replies.
- **Web interface errors**: Check that `index.html` is in the same directory as `server.py` and that the server is running.

## License

This project is licensed under the MIT License. See the [LICENSE](/LICENSE) file for details.

