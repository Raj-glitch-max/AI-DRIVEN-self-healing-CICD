import os
import openai
import time
import logging
from typing import Dict, Any, Optional
from .config import config

logger = logging.getLogger(__name__)

class LLMClient:
    """Enhanced LLM client with retry logic and better error handling"""
    
    def __init__(self):
        self.api_key = config.openai_api_key
        self.model = config.openai_model
        self.max_retries = config.max_retry_attempts
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Please set OPENAI_API_KEY environment variable.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info(f"LLM Client initialized with model: {self.model}")

    def get_fix(self, file_content: str, error_info: Dict[str, Any]) -> str:
        """
        Sends the code and error info to the LLM and returns the fixed code.
        Includes retry logic and enhanced prompting.
        """
        prompt = self._build_fix_prompt(file_content, error_info)
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Requesting fix from LLM (attempt {attempt + 1}/{self.max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": self._get_system_prompt()
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.1,  # Lower temperature for more consistent fixes
                    max_tokens=2000
                )
                
                fixed_code = response.choices[0].message.content.strip()
                fixed_code = self._clean_response(fixed_code)
                
                logger.info("Successfully received fix from LLM")
                return fixed_code
                
            except openai.RateLimitError as e:
                logger.warning(f"Rate limit hit, waiting before retry: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except openai.APIError as e:
                logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Unexpected error communicating with LLM: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
        
        raise Exception(f"Failed to get fix from LLM after {self.max_retries} attempts")

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM"""
        return """You are an expert Python developer and debugging specialist. 
Your task is to analyze failing code and provide precise fixes.

Rules:
1. Return ONLY the complete fixed file content
2. Do not include markdown formatting or code blocks
3. Preserve all existing functionality while fixing the specific error
4. Make minimal changes - only fix what's broken
5. Ensure the fix is syntactically correct and follows Python best practices
6. If the error is in a test, fix the test logic, not the implementation (unless the implementation is clearly wrong)"""

    def _build_fix_prompt(self, file_content: str, error_info: Dict[str, Any]) -> str:
        """Build a comprehensive prompt for the LLM"""
        return f"""
TASK: Fix the failing code

FILE PATH: {error_info.get('file_path', 'Unknown')}
LINE NUMBER: {error_info.get('line_number', 'Unknown')}
ERROR MESSAGE: {error_info.get('error_message', 'Unknown error')}

CURRENT FILE CONTENT:
{file_content}

ANALYSIS CONTEXT:
- This is part of a CI/CD pipeline that failed
- The error occurred during automated testing
- Focus on fixing the specific assertion or logic error
- Maintain backward compatibility with existing code

Please provide the complete fixed file content:
"""

    def _clean_response(self, response: str) -> str:
        """Clean up the LLM response to extract just the code"""
        # Remove common markdown formatting
        if response.startswith("```python"):
            response = response.replace("```python", "", 1)
        if response.startswith("```"):
            response = response.replace("```", "", 1)
        if response.endswith("```"):
            response = response[:-3]
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        # Validate that we have actual Python code
        if not response or len(response.split('\n')) < 2:
            raise ValueError("LLM returned invalid or empty code")
        
        return response

    def analyze_error(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze complex error logs"""
        prompt = f"""
Analyze this test failure log and extract key information:

LOG CONTENT:
{log_content}

Please identify:
1. The failing file path
2. The specific error message
3. The line number where the error occurred
4. The type of error (assertion, syntax, import, etc.)
5. A brief explanation of what went wrong

Return your analysis in this exact JSON format:
{{
    "file_path": "path/to/file.py",
    "error_message": "specific error message",
    "line_number": 123,
    "error_type": "assertion|syntax|import|runtime",
    "explanation": "brief explanation of the issue"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a log analysis expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content.strip())
            logger.info("LLM successfully analyzed error log")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze error with LLM: {e}")
            return None
