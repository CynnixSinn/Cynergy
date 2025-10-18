"""
Evaluation module for Cynergy
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import json


@dataclass
class EvaluationResult:
    """Result of a single evaluation"""
    id: str
    success: bool
    score: float
    details: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class EvaluationBenchmark:
    """Definition of an evaluation benchmark"""
    name: str
    description: str
    tasks: List[Dict[str, Any]]
    success_threshold: float = 0.7


class Evaluator:
    """Main evaluator class"""
    
    def __init__(self):
        self.results: List[EvaluationResult] = []
    
    async def run_task(self, agent, task: Dict[str, Any]) -> EvaluationResult:
        """Run a single evaluation task"""
        task_id = task.get("id", "unknown")
        expected = task.get("expected", "")
        input_prompt = task.get("input", "")
        
        try:
            # Run the agent with the input
            result = await agent.run(input_prompt)
            
            # Simple string comparison for demo purposes
            # In a real system, this would be more sophisticated
            score = 0.0
            if expected.lower() in result.lower():
                score = 1.0
            elif len(expected) > 0:
                # Simple similarity check
                common_chars = len(set(result.lower()) & set(expected.lower()))
                max_chars = max(len(result), len(expected))
                score = common_chars / max_chars if max_chars > 0 else 0
            
            success = score >= task.get("threshold", 0.5)
            
            return EvaluationResult(
                id=task_id,
                success=success,
                score=score,
                details={
                    "input": input_prompt,
                    "expected": expected,
                    "actual": result,
                    "threshold": task.get("threshold", 0.5)
                }
            )
        except Exception as e:
            return EvaluationResult(
                id=task_id,
                success=False,
                score=0.0,
                details={"input": input_prompt, "expected": expected},
                error=str(e)
            )
    
    async def run_benchmark(self, agent, benchmark: EvaluationBenchmark) -> List[EvaluationResult]:
        """Run an entire benchmark against an agent"""
        results = []
        
        for task in benchmark.tasks:
            result = await self.run_task(agent, task)
            results.append(result)
            
            # Small delay to avoid overwhelming the agent
            await asyncio.sleep(0.1)
        
        self.results.extend(results)
        return results
    
    def calculate_overall_score(self, results: List[EvaluationResult]) -> float:
        """Calculate the overall score for a set of results"""
        if not results:
            return 0.0
        
        total_score = sum(result.score for result in results)
        return total_score / len(results)
    
    def generate_report(self, results: List[EvaluationResult], benchmark_name: str) -> str:
        """Generate a human-readable report"""
        overall_score = self.calculate_overall_score(results)
        passed = sum(1 for r in results if r.success)
        total = len(results)
        
        report = f"Evaluation Report: {benchmark_name}\n"
        report += f"Overall Score: {overall_score:.2f} ({passed}/{total} tasks passed)\n\n"
        
        for result in results:
            status = "PASS" if result.success else "FAIL"
            report += f"Task {result.id}: {status} (Score: {result.score:.2f})\n"
            if result.error:
                report += f"  Error: {result.error}\n"
            report += "\n"
        
        return report