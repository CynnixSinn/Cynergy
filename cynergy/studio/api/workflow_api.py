"""
API endpoints for the Cynergy Studio
"""
from fastapi import FastAPI, HTTPException
from typing import List, Optional
import json
from ..models.workflow import (
    WorkflowManifest, SimulationRequest, SimulationResponse, 
    ExecutionRequest, ExecutionResponse, TraceInfo, WorkflowVersion
)
from ..services.workflow_service import get_workflow_service


def create_app():
    app = FastAPI(title="Cynergy Studio API", version="0.2.0")
    workflow_service = get_workflow_service()
    
    @app.get("/")
    async def root():
        return {"message": "Cynergy Studio API"}
    
    @app.get("/api/workflows", response_model=List[WorkflowManifest])
    async def list_workflows():
        """List all workflows"""
        return workflow_service.list_workflows()
    
    @app.get("/api/workflows/{workflow_id}", response_model=WorkflowManifest)
    async def get_workflow(workflow_id: str):
        """Get a specific workflow"""
        workflow = workflow_service.get_workflow(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    
    @app.post("/api/workflows", response_model=WorkflowManifest)
    async def save_workflow(manifest: WorkflowManifest):
        """Save or update a workflow"""
        try:
            return workflow_service.save_workflow(manifest)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/workflows/{workflow_id}/versions", response_model=List[WorkflowVersion])
    async def get_workflow_versions(workflow_id: str):
        """Get all versions of a workflow"""
        return workflow_service.get_workflow_versions(workflow_id)
    
    @app.get("/api/workflows/{workflow_id}/versions/{version_number}", response_model=WorkflowVersion)
    async def get_workflow_version(workflow_id: str, version_number: str):
        """Get a specific version of a workflow"""
        version = workflow_service.get_workflow_version(workflow_id, version_number)
        if not version:
            raise HTTPException(status_code=404, detail="Workflow version not found")
        return version
    
    @app.post("/api/workflows/{workflow_id}/revert/{version_number}", response_model=WorkflowManifest)
    async def revert_workflow_version(workflow_id: str, version_number: str):
        """Revert a workflow to a specific version"""
        result = workflow_service.revert_to_version(workflow_id, version_number)
        if not result:
            raise HTTPException(status_code=404, detail="Workflow or version not found")
        return result
    
    @app.post("/api/workflows/simulate", response_model=SimulationResponse)
    async def simulate_workflow(request: SimulationRequest):
        """Simulate a workflow execution"""
        try:
            return workflow_service.simulate_workflow(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/api/workflows/execute", response_model=ExecutionResponse)
    async def execute_workflow(request: ExecutionRequest):
        """Execute a workflow"""
        try:
            return workflow_service.execute_workflow(request)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/api/traces/{session_id}", response_model=TraceInfo)
    async def get_trace(session_id: str):
        """Get trace information for a session"""
        trace = workflow_service.get_trace(session_id)
        if not trace:
            raise HTTPException(status_code=404, detail="Trace not found")
        return trace
    
    return app


# For backward compatibility
app = create_app()