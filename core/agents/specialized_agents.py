from core.agents.base_agent import BaseAgent

class BugDetectionAgent(BaseAgent):
    """Specialized agent for finding logic errors and bugs."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are an expert Python debugger. Analyze the provided code and identify "
            "any logical errors, edge cases that are not handled, or potential runtime exceptions. "
            "If the code is perfectly fine, just say 'No bugs detected'."
        )
        self.focus_areas = ["Logic errors", "Edge cases", "Runtime exceptions", "Null/None checks"]

class SecurityReviewAgent(BaseAgent):
    """Specialized agent for finding security vulnerabilities."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are a Senior Security Engineer. Review the provided Python code for vulnerabilities "
            "such as SQL Injection, XSS, insecure deserialization, hardcoded secrets, or weak cryptography. "
            "Format your findings as a strict security audit."
        )
        self.focus_areas = ["SQL Injection", "XSS", "Insecure deserialization", "Hardcoded secrets", "Weak cryptography"]

class PerformanceOptimizationAgent(BaseAgent):
    """Specialized agent for optimizing code."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are a Performance Engineer. Analyze the Python code and suggest ways to make it faster "
            "or use less memory. Look for O(N^2) loops, unnecessary deep copies, or inefficient data structures."
        )
        self.focus_areas = ["Algorithmic complexity", "Memory usage", "Database query optimization", "Unnecessary copies"]

class DocumentationAgent(BaseAgent):
    """Specialized agent for generating clean English explanations and docstrings."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are a Technical Writer. Read the provided Python code and explain exactly what it does "
            "in plain English. Then, provide a perfectly formatted PEP 257 compliant docstring for it."
        )
        self.focus_areas = ["Code readability", "PEP 257 docstrings", "Variable naming", "Clear explanations"]

class TestGenerationAgent(BaseAgent):
    """Specialized agent for writing unit tests."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are a QA Automation Engineer. Write a comprehensive suite of `pytest` unit tests "
            "for the provided Python code. Include happy paths and edge cases."
        )
        self.focus_areas = ["Happy paths", "Edge cases", "Mocking external dependencies", "Test coverage"]

class RepositorySummarizationAgent(BaseAgent):
    """Specialized agent for high-level repository overviews."""
    def __init__(self, llm_client=None):
        super().__init__(llm_client)
        self.system_instruction = (
            "You are a Principal Software Architect. I will provide you with a list of core files "
            "and their summaries from a repository. Please write a highly professional, 2-paragraph "
            "executive summary of what this entire project does."
        )
        
    def summarize_repo(self, repo_context: str) -> str:
        prompt = f"Here is the context of the repository:\n\n{repo_context}"
        return self.llm.generate_response(self.system_instruction, prompt)
