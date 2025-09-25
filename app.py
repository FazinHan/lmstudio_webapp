from flask import Flask, render_template, request, jsonify, session
import requests
import secrets # Used for generating a secure secret key

# --- Configuration ---
# 1. Make sure your LM Studio server is running.
# 2. Update this with your model's identifier from LM Studio.
MODEL_IDENTIFIER = "local-model"

# 3. (Optional) Set a custom system prompt.
SYSTEM_PROMPT = "You are a helpful and friendly AI assistant."

# --- API Details ---
LMSTUDIO_API_URL = "http://127.0.0.1:1234/v1/chat/completions"

# --- Flask App Initialization ---
app = Flask(__name__)
# A secret key is required for session management
app.secret_key = secrets.token_hex(16)

def get_model_response(conversation_history):
    """
    Sends the conversation history to the model and gets a response.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": MODEL_IDENTIFIER,
        "messages": conversation_history,
        "temperature": 0.7,
    }

    try:
        response = requests.post(LMSTUDIO_API_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            message = response_json['choices'][0]['message']
            return message['content'].strip()
        else:
            return "Error: Received an invalid response from the model."

    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the LM Studio server. Details: {e}"
    except KeyError:
        return "Error: Invalid response format from the API."

@app.route("/")
def index():
    """Renders the main chat page."""
    # Initialize chat history in the session if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles the chat message submission."""
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Retrieve history, add user message, and get AI response
    chat_history = session.get('chat_history', [])
    chat_history.append({"role": "user", "content": user_message})
    
    ai_response = get_model_response(chat_history)
    
    # Add AI response to history and save it back to the session
    chat_history.append({"role": "assistant", "content": ai_response})
    session['chat_history'] = chat_history

    return jsonify({"response": ai_response})

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

if __name__ == "__main__":
    # Replace the filenames with the ones mkcert created
    cert_file = '172.20.110.168+2.pem'
    key_file = '172.20.110.168+2-key.pem'

    app.run(host='0.0.0.0', debug=True, port=5000, ssl_context=(cert_file, key_file))