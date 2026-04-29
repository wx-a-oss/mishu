import { useState, useRef, useEffect } from 'react'
import useWebSocket from './hooks/useWebSocket'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'
import ToolStatus from './components/ToolStatus'
import './App.css'

export default function App() {
  const { messages, toolStatus, sendMessage, connected } = useWebSocket()
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, toolStatus])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Mishu</h1>
        <span className={`status-dot ${connected ? 'connected' : ''}`} />
      </header>

      <div className="messages-container">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {toolStatus && <ToolStatus status={toolStatus} />}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={sendMessage} disabled={!connected} />
    </div>
  )
}
