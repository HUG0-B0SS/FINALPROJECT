from flask import Flask
import random
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

@app.route('/')
def home():
    app.logger.info("Homepage visited")
    return "Welcome to Cool Tech Store!", 200

@app.route('/error')
def error():
    app.logger.error("An error occurred!")
    return "Something went wrong!", 500

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
