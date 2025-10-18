// api/workflowApi.js
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getWorkflows() {
  const response = await fetch(`${API_BASE_URL}/api/workflows`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getWorkflow(workflowId) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function saveWorkflow(workflow) {
  const response = await fetch(`${API_BASE_URL}/api/workflows`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(workflow),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function simulateWorkflow(request) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/simulate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function executeWorkflow(request) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/execute`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getWorkflowVersions(workflowId) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}/versions`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function getWorkflowVersion(workflowId, versionNumber) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}/versions/${versionNumber}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}

export async function revertWorkflowVersion(workflowId, versionNumber) {
  const response = await fetch(`${API_BASE_URL}/api/workflows/${workflowId}/revert/${versionNumber}`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}