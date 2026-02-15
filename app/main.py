from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "AI-Driven Self-Healing CI/CD Platform",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "flask-app"
    })

@app.route('/api/add/<int:a>/<int:b>')
def api_add(a, b):
    result = add(a, b)
    return jsonify({
        "operation": "add",
        "inputs": [a, b],
        "result": result
    })

@app.route('/api/subtract/<int:a>/<int:b>')
def api_subtract(a, b):
    result = subtract(a, b)
    return jsonify({
        "operation": "subtract",
        "inputs": [a, b],
        "result": result
    })

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract two numbers"""
    return a - b

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
