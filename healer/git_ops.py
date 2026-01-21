import os
from git import Repo
import time

class GitOps:
    def __init__(self, repo_path="."):
        self.repo = Repo(repo_path)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.repo_slug = os.getenv("GITHUB_REPOSITORY") # e.g., "user/repo"

    def create_branch(self, branch_name):
        """Creates and checks out a new branch."""
        current = self.repo.create_head(branch_name)
        current.checkout()
        print(f"Checked out new branch: {branch_name}")

    def commit_changes(self, file_path, message):
        """Stages and commits changes."""
        self.repo.index.add([file_path])
        self.repo.index.commit(message)
        print(f"Committed changes to {file_path}")

    def push_changes(self, branch_name):
        """Pushes the branch to remote."""
        origin = self.repo.remote(name='origin')
        # We need to set the URL with the token for auth
        remote_url = f"https://x-access-token:{self.github_token}@github.com/{self.repo_slug}.git"
        origin.set_url(remote_url)
        origin.push(branch_name)
        print(f"Pushed branch {branch_name} to origin")

    def create_pr(self, branch_name, title, body):
        """Creates a Pull Request using GitHub API."""
        import requests
        
        url = f"https://api.github.com/repos/{self.repo_slug}/pulls"
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": title,
            "body": body,
            "head": branch_name,
            "base": "main"
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            print(f"PR Created: {response.json()['html_url']}")
        else:
            print(f"Failed to create PR: {response.text}")
