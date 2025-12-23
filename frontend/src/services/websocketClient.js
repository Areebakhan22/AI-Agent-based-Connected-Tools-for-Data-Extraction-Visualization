import { io } from 'socket.io-client'

export function websocketClient(diagramId) {
  let socket = null
  let callbacks = {
    onConnect: null,
    onDisconnect: null,
    onError: null,
    onUpdate: null
  }

  const connect = () => {
    socket = io('http://localhost:5000', {
      query: { diagramId },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      timeout: 20000
    })

    socket.on('connect', () => {
      console.log('WebSocket connected')
      if (callbacks.onConnect) callbacks.onConnect()
    })

    socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      if (callbacks.onDisconnect) callbacks.onDisconnect()
    })

    socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      if (callbacks.onError) callbacks.onError(error)
    })

    socket.on('diagram_update', (data) => {
      if (callbacks.onUpdate) {
        callbacks.onUpdate({ type: 'diagram_update', data })
      }
    })

    socket.on('node_update', (data) => {
      if (callbacks.onUpdate) {
        callbacks.onUpdate(data)
      }
    })
  }

  const sendUpdate = (update) => {
    if (socket && socket.connected) {
      socket.emit('node_update', {
        diagramId,
        ...update
      })
    } else {
      console.warn('WebSocket not connected, update not sent:', update)
    }
  }

  const close = () => {
    if (socket) {
      socket.disconnect()
      socket = null
    }
  }

  return {
    connect,
    sendUpdate,
    close,
    onConnect: (callback) => { callbacks.onConnect = callback },
    onDisconnect: (callback) => { callbacks.onDisconnect = callback },
    onError: (callback) => { callbacks.onError = callback },
    onUpdate: (callback) => { callbacks.onUpdate = callback }
  }
}

