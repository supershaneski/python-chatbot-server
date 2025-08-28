from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import socketserver

# In-memory storage for tasks
tasks = []
task_id = 1

class SimpleRESTServer(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == '/tasks':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(tasks).encode())
        elif path.startswith('/tasks/'):
            try:
                task_id = int(path.split('/')[-1])
                task = next((task for task in tasks if task['id'] == task_id), None)
                if task:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(task).encode())
                else:
                    self.send_error(404, 'Task not found')
            except ValueError:
                self.send_error(400, 'Invalid task ID')
        else:
            self.send_error(404, 'Not found')

    def do_POST(self):
        if self.path == '/tasks':
            global task_id
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                if 'title' not in data:
                    self.send_error(400, 'Title is required')
                    return
                task = {'id': task_id, 'title': data['title'], 'completed': False}
                tasks.append(task)
                task_id += 1
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(task).encode())
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
        else:
            self.send_error(404, 'Not found')

    def do_PUT(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/tasks/'):
            try:
                task_id = int(path.split('/')[-1])
                task = next((task for task in tasks if task['id'] == task_id), None)
                if not task:
                    self.send_error(404, 'Task not found')
                    return
                content_length = int(self.headers['Content-Length'])
                put_data = self.rfile.read(content_length)
                data = json.loads(put_data.decode())
                if 'title' in data:
                    task['title'] = data['title']
                if 'completed' in data:
                    task['completed'] = data['completed']
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(task).encode())
            except (ValueError, json.JSONDecodeError):
                self.send_error(400, 'Invalid request')
        else:
            self.send_error(404, 'Not found')

    def do_DELETE(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path.startswith('/tasks/'):
            try:
                task_id = int(path.split('/')[-1])
                global tasks
                task = next((task for task in tasks if task['id'] == task_id), None)
                if not task:
                    self.send_error(404, 'Task not found')
                    return
                tasks = [t for t in tasks if t['id'] != task_id]
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Task deleted'}).encode())
            except ValueError:
                self.send_error(400, 'Invalid task ID')
        else:
            self.send_error(404, 'Not found')

    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())

def run(server_class=HTTPServer, handler_class=SimpleRESTServer, port=8000):
    # Enable socket reuse to avoid "Address already in use" on restart
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