import { useState } from 'react'
import './ChatInput.css'

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState('')

  const handleSend = () => {
    const trimmed = text.trim()
    if (!trimmed) return
    onSend(trimmed)
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-input">
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={disabled ? 'Connecting...' : 'Type a message...'}
        disabled={disabled}
        rows={1}
      />
      <button onClick={handleSend} disabled={disabled || !text.trim()}>
        Send
      </button>
    </div>
  )
}
