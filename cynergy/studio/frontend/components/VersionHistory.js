// components/VersionHistory.js
import { useState, useEffect } from 'react';
import { getWorkflowVersions, revertWorkflowVersion } from '../api/workflowApi';

export function VersionHistory({ workflowId, currentVersion }) {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (workflowId) {
      fetchVersions();
    }
  }, [workflowId]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const data = await getWorkflowVersions(workflowId);
      setVersions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRevert = async (versionNumber) => {
    if (window.confirm(`Are you sure you want to revert to version ${versionNumber}?`)) {
      try {
        await revertWorkflowVersion(workflowId, versionNumber);
        // Refresh the versions list after revert
        fetchVersions();
        alert(`Successfully reverted to version ${versionNumber}`);
      } catch (err) {
        setError(err.message);
      }
    }
  };

  if (loading) return <div className="loading">Loading versions...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="version-history">
      <h3>Version History</h3>
      <div className="version-list">
        {versions.map((version) => (
          <div key={version.id} className="version-item">
            <div className="version-info">
              <span className="version-number">v{version.version_number}</span>
              <span className="version-date">{new Date(version.created_at).toLocaleString()}</span>
            </div>
            <div className="version-actions">
              {version.version_number !== currentVersion && (
                <button 
                  className="btn-secondary" 
                  onClick={() => handleRevert(version.version_number)}
                >
                  Revert
                </button>
              )}
              {version.version_number === currentVersion && (
                <span className="current-marker">Current</span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <style jsx>{`
        .version-history {
          padding: 1rem;
          border: 1px solid #ddd;
          border-radius: 6px;
          background: #f9f9f9;
        }
        
        .version-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        
        .version-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background: white;
          border: 1px solid #eee;
          border-radius: 4px;
        }
        
        .version-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .version-number {
          font-weight: 600;
          color: #333;
        }
        
        .version-date {
          font-size: 0.75rem;
          color: #666;
        }
        
        .version-actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .btn-secondary {
          padding: 0.25rem 0.75rem;
          background: #6c757d;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.75rem;
        }
        
        .btn-secondary:hover {
          background: #545b62;
        }
        
        .current-marker {
          background: #e8f5e9;
          color: #388e3c;
          padding: 0.25rem 0.75rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 500;
        }
        
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