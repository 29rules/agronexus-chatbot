import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from rag import load_knowledge_base, create_chain, ask

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow React frontend to call this API

# Load knowledge base and create chain once at startup
print("🚀 Starting Agronexus Chatbot API...")
vector_store = load_knowledge_base()
chain = create_chain(vector_store)
print("✅ Ready!")

# Store chat history per session (simple in-memory for now)
chat_sessions = {}


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "bot": "AgroBot"})


@app.route("/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint.
    Expects: { "message": "...", "session_id": "..." }
    Returns: { "answer": "...", "session_id": "..." }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data or "message" not in data:
            return jsonify({"error": "message is required"}), 400

        message = data["message"].strip()
        session_id = data.get("session_id", "default")

        if not message:
            return jsonify({"error": "message cannot be empty"}), 400

        # Get or create chat history for this session
        history = chat_sessions.get(session_id, [])

        # Get answer from RAG chain
        answer = ask(chain, message, history)

        # Update history (keep last 10 exchanges)
        history.append(("human", message))
        history.append(("ai", answer))
        chat_sessions[session_id] = history[-20:]

        return jsonify({
            "answer": answer,
            "session_id": session_id
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, port=port)