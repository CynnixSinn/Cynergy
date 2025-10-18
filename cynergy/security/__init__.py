"""
Security module for Cynergy with policy enforcement
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging


logger = logging.getLogger(__name__)


class PolicyType(Enum):
    SECURITY = "security"
    RATE_LIMIT = "rate_limit"
    PERMISSION = "permission"
    COMPLIANCE = "compliance"


@dataclass
class PolicyResult:
    allowed: bool
    reason: str
    metadata: Dict[str, Any] = None


class BasePolicy:
    """Base class for all policies"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    async def evaluate(self, context: Dict[str, Any]) -> PolicyResult:
        """Evaluate policy against context"""
        raise NotImplementedError


class RateLimitPolicy(BasePolicy):
    """Rate limiting policy"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.requests_per_minute = config.get("requests_per_minute", 10)
        self.window_size = config.get("window_size", 60)  # seconds
        self.requests: Dict[str, int] = {}
        self.reset_times: Dict[str, float] = {}
    
    async def evaluate(self, context: Dict[str, Any]) -> PolicyResult:
        agent_id = context.get("agent_id", "unknown")
        current_time = asyncio.get_event_loop().time()
        
        # Reset counter if window has passed
        if agent_id not in self.reset_times or current_time > self.reset_times[agent_id] + self.window_size:
            self.requests[agent_id] = 0
            self.reset_times[agent_id] = current_time
        
        # Check if limit is exceeded
        if self.requests.get(agent_id, 0) >= self.requests_per_minute:
            return PolicyResult(
                allowed=False,
                reason=f"Rate limit exceeded for agent {agent_id}. Max {self.requests_per_minute} requests per minute."
            )
        
        # Increment counter
        self.requests[agent_id] = self.requests.get(agent_id, 0) + 1
        
        return PolicyResult(allowed=True, reason="Rate limit check passed")


class SecurityPolicy(BasePolicy):
    """Security policy for blocking malicious operations"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.blocked_operations = config.get("blocked_operations", [
            "eval", "exec", "__import__", "open", "subprocess"
        ])
    
    async def evaluate(self, context: Dict[str, Any]) -> PolicyResult:
        operation = context.get("operation", "")
        
        # Check for blocked operations in the operation string
        for blocked in self.blocked_operations:
            if blocked.lower() in operation.lower():
                return PolicyResult(
                    allowed=False,
                    reason=f"Blocked operation detected: {blocked}"
                )
        
        return PolicyResult(allowed=True, reason="Security check passed")


class PolicyEngine:
    """Main policy engine that manages and executes policies"""
    
    def __init__(self):
        self.policies: Dict[str, BasePolicy] = {}
    
    def add_policy(self, policy: BasePolicy):
        """Add a policy to the engine"""
        self.policies[policy.name] = policy
        logger.info(f"Added policy: {policy.name}")
    
    def remove_policy(self, name: str):
        """Remove a policy from the engine"""
        if name in self.policies:
            del self.policies[name]
            logger.info(f"Removed policy: {name}")
    
    async def evaluate(self, context: Dict[str, Any]) -> PolicyResult:
        """Evaluate all policies against context"""
        for name, policy in self.policies.items():
            result = await policy.evaluate(context)
            if not result.allowed:
                logger.warning(f"Policy {name} blocked request: {result.reason}")
                return result
        
        return PolicyResult(allowed=True, reason="All policies passed")