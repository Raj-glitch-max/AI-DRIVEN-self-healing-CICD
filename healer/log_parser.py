import re
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class LogParser:
    """Enhanced log parser with support for multiple test frameworks and error types"""
    
    def __init__(self):
        self.patterns = {
            'pytest': {
                'file_pattern': re.compile(r"^([\w/]+\.py):(\d+):", re.MULTILINE),
                'error_patterns': [
                    re.compile(r"E\s+(.+)"),  # Standard pytest error
                    re.compile(r">\s+(.+)"),  # Code line that failed
                    re.compile(r"AssertionError:\s*(.+)"),  # Assertion errors
                    re.compile(r"(\w+Error):\s*(.+)")  # General Python errors
                ]
            },
            'unittest': {
                'file_pattern': re.compile(r'File "([^"]+)", line (\d+)'),
                'error_patterns': [
                    re.compile(r"AssertionError:\s*(.+)"),
                    re.compile(r"(\w+Error):\s*(.+)")
                ]
            }
        }

    def parse_failure(self, log_content: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced parsing that handles multiple test frameworks and error types.
        Returns a dict with 'file_path', 'error_message', 'line_number', and 'error_type'.
        """
        logger.info("Parsing log content for failures")
        
        # Try pytest format first (most common)
        error_info = self._parse_pytest_failure(log_content)
        if error_info:
            logger.info(f"Found pytest failure: {error_info}")
            return error_info
        
        # Try unittest format
        error_info = self._parse_unittest_failure(log_content)
        if error_info:
            logger.info(f"Found unittest failure: {error_info}")
            return error_info
        
        # Try generic Python error format
        error_info = self._parse_generic_failure(log_content)
        if error_info:
            logger.info(f"Found generic failure: {error_info}")
            return error_info
        
        logger.warning("No parseable error found in logs")
        return None

    def _parse_pytest_failure(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Parse pytest-specific failure format"""
        patterns = self.patterns['pytest']
        
        # Find file and line number
        file_match = patterns['file_pattern'].search(log_content)
        if not file_match:
            return None
        
        file_path = file_match.group(1)
        line_number = int(file_match.group(2))
        
        # Extract error information
        error_info = {
            'file_path': file_path,
            'line_number': line_number,
            'error_type': 'pytest',
            'framework': 'pytest'
        }
        
        # Find the most relevant error message
        lines = log_content.split('\n')
        error_messages = []
        
        for line in lines:
            for pattern in patterns['error_patterns']:
                match = pattern.search(line.strip())
                if match:
                    if len(match.groups()) == 1:
                        error_messages.append(match.group(1))
                    else:
                        error_messages.append(f"{match.group(1)}: {match.group(2)}")
        
        # Choose the most descriptive error message
        if error_messages:
            # Prefer assertion errors, then specific errors, then generic
            assertion_errors = [msg for msg in error_messages if 'assert' in msg.lower()]
            if assertion_errors:
                error_info['error_message'] = assertion_errors[0]
                error_info['error_type'] = 'assertion'
            else:
                error_info['error_message'] = error_messages[0]
        else:
            error_info['error_message'] = "Test failure detected"
        
        return error_info

    def _parse_unittest_failure(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Parse unittest-specific failure format"""
        patterns = self.patterns['unittest']
        
        file_match = patterns['file_pattern'].search(log_content)
        if not file_match:
            return None
        
        return {
            'file_path': file_match.group(1),
            'line_number': int(file_match.group(2)),
            'error_message': self._extract_error_message(log_content, patterns['error_patterns']),
            'error_type': 'unittest',
            'framework': 'unittest'
        }

    def _parse_generic_failure(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Parse generic Python error format"""
        # Look for traceback information
        traceback_pattern = re.compile(r'File "([^"]+)", line (\d+).*\n.*\n\s*(\w+Error.*)', re.MULTILINE)
        match = traceback_pattern.search(log_content)
        
        if match:
            return {
                'file_path': match.group(1),
                'line_number': int(match.group(2)),
                'error_message': match.group(3),
                'error_type': 'runtime',
                'framework': 'generic'
            }
        
        return None

    def _extract_error_message(self, log_content: str, error_patterns: List[re.Pattern]) -> str:
        """Extract the most relevant error message from log content"""
        for pattern in error_patterns:
            match = pattern.search(log_content)
            if match:
                if len(match.groups()) == 1:
                    return match.group(1)
                else:
                    return f"{match.group(1)}: {match.group(2)}"
        return "Unknown error"

    def extract_test_summary(self, log_content: str) -> Dict[str, Any]:
        """Extract test execution summary"""
        summary = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Pytest summary pattern
        pytest_summary = re.search(r'=+ (\d+) failed.*?(\d+) passed.*?in ([\d.]+)s', log_content)
        if pytest_summary:
            summary['failed'] = int(pytest_summary.group(1))
            summary['passed'] = int(pytest_summary.group(2))
            summary['total_tests'] = summary['failed'] + summary['passed']
            summary['duration'] = float(pytest_summary.group(3))
        
        return summary

    def is_flaky_test(self, log_content: str) -> bool:
        """Detect if this might be a flaky test failure"""
        flaky_indicators = [
            'timeout',
            'connection',
            'network',
            'race condition',
            'timing',
            'random'
        ]
        
        log_lower = log_content.lower()
        return any(indicator in log_lower for indicator in flaky_indicators)
