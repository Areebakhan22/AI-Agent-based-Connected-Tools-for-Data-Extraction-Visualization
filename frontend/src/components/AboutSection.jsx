import React, { useState } from 'react'

const AboutSection = ({ sysmlComments }) => {
  const [isOpen, setIsOpen] = useState(false)

  if (!sysmlComments || (Array.isArray(sysmlComments) && sysmlComments.length === 0)) {
    return null
  }

  const comments = Array.isArray(sysmlComments) ? sysmlComments : []

  return (
    <div className="glass-card rounded-2xl border-purple-500 overflow-hidden p-4">
      <div
        className="bg-gradient-to-r from-purple-500/30 to-pink-500/30 p-4 border-b border-purple-500/50 cursor-pointer hover:from-purple-500/40 hover:to-pink-500/40 transition-all -m-4 mb-4"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex justify-between items-center">
          <span className="font-bold text-cyan-100">
            ℹ️ About System {comments.length > 0 && `(${comments.length})`}
          </span>
          <span className="text-cyan-200 font-semibold">
            {isOpen ? '▲' : '▼'}
          </span>
        </div>
      </div>
      {isOpen && (
        <div className="max-h-64 overflow-y-auto space-y-4">
          {comments.length > 0 ? (
            comments.map((comment, idx) => (
              <div key={idx} className="border-b border-purple-500/30 pb-3 last:border-b-0 last:pb-0">
                {comment.title && (
                  <div className="mb-2">
                    <span className="text-cyan-200 font-bold text-sm neon-text-cyan">
                      {comment.title}
                    </span>
                  </div>
                )}
                {(comment.raw_comment || comment.content) && (
                  <pre className="text-cyan-200 text-xs font-mono whitespace-pre-wrap p-3 rounded-xl bg-cyberpunk-dark/60 border border-cyan-500/30 backdrop-blur-sm overflow-x-auto" style={{
                    lineHeight: '1.6',
                    fontFamily: 'monospace'
                  }}>
                    {comment.raw_comment || comment.content}
                  </pre>
                )}
                {comment.objectives && comment.objectives.length > 0 && !comment.raw_comment && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {comment.objectives.map((obj, objIdx) => (
                      <span
                        key={objIdx}
                        className="px-3 py-1 rounded-lg text-xs font-semibold bg-gradient-to-r from-pink-500/30 to-cyan-500/30 border border-pink-500/50 text-cyan-200"
                      >
                        {obj}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="text-cyan-300/70 text-sm text-center py-4">
              No comments available
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AboutSection
