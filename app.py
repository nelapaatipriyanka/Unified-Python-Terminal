from flask import Flask, request, jsonify, render_template
from terminal import UnifiedTerminal
from flask_cors import CORS
import os  # <-- Added for Render port

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests
terminal = UnifiedTerminal()

# Serve frontend
@app.route('/')
def home():
    return render_template('index.html')

# Execute commands via POST
@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    cmd = data.get("command", "")
    output = terminal.execute(cmd)
    return jsonify({"output": output})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns PORT dynamically
    app.run(host="0.0.0.0", port=port, debug=True)
