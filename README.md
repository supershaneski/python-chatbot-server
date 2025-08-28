python-sample-server
=====

A sample HTTP server using python.

# Endpoints

- `POST /tasks`: Create a task
- `GET /tasks`: List all tasks
- `GET /tasks/<id>`: Get a task by ID
- `PUT /tasks/<id>`: Update a task
- `DELETE /tasks/<id>`: Delete a task

# Setup

Clone repository

```sh
git clone https://github.com/supershaneski/python-sample-server.git

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
