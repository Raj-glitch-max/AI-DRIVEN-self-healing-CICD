import sys
import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from healer.config import config
from healer.log_parser import LogParser
from healer.llm_client import LLMClient
from healer.git_ops import GitOps

# Setup logging
logger = config.setup_logging()

class HealerAgent:
    """Main AI Healer Agent with comprehensive error handling and recovery"""
    
    def __init__(self):
        self.parser = LogParser()
        self.llm_client = None
        self.git_ops = None
        self.healing_session_id = uuid.uuid4().hex[:8]
        
        logger.info(f"Initializing Healer Agent (Session: {self.healing_session_id})")
        
    def initialize_clients(self):
        """Initialize LLM and Git clients with error handling"""
        try:
            self.llm_client = LLMClient()
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
        
        try:
            self.git_ops = GitOps()
            logger.info("Git operations client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Git client: {e}")
            raise

    def heal(self, log_file_path: str) -> bool:
        """Main healing process with comprehensive error handling"""
        logger.info(f"Starting healing process for: {log_file_path}")
        
        try:
            # Step 1: Read and validate log file
            log_content = self._read_log_file(log_file_path)
            if not log_content:
                return False
            
            # Step 2: Parse the log to find errors
            error_info = self._parse_log_content(log_content)
            if not error_info:
                return False
            
            # Step 3: Read and validate the failing file
            file_content = self._read_failing_file(error_info['file_path'])
            if not file_content:
                return False
            
            # Step 4: Get fix from LLM
            fixed_content = self._get_ai_fix(file_content, error_info)
            if not fixed_content:
                return False
            
            # Step 5: Apply fix and create PR
            success = self._apply_fix_and_create_pr(error_info, fixed_content)
            
            if success:
                logger.info("🎉 Healing process completed successfully!")
                self._log_healing_summary(error_info, success=True)
            else:
                logger.error("❌ Healing process failed during PR creation")
                self._log_healing_summary(error_info, success=False)
            
            return success
            
        except Exception as e:
            logger.error(f"Unexpected error during healing: {e}")
            self._log_healing_summary({}, success=False, error=str(e))
            return False

    def _read_log_file(self, log_file_path: str) -> Optional[str]:
        """Read and validate log file"""
        try:
            if not os.path.exists(log_file_path):
                logger.error(f"Log file not found: {log_file_path}")
                return None
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.error("Log file is empty")
                return None
            
            logger.info(f"Successfully read log file: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read log file {log_file_path}: {e}")
            return None

    def _parse_log_content(self, log_content: str) -> Optional[Dict[str, Any]]:
        """Parse log content to extract error information"""
        try:
            # First try the enhanced log parser
            error_info = self.parser.parse_failure(log_content)
            
            # If that fails, try LLM-based analysis
            if not error_info and self.llm_client:
                logger.info("Falling back to LLM-based log analysis")
                error_info = self.llm_client.analyze_error(log_content)
            
            if not error_info:
                logger.error("No parseable error found in logs")
                return None
            
            # Validate error info
            required_fields = ['file_path', 'error_message']
            missing_fields = [field for field in required_fields if not error_info.get(field)]
            
            if missing_fields:
                logger.error(f"Incomplete error info, missing: {missing_fields}")
                return None
            
            logger.info(f"Found error in {error_info['file_path']}: {error_info['error_message']}")
            return error_info
            
        except Exception as e:
            logger.error(f"Failed to parse log content: {e}")
            return None

    def _read_failing_file(self, file_path: str) -> Optional[str]:
        """Read and validate the failing file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Failing file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                logger.error(f"Failing file is empty: {file_path}")
                return None
            
            logger.info(f"Successfully read failing file: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to read failing file {file_path}: {e}")
            return None

    def _get_ai_fix(self, file_content: str, error_info: Dict[str, Any]) -> Optional[str]:
        """Get AI-generated fix for the failing code"""
        try:
            logger.info("Requesting AI fix...")
            fixed_content = self.llm_client.get_fix(file_content, error_info)
            
            if not fixed_content or fixed_content == file_content:
                logger.error("LLM returned empty or unchanged content")
                return None
            
            # Basic validation of the fixed content
            if len(fixed_content.split('\n')) < 2:
                logger.error("LLM returned suspiciously short content")
                return None
            
            logger.info("Successfully received AI fix")
            return fixed_content
            
        except Exception as e:
            logger.error(f"Failed to get AI fix: {e}")
            return None

    def _apply_fix_and_create_pr(self, error_info: Dict[str, Any], fixed_content: str) -> bool:
        """Apply the fix and create a pull request"""
        branch_name = f"{config.branch_prefix}-{self.healing_session_id}"
        
        try:
            # Create branch
            if not self.git_ops.create_branch(branch_name):
                return False
            
            # Apply fix
            logger.info(f"Applying fix to {error_info['file_path']}")
            with open(error_info['file_path'], 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Commit changes
            commit_message = f"fix: AI repair for {error_info['error_message'][:50]}..."
            if not self.git_ops.commit_changes(error_info['file_path'], commit_message):
                return False
            
            # Push changes
            if not self.git_ops.push_changes(branch_name):
                return False
            
            # Create PR
            pr_title = f"🤖 AI Fix: {error_info.get('error_type', 'Error').title()} in {os.path.basename(error_info['file_path'])}"
            pr_body = self._create_pr_body(error_info)
            
            pr_url = self.git_ops.create_pr(branch_name, pr_title, pr_body)
            
            if pr_url:
                logger.info(f"Pull request created: {pr_url}")
                return True
            else:
                logger.error("Failed to create pull request")
                return False
                
        except Exception as e:
            logger.error(f"Failed to apply fix and create PR: {e}")
            # Attempt cleanup
            try:
                self.git_ops.cleanup_branch(branch_name)
            except:
                pass
            return False

    def _create_pr_body(self, error_info: Dict[str, Any]) -> str:
        """Create a comprehensive PR body"""
        return f"""## 🔧 Automated Fix Summary

