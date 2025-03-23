#!/usr/bin/env python3
"""
Git Commit Script

This script performs a single Git commit and push operation for the current state
of the repository.
"""

import os
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Git repository path (current directory)
REPO_PATH = os.getcwd()

def commit_changes(message=None):
    """Commit all changes to Git and push to remote."""
    try:
        # Get the GitHub token from environment
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            logging.error("GitHub token not found in environment")
            return False
            
        # Create commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not message:
            message = f"Auto-commit: Changes at {timestamp}"
        
        # Add all changes
        logging.info("Adding changes to Git...")
        subprocess.run(["git", "add", "."], cwd=REPO_PATH, check=True)
        
        # Commit changes
        logging.info("Committing changes...")
        subprocess.run(["git", "commit", "-m", message], cwd=REPO_PATH, check=True)
        
        # Push changes using the GitHub token
        logging.info("Pushing to GitHub...")
        push_url = f"https://oauth2:{github_token}@github.com/HananiahKao/Web-App.git"
        subprocess.run(["git", "push", push_url, "main"], cwd=REPO_PATH, check=True)
        
        logging.info("Successfully committed and pushed changes to GitHub")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")
        return False
    except Exception as e:
        logging.error(f"Error during commit: {e}")
        return False

if __name__ == "__main__":
    # Get commit message from command line argument if provided
    import sys
    message = None
    if len(sys.argv) > 1:
        message = sys.argv[1]
    
    commit_changes(message)