import * as d3 from 'd3'

export class D3DiagramRenderer {
  constructor(svgElement, options = {}) {
    this.svg = d3.select(svgElement)
    this.simulation = null
    this.nodes = []
    this.links = []
    this.width = options.width || 960
    this.height = options.height || 540
    this.onNodeDrag = options.onNodeDrag || null
    this.onNodeRename = options.onNodeRename || null
    
    // HD rendering setup
    this.setupHD()
    this.createDefs()
  }

  setupHD() {
    const dpr = window.devicePixelRatio || 1
    
    this.svg
      .attr('width', this.width)
      .attr('height', this.height)
      .attr('viewBox', `0 0 ${this.width} ${this.height}`)
      .style('width', `${this.width}px`)
      .style('height', `${this.height}px`)
      .style('background', '#ffffff')
      .style('shape-rendering', 'geometricPrecision')
      .style('text-rendering', 'geometricPrecision')
      .style('image-rendering', '-webkit-optimize-contrast')
      .style('image-rendering', 'crisp-edges')
  }

  createDefs() {
    const defs = this.svg.append('defs')

    // Arrow markers (HD quality)
    const arrowMarker = defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('markerWidth', 12)
      .attr('markerHeight', 12)
      .attr('refX', 10)
      .attr('refY', 3)
      .attr('orient', 'auto')
      .style('shape-rendering', 'geometricPrecision')

    arrowMarker.append('polygon')
      .attr('points', '0 0, 12 3, 0 6')
      .attr('fill', '#000')

    // Dashed arrow marker
    const dashedArrowMarker = defs.append('marker')
      .attr('id', 'arrowhead-dashed')
      .attr('markerWidth', 12)
      .attr('markerHeight', 12)
      .attr('refX', 10)
      .attr('refY', 3)
      .attr('orient', 'auto')
      .style('shape-rendering', 'geometricPrecision')

    dashedArrowMarker.append('polygon')
      .attr('points', '0 0, 12 3, 0 6')
      .attr('fill', '#666')

    // Gradients for shapes
    this.createGradients(defs)
  }

