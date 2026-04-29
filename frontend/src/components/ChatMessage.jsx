import './ChatMessage.css'

export default function ChatMessage({ message }) {
  const { role, text } = message
  const isUser = role === 'user'

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="message-label">{isUser ? 'You' : 'Mishu'}</div>
      <div className="message-bubble">
        {text}
      </div>
    </div>
  )
}
