// components/WorkflowList.js
import { useState, useEffect } from 'react';
import { getWorkflows } from '../api/workflowApi';

export function WorkflowList({ onWorkflowSelect, selectedWorkflow }) {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await getWorkflows();
      setWorkflows(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkflow = () => {
    // For now, creating a new empty workflow
    const newWorkflow = {
      id: `wf_${Date.now()}`,
      name: 'New Workflow',
      description: 'A new workflow',
      nodes: [],
      edges: [],
      version: '1.0',
      status: 'draft'
    };
    
    setWorkflows([...workflows, newWorkflow]);
    onWorkflowSelect(newWorkflow);
  };

  if (loading) return <div className="loading">Loading workflows...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="workflow-list">
      <div className="workflow-actions">
        <button onClick={handleCreateWorkflow} className="btn-primary">
          + New Workflow
        </button>
      </div>
      
      <div className="workflow-items">
        {workflows.map(workflow => (
          <div 
            key={workflow.id} 
            className={`workflow-item ${selectedWorkflow?.id === workflow.id ? 'selected' : ''}`}
            onClick={() => onWorkflowSelect(workflow)}
          >
            <div className="workflow-info">
              <h3>{workflow.name}</h3>
              <p>{workflow.description}</p>
              <div className="workflow-meta">
                <span className="version">v{workflow.version}</span>
                <span className={`status status-${workflow.status}`}>{workflow.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <style jsx>{`
        .workflow-list {
          padding: 1rem;
        }
        
        .workflow-actions {
          margin-bottom: 1rem;
        }
        
        .btn-primary {
          width: 100%;
          padding: 0.75rem;
          background: #007acc;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
        
        .btn-primary:hover {
          background: #005a9e;
        }
        
        .workflow-items {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        
        .workflow-item {
          padding: 1rem;
          border: 1px solid #ddd;
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .workflow-item:hover {
          border-color: #007acc;
          box-shadow: 0 2px 6px rgba(0, 122, 204, 0.15);
        }
        
        .workflow-item.selected {
          border-color: #007acc;
          background-color: #f0f8ff;
        }
        
        .workflow-info h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1rem;
          color: #333;
        }
        
        .workflow-info p {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          color: #666;
          line-height: 1.4;
        }
        
        .workflow-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: #888;
        }
        
        .status {
          padding: 0.125rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
        }
        
        .status-draft { background: #e3f2fd; color: #1976d2; }
        .status-active { background: #e8f5e9; color: #388e3c; }
        .status-archived { background: #f5f5f5; color: #757575; }
        .status-failed { background: #ffebee; color: #d32f2f; }
        
        .loading, .error {
          padding: 1rem;
          text-align: center;
          color: #666;
        }
        
        .error {
          color: #d32f2f;
        }
      `}</style>
    </div>
  );
}