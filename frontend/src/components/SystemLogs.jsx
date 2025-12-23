import React, { useState, useEffect } from 'react'
import './SystemLogs.css'

function SystemLogs({ logs, onClear }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [autoScroll, setAutoScroll] = useState(true)
  const logEndRef = React.useRef(null)

  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const getLogLevelClass = (level) => {
    switch (level) {
      case 'error': return 'log-error'
      case 'warning': return 'log-warning'
      case 'info': return 'log-info'
      case 'success': return 'log-success'
      default: return 'log-default'
    }
  }

  return (
    <div className={`system-logs ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="logs-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="logs-title">
          <span className="logs-icon">📋</span>
          <span>System Logs</span>
          <span className="logs-count">{logs.length}</span>
        </div>
        <div className="logs-controls">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setAutoScroll(!autoScroll)
            }}
            className={`auto-scroll-btn ${autoScroll ? 'active' : ''}`}
            title="Auto-scroll"
          >
            ⬇️
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              onClear()
            }}
            className="clear-btn"
            title="Clear logs"
          >
            🗑️
          </button>
          <button className="toggle-btn">
            {isExpanded ? '▼' : '▶'}
          </button>
        </div>
      </div>
      
      {isExpanded && (
        <div className="logs-content">
          {logs.length === 0 ? (
            <div className="logs-empty">No logs yet. Processing will start when you select a diagram.</div>
          ) : (
            <div className="logs-list">
              {logs.map((log, index) => (
                <div key={index} className={`log-entry ${getLogLevelClass(log.level)}`}>
                  <span className="log-time">{log.time}</span>
                  <span className="log-level">[{log.level.toUpperCase()}]</span>
                  <span className="log-message">{log.message}</span>
                  {log.details && (
                    <div className="log-details">{log.details}</div>
                  )}
                </div>
              ))}
              <div ref={logEndRef} />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SystemLogs

