// pages/index.js - Main Studio page with workflow designer
import { useState, useCallback } from 'react';
import { WorkflowDesigner } from '../components/WorkflowDesigner';
import { WorkflowList } from '../components/WorkflowList';
import { SimulationPanel } from '../components/SimulationPanel';

export default function Studio() {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  const handleWorkflowSelect = (workflow) => {
    setSelectedWorkflow(workflow);
  };

  const handleSimulationStart = () => {
    setIsSimulating(true);
  };

  const handleSimulationComplete = (result) => {
    setSimulationResult(result);
    setIsSimulating(false);
  };

  return (
    <div className="studio-container">
      <header className="studio-header">
        <h1>🔥 Cynergy Studio</h1>
        <p>Design and orchestrate agentic AI workflows</p>
      </header>
      
      <div className="studio-layout">
        <div className="workflow-sidebar">
          <WorkflowList 
            onWorkflowSelect={handleWorkflowSelect} 
            selectedWorkflow={selectedWorkflow}
          />
        </div>
        
        <div className="workflow-main">
          {selectedWorkflow ? (
            <WorkflowDesigner 
              workflow={selectedWorkflow} 
              onSimulationStart={handleSimulationStart}
            />
          ) : (
            <div className="empty-state">
              <h2>Select or Create a Workflow</h2>
              <p>Choose an existing workflow from the list or create a new one to get started.</p>
            </div>
          )}
        </div>
      </div>
      
      {isSimulating && (
        <div className="simulation-overlay">
          <SimulationPanel 
            workflow={selectedWorkflow}
            onSimulationComplete={handleSimulationComplete}
          />
        </div>
      )}
      
      <style jsx global>{`
        .studio-container {
          height: 100vh;
          display: flex;
          flex-direction: column;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
        }
        
        .studio-header {
          background: #1a1a1a;
          color: white;
          padding: 1rem 2rem;
          border-bottom: 1px solid #333;
        }
        
        .studio-header h1 {
          margin: 0;
          font-size: 1.5rem;
        }
        
        .studio-layout {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .workflow-sidebar {
          width: 300px;
          border-right: 1px solid #e0e0e0;
          background: #f8f9fa;
          overflow-y: auto;
        }
        
        .workflow-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: relative;
        }
        
        .empty-state {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: #666;
          text-align: center;
        }
        
        .empty-state h2 {
          margin-bottom: 1rem;
          color: #333;
        }
        
        .simulation-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.7);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  );
}