**Error Type**: {error_info.get('error_type', 'Unknown')}
**File**: `{error_info['file_path']}`
**Line**: {error_info.get('line_number', 'Unknown')}
**Framework**: {error_info.get('framework', 'Unknown')}

### 🐛 Original Error
```
{error_info['error_message']}
```

### 🤖 AI Analysis
This error was automatically detected and fixed by the AI Healer Agent. The fix addresses the specific issue while preserving existing functionality.

### 🧪 Testing
Please verify that:
- [ ] All existing tests still pass
- [ ] The specific failing test now passes
- [ ] No new regressions are introduced

### 📊 Healing Session
- **Session ID**: `{self.healing_session_id}`
- **Agent Version**: `1.0.0`
- **Model Used**: `{config.openai_model}`
"""

    def _log_healing_summary(self, error_info: Dict[str, Any], success: bool, error: str = None):
        """Log a summary of the healing session"""
        summary = {
            'session_id': self.healing_session_id,
            'success': success,
            'file_path': error_info.get('file_path', 'Unknown'),
            'error_type': error_info.get('error_type', 'Unknown'),
            'error_message': error_info.get('error_message', 'Unknown')
        }
        
        if error:
            summary['error'] = error
        
        if success:
            logger.info(f"Healing Summary: {summary}")
        else:
            logger.error(f"Healing Failed: {summary}")

def main():
    """Main entry point for the healer agent"""
    print("🤖 AI-Driven Self-Healing CI/CD Platform")
    print("=" * 50)
    
    # Validate arguments
    if len(sys.argv) < 2:
        print("❌ Usage: python agent.py <path_to_log_file>")
        print("Example: python agent.py test_output.log")
        sys.exit(1)
    
    log_file_path = sys.argv[1]
    
    try:
        # Initialize and run healer
        healer = HealerAgent()
        healer.initialize_clients()
        
        success = healer.heal(log_file_path)
        
        if success:
            print("✅ Healing completed successfully!")
            sys.exit(0)
        else:
            print("❌ Healing failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Healing process interrupted by user")
        print("\n⚠️  Healing process interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
