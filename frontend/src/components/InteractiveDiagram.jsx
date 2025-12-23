import React, { useEffect, useRef, useState } from 'react'
import { D3DiagramRenderer } from '../utils/d3Renderer'
import { websocketClient } from '../services/websocketClient'
import { apiClient } from '../services/apiClient'
import { adaptJsonToD3 } from '../utils/diagramDataAdapter'
import SystemLogs from './SystemLogs'
import './InteractiveDiagram.css'

function InteractiveDiagram({ diagramId }) {
  const svgRef = useRef(null)
  const containerRef = useRef(null)
  const rendererRef = useRef(null)
  const wsClientRef = useRef(null)
  const [diagramData, setDiagramData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState(null)
  const [logs, setLogs] = useState([])
  
  const addLog = (level, message, details = null) => {
    const time = new Date().toLocaleTimeString()
    setLogs(prev => [...prev, { time, level, message, details }])
  }
  
  const clearLogs = () => {
    setLogs([])
  }

  useEffect(() => {
    loadDiagramData()

    return () => {
      // Cleanup WebSocket on unmount
      if (wsClientRef.current) {
        wsClientRef.current.close()
      }
    }
  }, [diagramId])

  const loadDiagramData = async () => {
    try {
      addLog('info', `Loading diagram: ${diagramId}`)
      addLog('info', 'Fetching diagram data from API...')
      
      const response = await apiClient.getDiagram(diagramId)
      addLog('success', 'Diagram data received from API')
      
      // Check if data needs adaptation
      let data
      if (response.data.nodes && response.data.links) {
        // Already in D3 format, but ensure proper node types
        data = response.data
        addLog('info', 'Data is already in D3 format')
        
        // Fix node types: Identify actors from connections and metadata
        // For individual relationship diagrams: Part → Actor connections
        // Actors are targets of connections from parts
        const actorNames = new Set()
        const useCaseNames = new Set()
        
        // Collect actor names from links (toName in connections)
        data.links.forEach(link => {
          if (link.toName && link.toName !== 'SoI') {
            actorNames.add(link.toName)
          }
        })
        
        // Also check metadata for relationship info
        if (response.data.metadata?.relationship) {
          const rel = response.data.metadata.relationship
          if (rel.to && rel.to !== 'SoI') {
            actorNames.add(rel.to)
          }
        }
        
        // Collect use case names
        data.nodes.forEach(node => {
          if (node.type === 'use_case') {
            useCaseNames.add(node.name)
          }
        })
        
        // Update node types: Convert actor parts to actor type
        data.nodes.forEach(node => {
          // Mark system boundary
          const systemName = response.data.metadata?.system_boundary || 
                            response.data.metadata?.system_name ||
                            data.nodes.find(n => n.name && (n.name.includes('OpsCon') || n.name.includes('System')))?.name
          
          if (systemName && node.name === systemName && node.type === 'part') {
            node.is_top_level = true
          }
          
          // Fix actors: if node name matches an actor name and it's currently a part, convert to actor
          if (actorNames.has(node.name) && node.type === 'part' && 
              !node.is_top_level && node.name !== systemName) {
            node.type = 'actor'
            node.size = 40 // Handle size for use case oval edge
            node.width = 40
            node.height = 40
            node.isHandle = true // Mark as handle on use case
            addLog('info', `Converted to actor handle: ${node.name}`)
          }
        })
        
        // For individual relationship diagrams: Filter out SoI and fix connections
        const isIndividualDiagram = response.data.metadata?.is_full_diagram === false
        
        if (isIndividualDiagram) {
          // Remove SoI from individual relationship diagrams
          data.nodes = data.nodes.filter(node => node.type !== 'soi')
          addLog('info', 'Filtered out SoI from individual relationship diagram')
          
          // Fix connections: Part → Use Case with targetHandle (Actor name)
          data.links.forEach(link => {
            const sourceNode = data.nodes.find(n => n.id === link.source)
            const targetNode = data.nodes.find(n => n.id === link.target)
            
            // If target is an actor, change to: Part → Use Case with targetHandle
            if (targetNode && targetNode.type === 'actor') {
              const useCaseNode = data.nodes.find(n => n.type === 'use_case')
              if (useCaseNode) {
                link.target = useCaseNode.id
                link.targetHandle = targetNode.name // Actor name as handle
                addLog('info', `Updated link: ${sourceNode?.name} → ${useCaseNode.name} (handle: ${targetNode.name})`)
              }
            }
          })
        } else {
          // Full diagram: Keep all connections as-is
          data.links.forEach(link => {
            const sourceNode = data.nodes.find(n => n.id === link.source)
            const targetNode = data.nodes.find(n => n.id === link.target)
            
            if (targetNode && targetNode.type === 'actor') {
              addLog('info', `Link: ${sourceNode?.name} → ${targetNode.name} (actor)`)
            }
          })
        }
      } else {
        // Needs adaptation
        addLog('info', 'Adapting data format for D3.js...')
        data = adaptJsonToD3(response.data)
        addLog('success', `Adapted ${data.nodes.length} nodes and ${data.links.length} links`)
      }
      
      addLog('info', `Diagram: ${data.title || diagramId}`)
      addLog('info', `Nodes: ${data.nodes.length}, Links: ${data.links.length}`)
      
      setDiagramData(data)
      
      // Initialize renderer
      if (svgRef.current && data) {
        addLog('info', 'Initializing D3.js renderer...')
        initializeRenderer(data)
        addLog('success', 'D3.js renderer initialized')
        setupWebSocket(diagramId, data)
      }
    } catch (err) {
      console.error('Error loading diagram:', err)
      addLog('error', `Failed to load diagram: ${err.message}`, err.stack)
      setError(`Failed to load diagram: ${err.message}`)
    }
  }

  const initializeRenderer = (data) => {
    if (!svgRef.current) return

    const renderer = new D3DiagramRenderer(svgRef.current, {
      width: 960,
      height: 540,
      onNodeDrag: handleNodeDrag,
      onNodeRename: handleNodeRename
    })

    renderer.render(data.nodes, data.links)
    rendererRef.current = renderer
  }

  const setupWebSocket = (diagramId, initialData) => {
    addLog('info', `Setting up WebSocket connection for diagram: ${diagramId}`)
    const wsClient = websocketClient(diagramId)
    
    wsClient.onConnect(() => {
      addLog('success', 'WebSocket connected successfully')
      setIsConnected(true)
      setError(null)
    })

    wsClient.onDisconnect(() => {
      addLog('warning', 'WebSocket disconnected')
      setIsConnected(false)
    })

    wsClient.onError((err) => {
      addLog('error', `WebSocket error: ${err.message || 'Connection failed'}`)
      setError(`WebSocket error: ${err.message || 'Connection failed'}`)
      setIsConnected(false)
    })

    wsClient.onUpdate((update) => {
      addLog('info', `Received update: ${update.type}`)
      // Handle real-time updates from backend
      if (update.type === 'diagram_update') {
        const adaptedData = adaptJsonToD3(update.data)
        setDiagramData(adaptedData)
        if (rendererRef.current) {
          rendererRef.current.update(adaptedData.nodes, adaptedData.links)
          addLog('success', 'Diagram updated from server')
        }
      } else if (update.type === 'node_moved') {
        // Update specific node position
        if (rendererRef.current) {
          rendererRef.current.updateNodePosition(update.nodeId, update.position)
          addLog('info', `Node ${update.nodeId} moved to (${update.position.x}, ${update.position.y})`)
        }
      } else if (update.type === 'node_renamed') {
        // Update specific node name
        if (rendererRef.current) {
          rendererRef.current.updateNodeName(update.nodeId, update.name)
          addLog('info', `Node ${update.nodeId} renamed to: ${update.name}`)
        }
      }
    })

    wsClientRef.current = wsClient
    addLog('info', 'Connecting to WebSocket server...')
    wsClient.connect()
  }

  const handleNodeDrag = (nodeId, position) => {
    addLog('info', `Node dragged: ${nodeId} → (${Math.round(position.x)}, ${Math.round(position.y)})`)
    // Send update to backend
    if (wsClientRef.current) {
      wsClientRef.current.sendUpdate({
        type: 'node_moved',
        nodeId,
        position
      })
      addLog('success', 'Position update sent to server')
    } else {
      addLog('warning', 'WebSocket not connected, update not sent')
    }
  }

  const handleNodeRename = (nodeId, newName) => {
    addLog('info', `Node renamed: ${nodeId} → ${newName}`)
    // Send update to backend
    if (wsClientRef.current) {
      wsClientRef.current.sendUpdate({
        type: 'node_renamed',
        nodeId,
        name: newName
      })
      addLog('success', 'Rename update sent to server')
    } else {
      addLog('warning', 'WebSocket not connected, update not sent')
    }
  }

  if (error) {
    return (
      <div className="diagram-error">
        <p>{error}</p>
        <button onClick={loadDiagramData}>Retry</button>
      </div>
    )
  }

  if (!diagramData) {
    return <div className="diagram-loading">Loading diagram...</div>
  }

  return (
    <div className="interactive-diagram-container">
      <div className="diagram-status">
        <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '● Connected' : '○ Disconnected'}
        </span>
        <span className="diagram-title">{diagramData.title || 'Diagram'}</span>
      </div>
      
      <div ref={containerRef} className="diagram-wrapper">
        <svg ref={svgRef} className="diagram-svg" />
      </div>

      <div className="diagram-legend">
        <div className="legend-item">
          <span className="legend-shape legend-oval"></span>
          <span>Use Case (Oval)</span>
        </div>
        <div className="legend-item">
          <span className="legend-shape legend-circle"></span>
          <span>Actor (Circle)</span>
        </div>
        <div className="legend-item">
          <span className="legend-shape legend-rect"></span>
          <span>Part (Rectangle)</span>
        </div>
        <div className="legend-item">
          <span className="legend-shape legend-soi"></span>
          <span>Subject of Interest</span>
        </div>
      </div>

      <SystemLogs logs={logs} onClear={clearLogs} />
    </div>
  )
}

export default InteractiveDiagram

