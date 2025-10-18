"""
Observability and tracing module for Cynergy
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import uuid


@dataclass
class TraceSpan:
    """A single span in a trace"""
    id: str
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent_id: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class Trace:
    """A complete trace of an agent execution"""
    id: str
    session_id: str
    spans: List[TraceSpan] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class Tracer:
    """Main tracer class for collecting traces"""
    
    def __init__(self):
        self.traces: Dict[str, Trace] = {}
        self.active_spans: Dict[str, TraceSpan] = {}
    
    def start_trace(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> Trace:
        """Start a new trace for a session"""
        trace_id = str(uuid.uuid4())
        trace = Trace(
            id=trace_id,
            session_id=session_id,
            metadata=metadata or {}
        )
        self.traces[trace_id] = trace
        return trace
    
    def start_span(self, name: str, trace_id: str, parent_id: Optional[str] = None) -> TraceSpan:
        """Start a new span within a trace"""
        span_id = str(uuid.uuid4())
        span = TraceSpan(
            id=span_id,
            name=name,
            start_time=datetime.now(),
            parent_id=parent_id
        )
        
        # Add span to the trace
        if trace_id in self.traces:
            self.traces[trace_id].spans.append(span)
        
        self.active_spans[span_id] = span
        return span
    
    def end_span(self, span_id: str):
        """End a span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.end_time = datetime.now()
            del self.active_spans[span_id]
    
    def add_event_to_span(self, span_id: str, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to a span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            event = {
                "name": name,
                "timestamp": datetime.now(),
                "attributes": attributes or {}
            }
            span.events.append(event)
    
    def end_trace(self, trace_id: str):
        """End a trace"""
        if trace_id in self.traces:
            self.traces[trace_id].end_time = datetime.now()
    
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID"""
        return self.traces.get(trace_id)
    
    def get_traces_for_session(self, session_id: str) -> List[Trace]:
        """Get all traces for a session"""
        return [trace for trace in self.traces.values() if trace.session_id == session_id]
    
    def export_trace_json(self, trace_id: str) -> str:
        """Export a trace as JSON"""
        trace = self.get_trace(trace_id)
        if not trace:
            return json.dumps({})
        
        # Convert datetime objects to ISO format strings for JSON serialization
        trace_dict = {
            "id": trace.id,
            "session_id": trace.session_id,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "metadata": trace.metadata,
            "spans": []
        }
        
        for span in trace.spans:
            span_dict = {
                "id": span.id,
                "name": span.name,
                "start_time": span.start_time.isoformat(),
                "end_time": span.end_time.isoformat() if span.end_time else None,
                "parent_id": span.parent_id,
                "attributes": span.attributes,
                "events": []
            }
            
            for event in span.events:
                event_dict = {
                    "name": event["name"],
                    "timestamp": event["timestamp"].isoformat(),
                    "attributes": event["attributes"]
                }
                span_dict["events"].append(event_dict)
            
            trace_dict["spans"].append(span_dict)
        
        return json.dumps(trace_dict, indent=2)
    
    def list_traces(self) -> List[Dict[str, Any]]:
        """List all traces with basic info"""
        traces_info = []
        for trace_id, trace in self.traces.items():
            traces_info.append({
                "id": trace_id,
                "session_id": trace.session_id,
                "start_time": trace.start_time.isoformat(),
                "end_time": trace.end_time.isoformat() if trace.end_time else None,
                "span_count": len(trace.spans),
                "metadata": trace.metadata
            })
        return traces_info


# Global tracer instance
global_tracer = Tracer()


def get_tracer() -> Tracer:
    """Get the global tracer instance"""
    return global_tracer