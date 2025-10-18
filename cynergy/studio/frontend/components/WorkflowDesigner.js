// components/WorkflowDesigner.js
import React, { useState, useCallback, useRef } from 'react';
import ReactFlow, {
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MiniMap,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { CustomNode } from './CustomNode';
import { VersionHistory } from './VersionHistory';

// Define node types for React Flow
const nodeTypes = {
  agent: CustomNode,
  conditional: CustomNode,
  loop: CustomNode,
  task: CustomNode,
};

export function WorkflowDesigner({ workflow, onSimulationStart }) {
  const [nodes, setNodes, onNodesChange] = useNodesState(workflow.nodes.map(n => ({
    id: n.id,
    type: n.type,
    position: { x: n.position_x || 0, y: n.position_y || 0 },
    data: { 
      label: n.name, 
      type: n.type,
      config: n.agent_config || {}
    },
  })));
  
  const [edges, setEdges, onEdgesChange] = useEdgesState(workflow.edges.map(e => ({
    id: e.id,
    source: e.source_id,
    target: e.target_id,
    animated: e.condition ? true : false,
    label: e.condition || undefined,
  })));
  
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodeConfig, setNodeConfig] = useState(null);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState(null);
  const connectingNodeId = useRef(null);

  const onConnect = useCallback(
    (params) => {
      setEdges((eds) => addEdge({ ...params, animated: true }, eds));
      
      // Add the new edge to the workflow
      const newEdge = {
        id: `edge_${Date.now()}`,
        source_id: params.source,
        target_id: params.target,
        condition: params.label || null,
      };
      
      // In a real implementation, we would update the workflow via API
    },
    [setEdges]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const newNode = {
        id: `node_${Date.now()}`,
        type,
        position,
        data: { label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node` },
      };

      setNodes((nds) => nds.concat(newNode));
      
      // In a real implementation, we would update the workflow via API
    },
    [reactFlowInstance, setNodes]
  );

  const handleNodeConfigOpen = (node) => {
    setNodeConfig(node);
  };

  const handleNodeConfigSave = (updatedNode) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === updatedNode.id ? { ...n, data: updatedNode.data } : n))
    );
    setNodeConfig(null);
  };

  const handleNodeConfigClose = () => {
    setNodeConfig(null);
  };

  const handleSimulation = () => {
    if (onSimulationStart) {
      onSimulationStart();
    }
  };

  return (
    <div className="workflow-designer">
      <div className="toolbar">
        <div className="node-palette">
          <h3>Node Palette</h3>
          <div 
            className="palette-item" 
            draggable
            onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'agent')}
          >
            Agent
          </div>
          <div 
            className="palette-item" 
            draggable
            onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'conditional')}
          >
            Conditional
          </div>
          <div 
            className="palette-item" 
            draggable
            onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'loop')}
          >
            Loop
          </div>
          <div 
            className="palette-item" 
            draggable
            onDragStart={(event) => event.dataTransfer.setData('application/reactflow', 'task')}
          >
            Task
          </div>
        </div>
        
        <div className="designer-actions">
          <button className="btn-secondary" onClick={handleSimulation}>
            ▶️ Simulate
          </button>
          <button className="btn-primary">
            💾 Save
          </button>
          <button 
            className="btn-info" 
            onClick={() => setShowVersionHistory(!showVersionHistory)}
          >
            📋 Versions
          </button>
        </div>
      </div>
      
      <div className="designer-content">
        <div className="reactflow-wrapper">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.5 }}
          >
            <Controls />
            <MiniMap />
            <Background gap={12} size={1} />
          </ReactFlow>
        </div>
        
        {showVersionHistory && (
          <div className="version-panel">
            <VersionHistory 
              workflowId={workflow.id} 
              currentVersion={workflow.version} 
            />
          </div>
        )}
      </div>
      
      {nodeConfig && (
        <NodeConfigModal 
          node={nodeConfig} 
          onSave={handleNodeConfigSave} 
          onClose={handleNodeConfigClose} 
        />
      )}
      
      <style jsx>{`
        .workflow-designer {
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        
        .toolbar {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem;
          background: #f8f9fa;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .node-palette {
          display: flex;
          gap: 0.5rem;
          align-items: center;
        }
        
        .node-palette h3 {
          margin: 0;
          font-size: 0.875rem;
          color: #666;
          margin-right: 1rem;
        }
        
        .palette-item {
          padding: 0.5rem 1rem;
          background: white;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: move;
          font-size: 0.875rem;
        }
        
        .palette-item:hover {
          background: #f0f0f0;
        }
        
        .designer-actions {
          display: flex;
          gap: 0.5rem;
        }
        
        .btn-primary, .btn-secondary, .btn-info {
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
        
        .btn-primary {
          background: #007acc;
          color: white;
        }
        
        .btn-primary:hover {
          background: #005a9e;
        }
        
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #545b62;
        }
        
        .btn-info {
          background: #17a2b8;
          color: white;
        }
        
        .btn-info:hover {
          background: #138496;
        }
        
        .designer-content {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .reactflow-wrapper {
          flex: 1;
          height: 100%;
        }
        
        .version-panel {
          width: 300px;
          border-left: 1px solid #e0e0e0;
          overflow-y: auto;
          padding: 1rem;
        }
      `}</style>
    </div>
  );
}

// Modal for configuring nodes
function NodeConfigModal({ node, onSave, onClose }) {
  const [name, setName] = useState(node.data.label);
  const [config, setConfig] = useState(node.data.config || {});

  const handleSave = () => {
    const updatedNode = {
      ...node,
      data: {
        ...node.data,
        label: name,
        config: config,
      }
    };
    onSave(updatedNode);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Configure Node</h3>
        <div className="form-group">
          <label>Name:</label>
          <input 
            type="text" 
            value={name} 
            onChange={(e) => setName(e.target.value)} 
          />
        </div>
        
        <div className="form-group">
          <label>Configuration:</label>
          <textarea
            value={JSON.stringify(config, null, 2)}
            onChange={(e) => setConfig(JSON.parse(e.target.value || '{}'))}
            rows="10"
            cols="50"
          />
        </div>
        
        <div className="modal-actions">
          <button className="btn-secondary" onClick={onClose}>Cancel</button>
          <button className="btn-primary" onClick={handleSave}>Save</button>
        </div>
      </div>
      
      <style jsx>{`
        .modal-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }
        
        .modal-content {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          width: 600px;
          max-width: 90vw;
          max-height: 90vh;
          overflow-y: auto;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-group label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .form-group input, .form-group textarea {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
        
        .modal-actions {
          display: flex;
          gap: 0.5rem;
          justify-content: flex-end;
          margin-top: 1rem;
        }
      `}</style>
    </div>
  );
}