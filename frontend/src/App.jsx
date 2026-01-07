import React, { useState, useEffect } from 'react'
import RelationshipViewer from './components/RelationshipViewer'

function App() {
  const [sysmlComments, setSysmlComments] = useState([])

  useEffect(() => {
    fetch('/relationship_images_metadata.json')
      .then(response => response.json())
      .then(data => {
        console.log('Loaded metadata:', data)
        if (data.sysml_comments && Array.isArray(data.sysml_comments) && data.sysml_comments.length > 0) {
          console.log('Setting sysmlComments:', data.sysml_comments)
          setSysmlComments(data.sysml_comments)
        } else {
          console.log('No sysml_comments found or empty:', data.sysml_comments)
        }
      })
      .catch(err => {
        console.error('Error loading metadata:', err)
      })
  }, [])

  return (
    <div className="h-screen w-screen overflow-hidden">
      <RelationshipViewer sysmlComments={sysmlComments} />
    </div>
  )
}

export default App
