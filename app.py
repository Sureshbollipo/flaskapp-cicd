# This is app code -
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! CI/CD Pipeline Working! <br/> <h1>Fisrt demo to Sindhu </h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
