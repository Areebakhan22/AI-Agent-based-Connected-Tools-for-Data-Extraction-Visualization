import React, { useState, useEffect } from 'react'
import InteractiveDiagram from './components/InteractiveDiagram'
import { apiClient } from './services/apiClient'
import './App.css'

function App() {
  const [diagrams, setDiagrams] = useState([])
  const [selectedDiagram, setSelectedDiagram] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadDiagrams()
  }, [])

  const loadDiagrams = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('Loading diagrams from API...')
      // Load from your existing JSON files or API
      const response = await apiClient.getDiagrams()
      console.log('Diagrams response:', response.data)
      setDiagrams(response.data || [])
      if (response.data && response.data.length > 0) {
        setSelectedDiagram(response.data[0].id)
        console.log(`Selected diagram: ${response.data[0].id}`)
      } else {
        setError('No diagrams found. Run: python3 generate_react_diagrams.py OpsCon.json')
      }
    } catch (err) {
      console.error('Error loading diagrams:', err)
      const errorMsg = err.response?.data?.error || err.message || 'Unknown error'
      setError(`Failed to load diagrams: ${errorMsg}. Make sure the backend server is running on port 5000.`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading">Loading diagrams...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="error">{error}</div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <div className="header">
        <h1>SysML Interactive Diagram Viewer</h1>
        <p>Real-time collaborative diagram editing</p>
      </div>

      <div className="diagram-selector">
        <label>Select Diagram: </label>
        <select 
          value={selectedDiagram || ''} 
          onChange={(e) => setSelectedDiagram(e.target.value)}
        >
          {diagrams.map(diagram => (
            <option key={diagram.id} value={diagram.id}>
              {diagram.title}
            </option>
          ))}
        </select>
      </div>

      {selectedDiagram && (
        <InteractiveDiagram 
          diagramId={selectedDiagram}
          key={selectedDiagram}
        />
      )}
    </div>
  )
}

export default App

