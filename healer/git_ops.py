import os
import subprocess
import logging
import requests
from typing import Optional, Dict, Any
from .config import config

logger = logging.getLogger(__name__)

class GitOps:
    """Enhanced Git operations with comprehensive error handling and validation"""
    
    def __init__(self):
        self.repo_url = config.github_repository
        self.token = config.github_token
        self.base_branch = config.github_base_branch
        self.branch_prefix = config.branch_prefix
        
        if not self.token or not self.repo_url:
            logger.warning("GitHub token or repository not configured. Some operations may fail.")
        
        self._setup_git_config()
        
    def _setup_git_config(self):
        """Setup git configuration for the healer agent"""
        try:
            self.run_cmd("git config --global user.email 'ai-healer@cicd.bot'")
            self.run_cmd("git config --global user.name 'AI Healer Bot'")
            logger.info("Git configuration setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup git config: {e}")

    def run_cmd(self, cmd: str, check_output: bool = True) -> str:
        """Execute git command with proper error handling"""
        logger.debug(f"Executing: {cmd}")
        
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30  # Prevent hanging
            )
            
            if result.returncode != 0:
                error_msg = f"Command failed: {cmd}\nError: {result.stderr}"
                logger.error(error_msg)
                if check_output:
                    raise Exception(error_msg)
                return ""
            
            output = result.stdout.strip()
            logger.debug(f"Command output: {output}")
            return output
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out: {cmd}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Failed to execute command: {cmd}. Error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)

    def get_current_branch(self) -> str:
        """Get the current git branch"""
        return self.run_cmd("git rev-parse --abbrev-ref HEAD")

    def is_clean_working_directory(self) -> bool:
        """Check if working directory is clean"""
        try:
            output = self.run_cmd("git status --porcelain", check_output=False)
            return len(output.strip()) == 0
        except:
            return False

    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch with validation"""
        try:
            # Ensure we're on the base branch
            current_branch = self.get_current_branch()
            if current_branch != self.base_branch:
                logger.info(f"Switching from {current_branch} to {self.base_branch}")
                self.run_cmd(f"git checkout {self.base_branch}")
            
            # Pull latest changes
            self.run_cmd(f"git pull origin {self.base_branch}")
            
            # Check if branch already exists
            existing_branches = self.run_cmd("git branch -a", check_output=False)
            if branch_name in existing_branches:
                logger.warning(f"Branch {branch_name} already exists, deleting it")
                self.run_cmd(f"git branch -D {branch_name}", check_output=False)
            
            # Create new branch
            self.run_cmd(f"git checkout -b {branch_name}")
            logger.info(f"Created and switched to branch: {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            return False

    def commit_changes(self, file_path: str, message: str) -> bool:
        """Commit changes with validation"""
        try:
            # Verify file exists
            if not os.path.exists(file_path):
                raise Exception(f"File {file_path} does not exist")
            
            # Add file
            self.run_cmd(f"git add {file_path}")
            
            # Check if there are changes to commit
            status = self.run_cmd("git status --porcelain", check_output=False)
            if not status.strip():
                logger.warning("No changes to commit")
                return False
            
            # Commit changes
            escaped_message = message.replace("'", "\\'")
            self.run_cmd(f"git commit -m '{escaped_message}'")
            logger.info(f"Committed changes to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to commit changes: {e}")
            return False

    def push_changes(self, branch_name: str) -> bool:
        """Push changes to remote repository"""
        if not self.token or not self.repo_url:
            logger.error("GitHub token or repository not configured")
            return False
        
        try:
            # Configure remote with token
            remote_url = f"https://{self.token}@github.com/{self.repo_url}.git"
            
            # Push the branch
            self.run_cmd(f"git push {remote_url} {branch_name}")
            logger.info(f"Successfully pushed branch {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            return False

    def create_pr(self, branch_name: str, title: str, body: str) -> Optional[str]:
        """Create a pull request using GitHub API"""
        if not self.token or not self.repo_url:
            logger.error("GitHub token or repository not configured")
            return None
        
        try:
            url = f"https://api.github.com/repos/{self.repo_url}/pulls"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            data = {
                "title": title,
                "body": self._enhance_pr_body(body, branch_name),
                "head": branch_name,
                "base": self.base_branch
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 201:
                pr_data = response.json()
                pr_url = pr_data.get('html_url')
                logger.info(f"PR created successfully: {pr_url}")
                return pr_url
            else:
                logger.error(f"Failed to create PR: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return None

    def _enhance_pr_body(self, body: str, branch_name: str) -> str:
        """Enhance PR body with additional context"""
        enhanced_body = f"""## 🤖 AI-Generated Fix

{body}

---

### 🔧 Automated Healing Details
- **Branch**: `{branch_name}`
- **Generated by**: AI Healer Agent
- **Timestamp**: {self._get_timestamp()}

### ✅ Pre-merge Checklist
- [ ] Review the proposed changes
- [ ] Verify tests pass locally
- [ ] Check for any side effects
- [ ] Confirm the fix addresses the root cause

### 🚀 Next Steps
1. Review the changes in this PR
2. Run tests locally to verify the fix
3. Merge if everything looks good
4. Monitor for any regressions

*This PR was automatically generated by the AI-Driven Self-Healing CI/CD Platform.*
"""
        return enhanced_body

    def _get_timestamp(self) -> str:
        """Get current timestamp for PR body"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    def cleanup_branch(self, branch_name: str) -> bool:
        """Clean up the healing branch after PR is merged"""
        try:
            # Switch back to base branch
            self.run_cmd(f"git checkout {self.base_branch}")
            
            # Delete local branch
            self.run_cmd(f"git branch -D {branch_name}", check_output=False)
            
            logger.info(f"Cleaned up branch: {branch_name}")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to cleanup branch {branch_name}: {e}")
            return False

    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information"""
        try:
            return {
                'current_branch': self.get_current_branch(),
                'is_clean': self.is_clean_working_directory(),
                'remote_url': self.run_cmd("git remote get-url origin", check_output=False),
                'last_commit': self.run_cmd("git log -1 --oneline", check_output=False)
            }
        except Exception as e:
            logger.error(f"Failed to get repo info: {e}")
            return {}
