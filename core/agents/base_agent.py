from core.agents.llm_client import LLMClient

class BaseAgent:
    """
    The BaseAgent defines the common structure for all specialized AI agents.
    This adheres to the Open/Closed Principle (SOLID): we can add new agents
    without modifying this base class.
    """
    
    def __init__(self, llm_client: LLMClient = None):
        """
        Args:
            llm_client (LLMClient): An instance of our Gemini client. 
                                    If None, a new one is instantiated.
        """
        self.llm = llm_client or LLMClient()
        self.system_instruction = "You are a helpful AI coding assistant."
        self.focus_areas = []
        
    def analyze(self, code_snippet: str) -> str:
        """
        The core method that all agents must implement or inherit.
        
        Args:
            code_snippet (str): The code to be analyzed.
            
        Returns:
            str: The AI's analysis as a JSON string.
        """
        focus_areas_str = f"Focus on these areas: {', '.join(self.focus_areas)}" if getattr(self, 'focus_areas', None) else ""
        prompt = f"""You are an expert code reviewer analyzing Python code.

{self.system_instruction}
{focus_areas_str}

CODE TO REVIEW:
```python
{code_snippet}
```

ANALYZE THE CODE AND RESPOND WITH ONLY THIS JSON FORMAT:

{{
  "summary": "1-2 sentence assessment of overall code quality",
  "severity_level": "low",
  "issues": [
    {{
      "type": "bug",
      "line": "line number or location",
      "issue": "Clear description of the problem",
      "impact": "Why this matters and potential consequences",
      "suggestion": "Specific fix with code example"
    }}
  ],
  "improvements": [
    {{
      "area": "readability",
      "current": "Current implementation",
      "suggestion": "Better approach and why",
      "priority": "high"
    }}
  ],
  "positive_aspects": [
    "Well-structured code",
    "Good error handling"
  ],
  "estimated_risk": "low"
}}

STRICT RULES:
✓ severity_level: MUST be "low", "medium", or "high"
✓ type: MUST be "bug", "security", "performance", "style", or "readability"
✓ priority: MUST be "low", "medium", or "high"
✓ ALL arrays must be present (use [] if empty)
✓ Issues: maximum 8 items
✓ Improvements: maximum 5 items
✓ positive_aspects: maximum 5 items
✓ RESPOND ONLY WITH JSON
✓ NO MARKDOWN CODE BLOCKS
✓ NO PREAMBLE OR EXPLANATION

BEGIN RESPONSE WITH {{ IMMEDIATELY - NO INTRO TEXT"""
        response = self.llm.generate_response("You are an expert code reviewer. Output only JSON.", prompt)
        
        # Cleanup potential markdown backticks that the model might add despite instructions
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
            
        return response.strip()
