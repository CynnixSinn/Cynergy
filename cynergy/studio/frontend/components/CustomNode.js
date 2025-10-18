// components/CustomNode.js
import React from 'react';
import { Handle, Position } from 'reactflow';

export function CustomNode({ data, type }) {
  const nodeColors = {
    agent: '#4A90E2',
    conditional: '#F5A623',
    loop: '#BD10E0',
    task: '#7ED321'
  };

  const color = nodeColors[type] || '#9B9B9B';

  return (
    <div className="custom-node">
      <div 
        className="node-header" 
        style={{ backgroundColor: color }}
      >
        <span className="node-type">{data.type}</span>
      </div>
      <div className="node-content">
        <div className="node-label">{data.label}</div>
        {data.config && Object.keys(data.config).length > 0 && (
          <div className="node-config-indicator">⚙️ Configured</div>
        )}
      </div>
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
      
      <style jsx>{`
        .custom-node {
          width: 200px;
          border: 1px solid #ddd;
          border-radius: 8px;
          background: white;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .node-header {
          padding: 0.5rem;
          color: white;
          border-top-left-radius: 8px;
          border-top-right-radius: 8px;
          font-weight: 500;
          font-size: 0.875rem;
          display: flex;
          align-items: center;
        }
        
        .node-type {
          text-transform: capitalize;
        }
        
        .node-content {
          padding: 0.75rem;
        }
        
        .node-label {
          font-weight: 500;
          margin-bottom: 0.25rem;
          color: #333;
        }
        
        .node-config-indicator {
          font-size: 0.75rem;
          color: #666;
          background: #f0f0f0;
          padding: 0.25rem;
          border-radius: 3px;
          display: inline-block;
        }
      `}</style>
    </div>
  );
}