  calculateSysMLLayout(nodes) {
    // Diagrammatic Alignment with Box/Area Structure:
    // 1. System Boundary (outer container box) - drawn separately
    // 2. Use Case (oval) - centered horizontally, upper region (box area)
    // 3. Actor Handles (circles) - pinned to right edge of Use Case oval
    // 4. Physical Parts (rectangles) - lower-left region (box area)
    // 5. SoI (Subject of Interest) - upper-right region (box area)
    
    const margin = 50
    const systemBoundaryMargin = 50
    const centerX = this.width / 2
    const centerY = this.height / 2
    
    // Define box areas for proper alignment
    const upperRegion = {
      top: margin + 30,
      bottom: centerY * 0.6,
      left: margin,
      right: this.width - margin
    }
    
    const lowerRegion = {
      top: centerY * 0.6,
      bottom: this.height - margin - 30,
      left: margin,
      right: this.width - margin
    }
    
    const leftBox = {
      left: margin + 20,
      right: centerX - 50,
      top: lowerRegion.top,
      bottom: lowerRegion.bottom
    }
    
    const rightBox = {
      left: centerX + 50,
      right: this.width - margin - 20,
      top: upperRegion.top,
      bottom: upperRegion.bottom
    }
    
    // Dynamically identify elements from structure
    // Level 0: System Boundary (part def - top level part)
    const systemBoundary = nodes.find(n => (n.type === 'part' && n.is_top_level) || 
                                           (n.name && (n.name.includes('OpsCon') || n.name.includes('System'))))
    
    // Level 1: Use Case (behavioral context)
    const useCases = nodes.filter(n => n.type === 'use_case')
    
    // Level 2: Actors (functional roles - inside use case)
    const actors = nodes.filter(n => n.type === 'actor')
    
    // Level 3: Parts (physical entities - exclude system boundary)
    const parts = nodes.filter(n => {
      if (n.type !== 'part') return false
      // Exclude system boundary (top level part)
      if (n.is_top_level) return false
      // Exclude if it's the system name
      if (systemBoundary && n.name === systemBoundary.name) return false
      return true
    })
    
    const sois = nodes.filter(n => n.type === 'soi')
    
    // 1. Position Use Cases: Center-right region (matching reference)
    useCases.forEach((uc, idx) => {
      if (uc.fx === undefined && uc.fy === undefined) {
        // For individual diagrams: position center-right
        // For full diagrams: center horizontally
        const isIndividual = nodes.length <= 4 // Individual diagrams have fewer nodes
        if (isIndividual) {
          uc.x = centerX + 100 // Center-right position
          uc.y = centerY // Vertical center
        } else {
          uc.x = centerX // Centered horizontally
          uc.y = (upperRegion.top + upperRegion.bottom) / 2
        }
        uc.fx = uc.x
        uc.fy = uc.y
      }
    })
    
    // 2. Position Actors: ON the right edge of Use Case oval (as handles)
    const useCaseX = useCases[0]?.x || centerX
    const useCaseY = useCases[0]?.y || (upperRegion.top + upperRegion.bottom) / 2
    const useCaseWidth = useCases[0]?.width || 280
    const useCaseHeight = useCases[0]?.height || 90
    const useCaseRx = useCaseWidth / 2
    const useCaseRy = useCaseHeight / 2
    
    // Actors are handles on the RIGHT EDGE of the use case oval
    actors.forEach((actor, idx) => {
      if (actor.fx === undefined && actor.fy === undefined) {
        const handleSize = 40 // Larger handle
        const handleRadius = handleSize / 2
        
        // Distribute along right edge of ellipse
        const totalActors = actors.length
        const verticalRange = useCaseHeight * 0.7
        const startOffset = -verticalRange / 2
        const relativeY = totalActors > 1 
          ? startOffset + (idx * (verticalRange / (totalActors - 1)))
          : 0
        
        const normalizedY = relativeY / useCaseRy
        const clampedY = Math.max(-0.85, Math.min(0.85, normalizedY))
        const angle = Math.asin(clampedY)
        
        // Point on ellipse perimeter (right edge)
        const edgeX = useCaseX + useCaseRx * Math.cos(angle)
        const edgeY = useCaseY + useCaseRy * Math.sin(angle)
        
        // Position handle ON the edge (partially overlapping)
        const normalX = Math.cos(angle)
        const normalY = Math.sin(angle)
        
        actor.x = edgeX + normalX * (handleRadius * 0.4) // 40% overlap
        actor.y = edgeY + normalY * (handleRadius * 0.4)
        actor.fx = actor.x
        actor.fy = actor.y
        actor.size = handleSize
        actor.width = handleSize
        actor.height = handleSize
        actor.isHandle = true // Mark as handle on use case
      }
    })
    
    // 3. Position Parts: Bottom-left area (matching reference)
    const totalParts = parts.length
    const isIndividual = nodes.length <= 4 // Individual diagrams have fewer nodes
    
    if (isIndividual && totalParts === 1) {
      // Single part in individual diagram: bottom-left position
      parts.forEach((part, idx) => {
        if (part.fx === undefined && part.fy === undefined) {
          part.x = margin + 120 // Left side
          part.y = this.height - margin - 100 // Bottom area
          part.fx = part.x
          part.fy = part.y
        }
      })
    } else {
      // Multiple parts: use box alignment
      const partBoxWidth = leftBox.right - leftBox.left
      const partSpacing = totalParts > 1 ? partBoxWidth / (totalParts + 1) : partBoxWidth / 2
      const partStartX = leftBox.left + partSpacing
      const partCenterY = (leftBox.top + leftBox.bottom) / 2
      
      parts.forEach((part, idx) => {
        if (part.fx === undefined && part.fy === undefined) {
          part.x = partStartX + (idx * partSpacing)
          part.y = partCenterY
          part.fx = part.x
          part.fy = part.y
        }
      })
    }
    
    // 4. Position SoI: Upper-right box area (proper alignment)
    sois.forEach((soi, idx) => {
      if (soi.fx === undefined && soi.fy === undefined) {
        // Position SoI in upper-right box area
        soi.x = rightBox.left + (rightBox.right - rightBox.left) * 0.7 // 70% from left of right box
        soi.y = rightBox.top + (rightBox.bottom - rightBox.top) * 0.3 // 30% from top of right box
        soi.fx = soi.x
        soi.fy = soi.y
      }
    })
  }

