import React, { useState, useEffect } from 'react'
import AboutSection from './AboutSection'

const RelationshipViewer = ({ sysmlComments = [] }) => {
  const [relationships, setRelationships] = useState([])
  const [filteredRelationships, setFilteredRelationships] = useState([])
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedRelationship, setSelectedRelationship] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetch('/relationship_images_metadata.json')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load metadata.')
        }
        return response.json()
      })
      .then(data => {
        const rels = data.relationships || []
        // Show all relationships, not just those with images
        setRelationships(rels)
        setFilteredRelationships(rels)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  useEffect(() => {
    let filtered = relationships
    
    if (selectedCategory === 'all') {
      filtered = relationships
    } else if (selectedCategory === 'complete') {
      filtered = relationships.filter(r => r.relationship_category === 'complete')
    } else {
      filtered = relationships.filter(r => 
        r.relationship_category === selectedCategory
      )
    }
    
    if (searchTerm) {
      filtered = filtered.filter(rel => 
        rel.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rel.from_element?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rel.to_element?.name?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    
    setFilteredRelationships(filtered)
    
    if (filtered.length > 0 && !selectedRelationship) {
      setSelectedRelationship(filtered[0])
    } else if (filtered.length === 0) {
      setSelectedRelationship(null)
    }
  }, [selectedCategory, relationships, searchTerm])

  // Dynamically generate categories from relationships
  const [availableCategories, setAvailableCategories] = useState([
    { value: 'all', label: 'All', icon: '📋' },
    { value: 'complete', label: 'Complete', icon: '📊' },
  ])

  useEffect(() => {
    // Extract unique categories from relationships AND metadata categories
    const uniqueCategories = new Set()
    relationships.forEach(rel => {
      if (rel.relationship_category && rel.relationship_category !== 'complete') {
        uniqueCategories.add(rel.relationship_category)
      }
    })
    
    // Also include all categories from metadata (even if empty) so filters show all options
    fetch('/relationship_images_metadata.json')
      .then(response => response.json())
      .then(data => {
        if (data.categories) {
          Object.keys(data.categories).forEach(cat => {
            if (cat !== 'complete') {
              uniqueCategories.add(cat)
            }
          })
        }
      })
      .catch(() => {})
    
    // Category definitions with labels and icons
    const categoryDefinitions = {
      'part_to_actor': { label: 'Part → Actor', icon: '🔗' },
      'part_to_part': { label: 'Part → Part', icon: '⚙️' },
      'part_to_subject': { label: 'Part → Subject', icon: '📌' },
      'actor_to_use_case': { label: 'Actor → Use Case', icon: '🎯' },
      'subject_to_use_case': { label: 'Subject → Use Case', icon: '🎪' },
      'system_to_part': { label: 'System → Part', icon: '🏗️' },
      'other': { label: 'Other', icon: '🔀' },
    }
    
    // Build category list - ALWAYS show all 5 main categories, even if empty
    const allMainCategories = ['part_to_actor', 'part_to_part', 'part_to_subject', 'actor_to_use_case', 'subject_to_use_case']
    const categoryList = [
      { value: 'all', label: 'All', icon: '📋' },
      { value: 'complete', label: 'Complete', icon: '📊' },
      ...allMainCategories.map(cat => ({
        value: cat,
        label: categoryDefinitions[cat]?.label || cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        icon: categoryDefinitions[cat]?.icon || '🔗'
      })),
      ...Array.from(uniqueCategories)
        .filter(cat => !allMainCategories.includes(cat))
        .map(cat => ({
          value: cat,
          label: categoryDefinitions[cat]?.label || cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          icon: categoryDefinitions[cat]?.icon || '🔗'
        }))
    ]
    
    setAvailableCategories(categoryList)
  }, [relationships])

  const getCategoryColor = (category) => {
    const colors = {
      'part_to_actor': 'from-cyan-500 to-cyan-600',
      'part_to_part': 'from-blue-500 to-blue-600',
      'part_to_subject': 'from-pink-500 to-pink-600',
      'actor_to_use_case': 'from-purple-500 to-purple-600',
      'subject_to_use_case': 'from-indigo-500 to-indigo-600',
      'system_to_part': 'from-green-500 to-green-600',
      'complete': 'from-pink-500 to-cyan-500',
      'other': 'from-gray-500 to-gray-600'
    }
    return colors[category] || 'from-gray-500 to-gray-600'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="glass-card rounded-2xl p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-400 mx-auto mb-4"></div>
          <p className="text-cyan-200 font-semibold neon-text-cyan">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <div className="glass-card rounded-2xl p-4 border-pink-500">
          <p className="text-pink-300 font-semibold neon-text-pink">
            <strong>Error:</strong> {error}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen overflow-hidden flex flex-col p-4">
      {/* Header */}
      <div className="glass-card rounded-2xl p-4 flex-shrink-0 mb-4 border-purple-500">
        <div className="flex justify-between items-center flex-wrap gap-2">
          <h2 className="text-xl font-bold text-cyan-100">
            ⚡ SysML Relationship Viewer
          </h2>
          <div className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400/50">
            <span className="text-cyan-200 font-semibold">{relationships.length} relationships</span>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="glass-card rounded-2xl p-4 flex-shrink-0 mb-4 border-cyan-500">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="bg-cyberpunk-dark/60 backdrop-blur-xl border border-purple-500/50 rounded-xl px-4 py-2 text-cyan-300 font-medium focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-all w-full"
          >
            {availableCategories.map(cat => (
              <option key={cat.value} value={cat.value} className="bg-cyberpunk-darker">
                {cat.icon} {cat.label}
              </option>
            ))}
          </select>
          
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-cyberpunk-dark/60 backdrop-blur-xl border border-purple-500/50 rounded-xl px-4 py-2 text-cyan-300 placeholder-cyan-400/70 font-medium focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-pink-500 transition-all w-full"
          />
        </div>
      </div>

      {/* Main Layout: Flexbox with Sidebar (fixed width) and Main Content (flex-1) */}
      <div className="flex-1 flex gap-4 min-h-0 overflow-hidden">
        {/* Left Sidebar - Fixed Width */}
        <div className="w-80 flex-shrink-0 flex flex-col space-y-4">
          {/* About Section - Separate Card */}
          {sysmlComments && Array.isArray(sysmlComments) && sysmlComments.length > 0 ? (
            <div className="flex-shrink-0">
              <AboutSection sysmlComments={sysmlComments} />
            </div>
          ) : (
            <div className="flex-shrink-0 text-xs text-cyan-400/50 p-2">
              {/* Debug: About section not showing - sysmlComments: {sysmlComments ? JSON.stringify(sysmlComments).substring(0, 50) : 'null'} */}
            </div>
          )}
          
          {/* Relationship List Card */}
          <div className="glass-sidebar rounded-2xl flex-1 flex flex-col min-h-0 border-purple-500 overflow-hidden p-4">
            <div className="pb-4 border-b border-purple-500/50 flex-shrink-0">
              <h3 className="text-lg font-bold text-cyan-100">
                📋 List ({filteredRelationships.length})
              </h3>
            </div>
            <div className="flex-1 overflow-y-auto space-y-2 pt-4 min-h-0">
              {filteredRelationships.length > 0 ? (
                filteredRelationships.map(rel => (
                  <button
                    key={rel.relationship_id}
                    onClick={() => setSelectedRelationship(rel)}
                    className={`w-full text-left p-4 rounded-xl border transition-all ${
                      selectedRelationship?.relationship_id === rel.relationship_id
                        ? 'bg-gradient-to-r from-pink-500/30 to-cyan-500/30 border-pink-500 shadow-neon-pink'
                        : 'bg-cyberpunk-dark/50 border-purple-500/30 hover:border-cyan-500/50 hover:bg-cyberpunk-dark/60'
                    }`}
                  >
                    <div className="font-bold text-cyan-200 mb-2 truncate">{rel.description || rel.relationship_id}</div>
                    <div className="flex gap-2">
                      <span className={`px-2 py-1 rounded-lg text-xs font-semibold bg-gradient-to-r ${getCategoryColor(rel.relationship_category)} text-white`}>
                        {rel.relationship_category?.replace('_', ' ') || 'N/A'}
                      </span>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center p-4 text-cyan-300/80">
                  No relationships found
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content Area - flex-1 */}
        <div className="flex-1 min-w-0 flex flex-col">
          <div className="glass-card rounded-2xl h-full flex flex-col border-cyan-500 overflow-hidden">
            <div className="flex-1 flex items-center justify-center p-4 min-h-0 overflow-hidden">
              {selectedRelationship ? (
                <div className="w-full h-full flex flex-col">
                  <div className="flex-1 flex items-center justify-center overflow-hidden min-h-0">
                    {selectedRelationship.image_filename || selectedRelationship.image_path ? (
                      <img
                        src={`/generated_images/${selectedRelationship.image_filename || selectedRelationship.image_path?.split('/').pop()}`}
                        alt={selectedRelationship.description}
                        className="max-h-full max-w-full object-contain rounded-xl shadow-neon-cyan"
                        onError={(e) => {
                          if (selectedRelationship.image_filename === 'complete_sysml_diagram_gemini.png') {
                            e.target.src = '/generated_images/complete_sysml_diagram.png'
                            return
                          }
                          e.target.style.display = 'none'
                        }}
                      />
                    ) : (
                      <div className="text-center text-cyan-300/90 p-8">
                        <div className="text-6xl mb-4">🖼️</div>
                        <p className="font-medium text-lg mb-2">Image not yet generated</p>
                        <p className="text-sm text-cyan-400/70">Relationship: {selectedRelationship.description}</p>
                      </div>
                    )}
                  </div>
                  <div className="mt-4 p-4 border-t border-cyan-500/50 flex-shrink-0">
                    <h3 className="text-lg font-bold text-cyan-200 mb-2 neon-text-cyan truncate">
                      {selectedRelationship.description}
                    </h3>
                    {selectedRelationship.connection_type !== 'COMPLETE' && (
                      <div className="flex gap-2 flex-wrap">
                        <span className="px-3 py-1 rounded-lg bg-gradient-to-r from-pink-500/30 to-cyan-500/30 border border-pink-500/50 text-cyan-200 text-sm font-medium">
                          {selectedRelationship.from_element?.name} → {selectedRelationship.to_element?.name}
                        </span>
                        <span className="px-3 py-1 rounded-lg bg-gradient-to-r from-purple-500/30 to-indigo-500/30 border border-purple-500/50 text-cyan-200 text-sm font-medium">
                          {selectedRelationship.connection_type}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center text-cyan-300/90">
                  <div className="text-6xl mb-4">🖼️</div>
                  <p className="font-medium">Select a relationship to view</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Stat Cards - Grid layout with 4 equal cards */}
      <div className="grid grid-cols-4 gap-4 flex-shrink-0 mt-4">
        <div className="glass-card rounded-2xl p-4 text-center border-pink-500 h-24 flex flex-col items-center justify-center">
          <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-cyan-400 mb-1">
            {relationships.length}
          </div>
          <div className="text-cyan-200 text-sm font-medium">Total</div>
        </div>
        <div className="glass-card rounded-2xl p-4 text-center border-cyan-500 h-24 flex flex-col items-center justify-center">
          <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-pink-300 mb-1">
            {filteredRelationships.length}
          </div>
          <div className="text-cyan-200 text-sm font-medium">Filtered</div>
        </div>
        <div className="glass-card rounded-2xl p-4 text-center border-purple-500 h-24 flex flex-col items-center justify-center">
          <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-pink-300 mb-1">
            {relationships.filter(r => r.image_path || r.image_filename).length}
          </div>
          <div className="text-cyan-200 text-sm font-medium">With Images</div>
        </div>
        <div className="glass-card rounded-2xl p-4 text-center border-indigo-500 h-24 flex flex-col items-center justify-center">
          <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 to-cyan-300 mb-1">
            {selectedRelationship ? 1 : 0}
          </div>
          <div className="text-cyan-200 text-sm font-medium">Selected</div>
        </div>
      </div>
    </div>
  )
}

export default RelationshipViewer
