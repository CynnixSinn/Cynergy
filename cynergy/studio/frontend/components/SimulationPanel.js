// components/SimulationPanel.js
import { useState, useEffect } from 'react';
import { simulateWorkflow } from '../api/workflowApi';

export function SimulationPanel({ workflow, onSimulationComplete }) {
  const [inputData, setInputData] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState(null);
  const [trace, setTrace] = useState(null);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    try {
      // Parse input data as JSON if possible
      let parsedInput = inputData;
      try {
        parsedInput = JSON.parse(inputData);
      } catch (e) {
        // If it's not JSON, treat as a string
        parsedInput = { input: inputData };
      }

      const request = {
        workflow_id: workflow.id,
        input_data: parsedInput,
        simulate_tracing: true
      };

      const response = await simulateWorkflow(request);
      setResult(response);
      setTrace(response.trace);
      onSimulationComplete(response);
    } catch (error) {
      console.error('Simulation error:', error);
      setResult({ error: error.message });
    } finally {
      setIsRunning(false);
    }
  };

  const handleCancel = () => {
    onSimulationComplete(null);
  };

  return (
    <div className="simulation-panel">
      <div className="panel-content">
        <h3>Workflow Simulation</h3>
        
        <div className="simulation-input">
          <label>Input Data (JSON):</label>
          <textarea
            value={inputData}
            onChange={(e) => setInputData(e.target.value)}
            placeholder='{"query": "customer needs help", "priority": "high"}'
            rows="4"
          />
        </div>
        
        <div className="simulation-actions">
          <button 
            className="btn-primary" 
            onClick={handleRunSimulation}
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : 'Run Simulation'}
          </button>
          <button className="btn-secondary" onClick={handleCancel}>
            Cancel
          </button>
        </div>
        
        {result && (
          <div className="simulation-result">
            <h4>Result:</h4>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        )}
        
        {trace && (
          <div className="simulation-trace">
            <h4>Execution Trace:</h4>
            <pre>{JSON.stringify(trace, null, 2)}</pre>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .simulation-panel {
          width: 90%;
          height: 80%;
          max-width: 1200px;
          background: white;
          border-radius: 8px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
        }
        
        .panel-content {
          padding: 1.5rem;
          flex: 1;
          overflow-y: auto;
        }
        
        .simulation-input {
          margin-bottom: 1.5rem;
        }
        
        .simulation-input label {
          display: block;
          margin-bottom: 0.5rem;
          font-weight: 500;
        }
        
        .simulation-input textarea {
          width: 100%;
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-family: monospace;
          font-size: 0.875rem;
        }
        
        .simulation-actions {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1.5rem;
        }
        
        .btn-primary, .btn-secondary {
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
        
        .btn-primary:hover:not(:disabled) {
          background: #005a9e;
        }
        
        .btn-primary:disabled {
          background: #cccccc;
          cursor: not-allowed;
        }
        
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #545b62;
        }
        
        .simulation-result, .simulation-trace {
          margin-top: 1.5rem;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 4px;
          border-left: 3px solid #007acc;
        }
        
        .simulation-result h4, .simulation-trace h4 {
          margin-top: 0;
          color: #333;
        }
        
        pre {
          white-space: pre-wrap;
          word-break: break-word;
          font-size: 0.8rem;
          line-height: 1.4;
          max-height: 300px;
          overflow-y: auto;
        }
      `}</style>
    </div>
  );
}