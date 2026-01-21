import re

class LogParser:
    @staticmethod
    def parse_failure(log_content):
        """
        Parses the log content to find the specific test failure.
        Returns a dictionary with file_path, line_number, and error_message.
        """
        # Regex to find pytest failures
        # Example: E       assert 4 == 5
        #          tests/test_main.py:24: AssertionError
        
        failure_pattern = re.compile(r"(E\s+.*)\n.*\n(.*):(\d+): (AssertionError|Error)")
        
        match = failure_pattern.search(log_content)
        if match:
            error_details = match.group(1).strip()
            file_path = match.group(2).strip()
            line_number = int(match.group(3).strip())
            
            return {
                "file_path": file_path,
                "line_number": line_number,
                "error_message": error_details,
                "full_context": log_content[-2000:] # Last 2000 chars for context
            }
        return None
