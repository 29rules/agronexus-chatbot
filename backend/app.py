import os
import threading
import pathlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

print("🚀 Starting Agronexus Chatbot API...")

# Global state
chain = None
ask = None
chat_sessions = {}
ready = False
init_error = None

def init_knowledge_base():
    global chain, ask, ready, init_error
    try:
        from rag import load_knowledge_base, build_knowledge_base, create_chain, ask as rag_ask
        if not pathlib.Path("faiss_index").exists():
            print("📚 No index found — building knowledge base...")
            vector_store = build_knowledge_base()
        else:
            print("📦 Loading existing knowledge base...")
            vector_store = load_knowledge_base()
        chain = create_chain(vector_store)
        ask = rag_ask
        ready = True
        print("✅ Ready!")
    except Exception as e:
        init_error = str(e)
        print(f"❌ Init error: {e}")

# Start knowledge base init in background so Flask can bind to port immediately
threading.Thread(target=init_knowledge_base, daemon=True).start()

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "bot": "AgroBot", "ready": ready})

@app.route("/chat", methods=["POST"])
def chat():
    if not ready:
        if init_error:
            return jsonify({"error": f"Initialization failed: {init_error}"}), 500
        return jsonify({"error": "Bot is still initializing, please try again in a moment."}), 503

    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "message is required"}), 400

        message = data["message"].strip()
        session_id = data.get("session_id", "default")

        if not message:
            return jsonify({"error": "message cannot be empty"}), 400

        history = chat_sessions.get(session_id, [])
        answer = ask(chain, message, history)
        history.append(("human", message))
        history.append(("ai", answer))
        chat_sessions[session_id] = history[-20:]
        return jsonify({"answer": answer, "session_id": session_id})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Something went wrong. Please try again."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # 0.0.0.0 is critical for Render — allows external traffic
    app.run(host="0.0.0.0", port=port, debug=False)
