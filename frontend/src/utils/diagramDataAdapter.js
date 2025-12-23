/**
 * Adapts existing JSON format from LLM pipeline to D3.js format
 * 
 * Input format (from visualize_sysml.py):
 * {
 *   "parts": [...],
 *   "actors": [...],
 *   "use_cases": [...],
 *   "connections": [...],
 *   "hierarchy": {...}
 * }
 * 
 * Output format (for D3.js):
 * {
 *   nodes: [{ id, name, type, x, y, width, height, ... }],
 *   links: [{ source, target, dashed, ... }],
 *   title: "..."
 * }
 */

export function adaptJsonToD3(jsonData) {
  const nodes = []
  const links = []
  const nodeMap = new Map()

  // Extract title
  const title = jsonData.diagram_title || 
                jsonData.system_boundary || 
                jsonData.title || 
                'SysML Diagram'

  // Process parts - identify system boundary and regular parts
  if (jsonData.parts && Array.isArray(jsonData.parts)) {
    jsonData.parts.forEach(part => {
      const nodeId = `part_${part.name}`
      const isTopLevel = part.is_top_level || part.parent === null
      
      const node = {
        id: nodeId,
        name: part.name,
        type: 'part',
        width: 140,
        height: 60,
        x: 0, // Will be set by layout calculation
        y: 0,
        doc: part.doc || '',
        parent: part.parent || null,
        is_top_level: isTopLevel
      }
      nodes.push(node)
      nodeMap.set(part.name, node)
    })
  }

  // Process actors
  if (jsonData.actors && Array.isArray(jsonData.actors)) {
    jsonData.actors.forEach(actor => {
      const nodeId = `actor_${actor.name}`
      const node = {
        id: nodeId,
        name: actor.name,
        type: 'actor',
        size: 55,
        width: 55,
        height: 55,
        x: 0,
        y: 0,
        doc: actor.doc || ''
      }
      nodes.push(node)
      nodeMap.set(actor.name, node)
    })
  }

  // Process use cases
  if (jsonData.use_cases && Array.isArray(jsonData.use_cases)) {
    jsonData.use_cases.forEach(useCase => {
      const nodeId = `usecase_${useCase.name}`
      const node = {
        id: nodeId,
        name: useCase.name,
        type: 'use_case',
        width: 280,
        height: 90,
        x: 0,
        y: 0,
        doc: useCase.doc || '',
        objectives: useCase.objectives || []
      }
      nodes.push(node)
      nodeMap.set(useCase.name, node)
    })
  }

  // Process SoI (Subject of Interest) if present
  if (jsonData.soi) {
    const soi = jsonData.soi
    const nodeId = 'soi'
    const node = {
      id: nodeId,
      name: 'SoI',
      type: 'soi',
      width: 80,
      height: 50,
      x: 0,
      y: 0
    }
    nodes.push(node)
    nodeMap.set('SoI', node)
  }

  // Process connections: Part → Use Case (with targetHandle = Actor name)
  // Universal Rule: connect [Source Part] to [Target Actor] maps to:
  // - Source ID: Part name
  // - Target ID: Use Case name (where actor is defined)
  // - Target Handle: Actor name
  if (jsonData.connections && Array.isArray(jsonData.connections)) {
    jsonData.connections.forEach(conn => {
      const fromName = conn.from  // Part name (Source)
      const toName = conn.to       // Actor name (Target Handle)
      
      // Check if connection involves SoI (dashed line)
      const isDashed = toName === 'SoI' || fromName === 'SoI'
      
      // Find source (Part) node
      const sourceNode = nodeMap.get(fromName)
      
      // Find target: Use Case (where actor is defined)
      // Actors are defined inside use cases, so find the use case
      const useCases = jsonData.use_cases || []
      let targetUseCase = null
      
      // Find use case that contains this actor
      // In SysML: actors are declared inside use case blocks
      if (useCases.length > 0) {
        // For now, use the first use case (can be enhanced to match actor to specific use case)
        targetUseCase = useCases[0]
      }
      
      // If no use case found, fallback to actor as target
      let targetNode = null
      let targetHandle = null
      
      if (targetUseCase) {
        const useCaseNode = nodeMap.get(targetUseCase.name)
        if (useCaseNode) {
          targetNode = useCaseNode
          targetHandle = toName // Actor name is the handle
        }
      }
      
      // Fallback: if use case not found, use actor directly
      if (!targetNode) {
        let actorNode = nodeMap.get(toName)
        if (!actorNode && jsonData.actors) {
          const actor = jsonData.actors.find(a => a.name === toName)
          if (actor) {
            const nodeId = `actor_${actor.name}`
            actorNode = {
              id: nodeId,
              name: actor.name,
              type: 'actor',
              size: 12,
              width: 12,
              height: 12,
              x: 0,
              y: 0,
              doc: actor.doc || ''
            }
            nodes.push(actorNode)
            nodeMap.set(actor.name, actorNode)
          }
        }
        targetNode = actorNode
      }
      
      if (sourceNode && targetNode) {
        links.push({
          source: sourceNode.id,
          target: targetNode.id,
          targetHandle: targetHandle, // Actor name as handle
          dashed: isDashed,
          fromName: fromName,
          toName: toName
        })
      }
    })
  }

  // If data comes from layout calculation (with positions), preserve them
  if (jsonData.layout && jsonData.layout.elements) {
    Object.entries(jsonData.layout.elements).forEach(([name, layout]) => {
      const node = nodes.find(n => 
        n.name === name || n.id.includes(name.toLowerCase().replace(/\s+/g, ''))
      )
      if (node && layout.x !== undefined && layout.y !== undefined) {
        // Convert from layout coordinates (which might be top-left) to center coordinates
        if (node.type === 'actor') {
          // Actors use center coordinates
          node.x = layout.x
          node.y = layout.y
        } else {
          // Parts and use cases: convert top-left to center
          node.x = layout.x + (layout.width || node.width || 0) / 2
          node.y = layout.y + (layout.height || node.height || 0) / 2
        }
        node.fx = node.x // Fixed position initially
        node.fy = node.y
      }
    })
  }

  return {
    nodes,
    links,
    title,
    metadata: {
      partsCount: jsonData.parts?.length || 0,
      actorsCount: jsonData.actors?.length || 0,
      useCasesCount: jsonData.use_cases?.length || 0,
      connectionsCount: links.length
    }
  }
}

