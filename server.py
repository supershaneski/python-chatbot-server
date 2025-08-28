from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import socketserver

# In-memory storage for messages
messages = []
message_id = 1

class SimpleRESTServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/messages':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(messages).encode())
        elif path.startswith('/messages/'):
            try:
                message_id = int(path.split('/')[-1])
                message = next((message for message in messages if message['id'] == message_id), None)
                if message:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(message).encode())
                else:
                    self.send_error(404, 'Message not found')
            except ValueError:
                self.send_error(400, 'Invalid message ID')
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

                # Mocking model reply
                model_reply = {'id': message_id, 'role': 'model', 'parts': [{ 'text': 'Lorem ipsum dolor' }]}
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
    
    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

def run(server_class=HTTPServer, handler_class=SimpleRESTServer, port=8000):
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