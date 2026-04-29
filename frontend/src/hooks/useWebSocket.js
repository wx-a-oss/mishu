import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws`

export default function useWebSocket() {
  const [messages, setMessages] = useState([])
  const [toolStatus, setToolStatus] = useState(null)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const connect = useCallback(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onclose = () => {
      setConnected(false)
      wsRef.current = null
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)

      switch (msg.type) {
        case 'assistant_message':
          setToolStatus(null)
          setMessages(prev => [...prev, { role: 'assistant', text: msg.data.text }])
          break
        case 'tool_start':
          setToolStatus({ name: msg.data.name, args: msg.data.args })
          break
        case 'tool_end':
          setToolStatus(null)
          break
        case 'error':
          setToolStatus(null)
          setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${msg.data.text}` }])
          break
      }
    }
  }, [])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((text) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      setMessages(prev => [...prev, { role: 'user', text }])
      wsRef.current.send(JSON.stringify({ message: text }))
    }
  }, [])

  return { messages, toolStatus, sendMessage, connected }
}
