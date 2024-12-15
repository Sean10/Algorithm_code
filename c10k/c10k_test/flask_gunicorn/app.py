from flask import Flask
import os
from gevent import monkey
monkey.patch_all()

app = Flask(__name__)

@app.route('/')
def hello():
    return f"Hello from process {os.getpid()}"

if __name__ == '__main__':
    app.run()