  drawSystemBoundary() {
    // Draw system boundary rectangle (outer container) - Layer 1
    // Clear any existing boundary first
    this.svg.selectAll('.system-boundary-group').remove()
    
    const margin = 50
    const boundaryGroup = this.svg.append('g').attr('class', 'system-boundary-group')
    
    // Create gradient for fill
    const defs = this.svg.select('defs')
    const boundaryGrad = defs.append('linearGradient')
      .attr('id', 'boundaryGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', this.width).attr('y2', this.height)
    
    boundaryGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ecf0f1')
      .attr('stop-opacity', 0.3)
    
    boundaryGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#d5dbdb')
      .attr('stop-opacity', 0.3)
    
    boundaryGroup.append('rect')
      .attr('x', margin)
      .attr('y', margin + 30) // Space for title
      .attr('width', this.width - 2 * margin)
      .attr('height', this.height - 2 * margin - 30)
      .attr('rx', 5)
      .attr('fill', 'url(#boundaryGradient)')
      .attr('stroke', '#2c3e50') // Darker border
      .attr('stroke-width', 4) // Thicker border
      .style('shape-rendering', 'geometricPrecision')
      .style('filter', 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2))')
    
    // Add system title in top-left corner
    boundaryGroup.append('text')
      .attr('x', margin + 20)
      .attr('y', margin + 50)
      .attr('font-family', 'Segoe UI, Roboto, Arial, sans-serif')
      .attr('font-size', '16px')
      .attr('font-weight', '700')
      .attr('fill', '#2c3e50')
      .text('OpsCon_UAV_basedAircraftInspection')
  }

  createSmoothstepPath(source, target, targetHandle = null) {
    // Create smoothstep path (90-degree elbow): Part → Use Case (with targetHandle)
    // Reference pattern: Aircraft (bottom-left) → Use Case oval (center-right) → Actor handle (right edge)
    // Universal Rules:
    // - Source: Part rectangle (bottom-right corner for connection start)
    // - Target: Use Case oval (with targetHandle = Actor name on right edge)
    // - Path: smoothstep (90-degree elbow) with markerEnd arrow
    // - Sticky Integrity: targetHandle explicitly linked to actor handle position
    
    let startX, startY, endX, endY
    
    // Start point: Bottom-right corner of Part rectangle (matching reference)
    if (source.type === 'part') {
      startX = source.x + source.width / 2 // Right edge
      startY = source.y + source.height / 2 // Bottom edge
    } else {
      startX = source.x
      startY = source.y
    }
    
    // End point: Bottom-left edge of Use Case oval (matching reference)
    // The connection goes to the use case, not directly to the actor handle
    if (target.type === 'use_case') {
      // Bottom-left edge of use case oval (matching reference image)
      endX = target.x - target.width / 2
      endY = target.y + target.height / 2 // Bottom edge
    } else if (target.type === 'actor') {
      // Actor handle position (if directly connecting to actor)
      endX = target.x
      endY = target.y
    } else {
      endX = target.x
      endY = target.y
    }
    
    // Smoothstep path: 90-degree elbow (L-shaped)
    // Path: Start (Part bottom-right) → horizontal → vertical → End (Use Case bottom-left or Actor handle)
    const midX = endX
    const midY = startY
    
    // Create L-shaped path (horizontal then vertical)
    return `M ${startX} ${startY} 
            L ${midX} ${startY} 
            L ${midX} ${endY}`
  }

  createGradients(defs) {
    // Use Case gradient - More prominent blue
    const useCaseGrad = defs.append('linearGradient')
      .attr('id', 'useCaseGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', 280).attr('y2', 90)

    useCaseGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#d9e6ff')
      .attr('stop-opacity', 1)

    useCaseGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#b3d9ff')
      .attr('stop-opacity', 1)

    // Actor gradient
    const actorGrad = defs.append('linearGradient')
      .attr('id', 'actorGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('cx', '50%').attr('cy', '50%')
      .attr('r', '50%')

    actorGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#fff9c4')

    actorGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#ffe082')

    // Part gradient
    const partGrad = defs.append('linearGradient')
      .attr('id', 'partGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', 140).attr('y2', 60)

    partGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#ffffff')

    partGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#f5f5f5')

    // SoI gradient
    const soiGrad = defs.append('linearGradient')
      .attr('id', 'soiGradient')
      .attr('gradientUnits', 'userSpaceOnUse')
      .attr('x1', 0).attr('y1', 0)
      .attr('x2', 80).attr('y2', 50)

    soiGrad.append('stop')
      .attr('offset', '0%')
      .attr('stop-color', '#c7e6c8')

    soiGrad.append('stop')
      .attr('offset', '100%')
      .attr('stop-color', '#a5d6a7')
  }

  render(nodes, links) {
    this.nodes = nodes
    this.links = links

    // Clear existing
    this.svg.selectAll('.link-group, .node-group, .system-boundary-group').remove()

    // Calculate proper positions based on SysML layout pattern (dynamic)
    this.calculateSysMLLayout(nodes)

    // Setup force simulation - use minimal forces since we have fixed positions
    // Only use collision detection to prevent overlaps
    this.simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(0).strength(0))
      .force('charge', d3.forceManyBody().strength(0)) // Disable charge
      .force('collision', d3.forceCollide().radius(d => {
        if (d.type === 'use_case') return Math.max(d.width, d.height) / 2 + 25
        if (d.type === 'actor') return (d.size || 55) / 2 + 15
        return Math.max(d.width, d.height) / 2 + 15
      }))
      .alpha(0.1) // Start with low alpha
      .alphaDecay(0.05) // Quick decay
      .velocityDecay(0.6)

    // Draw system boundary (outer container)
    this.drawSystemBoundary()
    
    // Draw links (arrows) - ORTHOGONAL/ELBOW lines, FIXED, cannot be removed
    const linkGroup = this.svg.append('g').attr('class', 'link-group')
    
    const link = linkGroup
      .selectAll('path')
      .data(links)
      .enter()
      .append('path')
      .attr('class', d => d.dashed ? 'connection-dashed' : 'connection-arrow')
      .attr('marker-end', d => d.dashed ? 'url(#arrowhead-dashed)' : 'url(#arrowhead)')
      .attr('stroke', d => d.dashed ? '#666' : '#000')
      .attr('stroke-width', 3) // Thicker lines
      .attr('fill', 'none')
      .style('stroke-dasharray', d => d.dashed ? '8,5' : 'none')
      .style('shape-rendering', 'geometricPrecision')
      .style('stroke-linecap', 'round')
      .style('stroke-linejoin', 'round')
      .style('filter', 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2))')

    // Draw nodes (shapes)
    const nodeGroup = this.svg.append('g').attr('class', 'node-group')
    
    // Capture renderer instance for use in callbacks
    const renderer = this
    
    const node = nodeGroup
      .selectAll('g.node')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('data-node-id', d => d.id)
      .call(this.dragHandler())

    // Draw shapes based on type
    node.each(function(d) {
      const shapeGroup = d3.select(this)
      
      if (d.type === 'use_case') {
        // Use Case: Large, prominent blue oval
        const rx = Math.max(d.width / 2, 140)
        const ry = Math.max(d.height / 2, 45)
        shapeGroup.append('ellipse')
          .attr('rx', rx)
          .attr('ry', ry)
          .attr('fill', 'url(#useCaseGradient)')
          .attr('stroke', '#1a73e8')
          .attr('stroke-width', 4)
          .style('filter', 'drop-shadow(0 6px 16px rgba(26, 115, 232, 0.4))')
          .style('shape-rendering', 'geometricPrecision')
          .style('cursor', 'move')
          .attr('class', 'use-case-oval')
        d.width = rx * 2
        d.height = ry * 2
      } else if (d.type === 'actor') {
        // Actors: Orange/yellow circles as handles on use case right edge
        // Position them ON the right edge of the use case oval
        const radius = 20 // Larger, more visible
        shapeGroup.append('circle')
          .attr('r', radius)
          .attr('fill', '#ffe082') // Yellow/orange (matching reference)
          .attr('stroke', '#f57c00')
          .attr('stroke-width', 3) // Thicker border
          .style('filter', 'drop-shadow(0 4px 12px rgba(245, 124, 0, 0.4))')
          .style('shape-rendering', 'geometricPrecision')
          .style('cursor', 'default') // Handles are not draggable
          .attr('class', 'actor-handle')
        d.size = radius * 2
        d.width = radius * 2
        d.height = radius * 2
      } else if (d.type === 'part') {
        // Parts: Large, prominent green rectangles
        const partWidth = Math.max(d.width, 160) // Larger minimum size
        const partHeight = Math.max(d.height, 70)
        shapeGroup.append('rect')
          .attr('width', partWidth)
          .attr('height', partHeight)
          .attr('rx', 4)
          .attr('x', -partWidth / 2)
          .attr('y', -partHeight / 2)
          .attr('fill', '#ffffff') // White fill (matching reference)
          .attr('stroke', '#388e3c')
          .attr('stroke-width', 3) // Thicker border
          .style('filter', 'drop-shadow(0 4px 12px rgba(56, 142, 60, 0.3))')
          .style('shape-rendering', 'geometricPrecision')
          .style('cursor', 'move')
        d.width = partWidth
        d.height = partHeight
      } else if (d.type === 'soi') {
        // SoI: Subject of Interest - Green gradient with purple border (matching reference)
        const soiWidth = Math.max(d.width, 100)
        const soiHeight = Math.max(d.height, 60)
        
        // Create gradient for SoI (green gradient)
        // Use renderer instance (captured outside the loop)
        const defs = renderer.svg.select('defs')
        if (defs.select('#soiGradient').empty()) {
          const soiGrad = defs.append('linearGradient')
            .attr('id', 'soiGradient')
            .attr('gradientUnits', 'userSpaceOnUse')
            .attr('x1', 0).attr('y1', 0)
            .attr('x2', soiWidth).attr('y2', soiHeight)
          
          soiGrad.append('stop')
            .attr('offset', '0%')
            .attr('stop-color', '#c7e6c8')
          
          soiGrad.append('stop')
            .attr('offset', '100%')
            .attr('stop-color', '#a5d6a7')
        }
        
        shapeGroup.append('rect')
          .attr('width', soiWidth)
          .attr('height', soiHeight)
          .attr('rx', 8) // Rounded corners
          .attr('x', -soiWidth / 2)
          .attr('y', -soiHeight / 2)
          .attr('fill', 'url(#soiGradient)') // Green gradient fill
          .attr('stroke', '#7b1fa2') // Purple border (matching reference)
          .attr('stroke-width', 3)
          .style('filter', 'drop-shadow(0 4px 12px rgba(123, 31, 162, 0.3))')
          .style('shape-rendering', 'geometricPrecision')
          .style('cursor', 'move')
        d.width = soiWidth
        d.height = soiHeight
      }

      // Add text (display only)
      const text = shapeGroup.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '.35em')
        .text(d.name)
        .attr('font-family', 'Segoe UI, Roboto, Arial, sans-serif')
        .attr('font-size', d => {
          if (d.type === 'actor') return '11px' // Larger text for actors
          if (d.type === 'use_case') return '14px' // Larger for use cases
          return '13px' // Larger for parts
        })
        .attr('font-weight', '700') // Bolder text
        .attr('fill', d => {
          if (d.type === 'use_case') return '#1a237e' // Dark blue
          if (d.type === 'actor') return '#e65100' // Dark orange
          if (d.type === 'part') return '#1b5e20' // Dark green
          if (d.type === 'soi') return '#4a148c' // Dark purple (text on green gradient)
          return '#4a148c'
        })
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle')
        .style('text-rendering', 'geometricPrecision')
        .style('-webkit-font-smoothing', 'antialiased')
        .style('-moz-osx-font-smoothing', 'grayscale')
        .style('pointer-events', 'none')
        .style('user-select', 'none')
        .attr('class', 'node-text')

      // Make text editable with double-click
      shapeGroup.on('dblclick', function(event, d) {
        event.stopPropagation()
        const currentText = d3.select(this).select('text')
        const textNode = currentText.node()
        const bbox = textNode.getBBox()
        
        // Get current position
        const transform = d3.select(this).attr('transform')
        const translateMatch = transform.match(/translate\(([^,]+),([^)]+)\)/)
        const x = translateMatch ? parseFloat(translateMatch[1]) : d.x
        const y = translateMatch ? parseFloat(translateMatch[2]) : d.y
        
        // Create input field
        const input = renderer.svg.append('foreignObject')
          .attr('x', x + bbox.x - 5)
          .attr('y', y + bbox.y - 2)
          .attr('width', Math.max(bbox.width + 10, 100))
          .attr('height', bbox.height + 4)
          .style('pointer-events', 'all')
          .attr('class', 'text-edit-input')
        
        const inputElement = input.append('xhtml:input')
          .attr('type', 'text')
          .attr('value', d.name)
          .style('width', '100%')
          .style('height', '100%')
          .style('border', '2px solid #667eea')
          .style('border-radius', '4px')
          .style('padding', '2px 5px')
          .style('font-family', 'Segoe UI, Roboto, Arial, sans-serif')
          .style('font-size', d.type === 'actor' ? '10px' : '12px')
          .style('font-weight', '600')
          .style('text-align', 'center')
          .node()
        
        inputElement.focus()
        inputElement.select()
        
        const finishEdit = () => {
          const newName = inputElement.value.trim()
          if (newName && newName !== d.name) {
            d.name = newName
            currentText.text(newName)
            if (renderer.onNodeRename) {
              renderer.onNodeRename(d.id, newName)
            }
          }
          input.remove()
        }
        
        inputElement.addEventListener('blur', finishEdit)
        inputElement.addEventListener('keydown', (e) => {
          if (e.key === 'Enter') {
            e.preventDefault()
            finishEdit()
          } else if (e.key === 'Escape') {
            input.remove()
          }
        })
      })
    })

      // Update positions on simulation tick (outside the loop)
    this.simulation.on('tick', () => {
      // Update smoothstep paths for connections (Part → Use Case with targetHandle)
      link.attr('d', d => {
        const sourceNode = typeof d.source === 'object' ? d.source : this.nodes.find(n => n.id === d.source)
        const targetNode = typeof d.target === 'object' ? d.target : this.nodes.find(n => n.id === d.target)
        const targetHandle = d.targetHandle || d.toName // Actor name as handle
        return this.createSmoothstepPath(sourceNode, targetNode, targetHandle)
      })

      node.attr('transform', d => `translate(${d.x},${d.y})`)
    })
    
    // Stop simulation after initial positioning
    this.simulation.on('end', () => {
      // Release fixed positions for dragging
      nodes.forEach(n => {
        if (n.fx !== undefined && n.fy !== undefined) {
          // Keep positions but allow dragging
          n.fx = null
          n.fy = null
        }
      })
    })
  }

  dragHandler() {
    return d3.drag()
      .on('start', (event, d) => {
        if (!event.active) this.simulation.alphaTarget(0.3).restart()
        d.fx = d.x
        d.fy = d.y
      })
      .on('drag', (event, d) => {
        d.fx = event.x
        d.fy = event.y
        // Arrows automatically update via simulation tick
      })
      .on('end', (event, d) => {
        if (!event.active) this.simulation.alphaTarget(0)
        // Send position update to backend
        if (this.onNodeDrag) {
          this.onNodeDrag(d.id, { x: d.fx, y: d.fy })
        }
        // Release fixed position for smooth animation
        d.fx = null
        d.fy = null
      })
  }

  update(nodes, links) {
    this.nodes = nodes
    this.links = links
    
    // Recalculate layout for new nodes
    this.calculateSysMLLayout(nodes)
    
    if (this.simulation) {
      this.simulation.nodes(nodes)
      this.simulation.force('link').links(links)
      this.simulation.alpha(0.3).restart()
    } else {
      this.render(nodes, links)
    }
  }

  updateNodePosition(nodeId, position) {
    const node = this.nodes.find(n => n.id === nodeId)
    if (node) {
      node.fx = position.x
      node.fy = position.y
      if (this.simulation) {
        this.simulation.alpha(1).restart()
      }
    }
  }

  updateNodeName(nodeId, newName) {
    const node = this.nodes.find(n => n.id === nodeId)
    if (node) {
      node.name = newName
      // Update text element
      this.svg.select(`g.node[data-node-id="${nodeId}"] text`)
        .text(newName)
    }
  }
}

