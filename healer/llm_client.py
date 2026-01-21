import os
from openai import OpenAI

class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_fix(self, file_content, error_details):
        """
        Asks the LLM to fix the code based on the error.
        """
        prompt = f"""
        You are an expert Python developer. A unit test has failed.
        
        FILE CONTENT:
        ```python
        {file_content}
        ```
        
        ERROR DETAILS:
        {error_details['error_message']}
        at {error_details['file_path']}:{error_details['line_number']}
        
        TASK:
        Provide the corrected code for the ENTIRE file. 
        Do not change the logic of the test if the test is correct and the code is wrong. 
        However, if the test itself is clearly buggy (e.g., asserting 2+2=5), fix the test.
        
        OUTPUT FORMAT:
        Return ONLY the raw python code. No markdown formatting, no explanations.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an automated code repair agent."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
