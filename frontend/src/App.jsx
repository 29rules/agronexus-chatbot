import { useState, useRef, useEffect } from "react"
import axios from "axios"
import "./App.css"

// Generate a random session ID for this browser session
const SESSION_ID = `session_${Date.now()}`
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000"

// Suggested questions shown at the start
const SUGGESTIONS = [
  "What spices do you sell?",
  "What's the minimum order for cumin?",
  "Do you ship to Canada?",
  "Can I get a sample?",
  "Are your products organic?",
]

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "👋 Hello! I'm AgroBot, your Agronexus Trading assistant. I can help you with product information, pricing, shipping, and orders. What would you like to know?",
    }
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async (text) => {
    const msg = text || input.trim()
    if (!msg || loading) return

    // Add user message to chat
    setMessages(prev => [...prev, { role: "user", text: msg }])
    setInput("")
    setLoading(true)

    try {
      const res = await axios.post(`${API_URL}/chat`, {
        message: msg,
        session_id: SESSION_ID,
      })
      setMessages(prev => [...prev, { role: "bot", text: res.data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: "bot",
        text: "Sorry, I'm having trouble connecting. Please try again or email info@agronexustrading.in",
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <div className="chat-container">

        {/* Header */}
        <div className="chat-header">
          <div className="header-left">
            <div className="avatar">🌿</div>
            <div>
              <div className="bot-name">AgroBot</div>
              <div className="bot-status">
                <span className="status-dot"></span>
                Agronexus Trading Assistant
              </div>
            </div>
          </div>
          <a href="mailto:info@agronexustrading.in" className="contact-btn">
            Contact Us
          </a>
        </div>

        {/* Messages */}
        <div className="messages">
          {messages.map((msg, i) => (
            <div key={i} className={`msg ${msg.role} ${msg.error ? "error" : ""}`}>
              {msg.role === "bot" && <div className="msg-avatar">🌿</div>}
              <div className="msg-bubble">{msg.text}</div>
            </div>
          ))}

          {/* Loading indicator */}
          {loading && (
            <div className="msg bot">
              <div className="msg-avatar">🌿</div>
              <div className="msg-bubble typing">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}

          {/* Suggested questions — only show at start */}
          {messages.length === 1 && !loading && (
            <div className="suggestions">
              <p className="suggestions-label">Try asking:</p>
              {SUGGESTIONS.map((s, i) => (
                <button key={i} className="suggestion-btn"
                  onClick={() => sendMessage(s)}>{s}</button>
              ))}
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="chat-input-area">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about our spices, pricing, shipping..."
            disabled={loading}
            rows={1}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="send-btn"
          >
            {loading ? "..." : "Send"}
          </button>
        </div>

      </div>
    </div>
  )
}