/**
 * Adapts complete diagram JSON (from complete_diagram.json format)
 */
export function adaptCompleteDiagramToD3(jsonData) {
  if (jsonData.elements && Array.isArray(jsonData.elements)) {
    // This is the complete_diagram.json format
    const nodes = []
    const links = []
    const nodeMap = new Map()

    jsonData.elements.forEach(element => {
      const nodeId = element.id || `${element.type.toLowerCase()}_${element.text}`
      
      const node = {
        id: nodeId,
        name: element.text,
        type: mapElementTypeToNodeType(element.type),
        x: element.x || 0,
        y: element.y || 0,
        fx: element.x || null, // Fixed position if provided
        fy: element.y || null
      }

      // Set dimensions based on type
      if (element.shape_type === 'ELLIPSE' || element.type === 'USE_CASE') {
        node.width = element.width || 280
        node.height = element.height || 90
      } else if (element.type === 'ACTOR') {
        node.size = element.width || 55
        node.width = element.width || 55
        node.height = element.height || 55
      } else {
        node.width = element.width || 140
        node.height = element.height || 60
      }

      nodes.push(node)
      nodeMap.set(element.text, node)
    })

    // Extract connections from elements or separate connections array
    if (jsonData.connections) {
      jsonData.connections.forEach(conn => {
        const sourceNode = nodeMap.get(conn.from)
        const targetNode = nodeMap.get(conn.to)
        
        if (sourceNode && targetNode) {
          links.push({
            source: sourceNode.id,
            target: targetNode.id,
            dashed: conn.dashed || false
          })
        }
      })
    }

    return {
      nodes,
      links,
      title: jsonData.diagram_title || jsonData.description || 'Complete Diagram'
    }
  }

  // Fallback to standard adapter
  return adaptJsonToD3(jsonData)
}

function mapElementTypeToNodeType(elementType) {
  const mapping = {
    'USE_CASE': 'use_case',
    'ACTOR': 'actor',
    'PART': 'part',
    'SOI': 'soi',
    'SYSTEM': 'system'
  }
  return mapping[elementType] || 'part'
}

