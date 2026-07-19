import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables (e.g. GEMINI_API_KEY) from a .env file
load_dotenv()

class LLMClient:
    """
    A wrapper around the Google Generative AI SDK (Gemini 2.5 Pro).
    This handles authentication and the generation of text using the LLM.
    """
    
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set in the environment. LLM calls will fail.")
            
        # Configure the Gemini SDK
        genai.configure(api_key=api_key)
        
        # Instantiate the model. We specify Gemini 2.5 Pro for advanced reasoning.
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"Initialized LLMClient with model: {model_name}")

    def generate_response(self, system_instruction: str, prompt: str) -> str:
        """
        Generates a response from the LLM.
        
        Args:
            system_instruction (str): The 'persona' or rules the AI should follow.
            prompt (str): The actual user query or code snippet to analyze.
            
        Returns:
            str: The AI's response text.
        """
        # We can simulate system instructions in Gemini by prepending them,
        # or by using specific model configurations if the API version supports it directly.
        # For simplicity and compatibility, we combine them clearly.
        full_prompt = f"SYSTEM INSTRUCTION:\n{system_instruction}\n\nUSER PROMPT:\n{prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return f"Error analyzing code: {str(e)}"
