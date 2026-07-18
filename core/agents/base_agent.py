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
        
    def analyze(self, code_snippet: str) -> str:
        """
        The core method that all agents must implement or inherit.
        
        Args:
            code_snippet (str): The code to be analyzed.
            
        Returns:
            str: The AI's analysis.
        """
        prompt = f"Please review the following code:\n\n```python\n{code_snippet}\n```"
        return self.llm.generate_response(self.system_instruction, prompt)
