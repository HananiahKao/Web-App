#!/usr/bin/env python3
"""
Git Auto-Commit Script

This script watches for file changes in a directory and automatically commits 
and pushes changes to Git when files are modified.
"""

import os
import time
import subprocess
import logging
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Git repository path (current directory)
REPO_PATH = os.getcwd()

# Files to ignore (don't trigger commits for these)
IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    '*.pyc',
    '.DS_Store',
    'git_auto_commit.py',  # Don't commit changes to this script itself
]

class GitAutoCommitHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_commit_time = time.time()
        self.pending_changes = set()
        self.commit_delay = 2  # Delay in seconds to accumulate changes

    def should_ignore(self, path):
        """Check if a file should be ignored based on patterns."""
        for pattern in IGNORE_PATTERNS:
            if pattern.startswith('*'):
                if path.endswith(pattern[1:]):
                    return True
            elif pattern in path:
                return True
        return False

    def on_any_event(self, event):
        """Handle any file system event."""
        if event.is_directory:
            return
        
        # Get path relative to repository
        try:
            path = os.path.relpath(event.src_path, REPO_PATH)
            
            # Ignore files based on patterns
            if self.should_ignore(path):
                return
                
            # Store the changed file
            self.pending_changes.add(path)
            logging.info(f"Change detected in {path}")
            
            # Schedule a commit after delay
            current_time = time.time()
            if current_time - self.last_commit_time > self.commit_delay:
                self.commit_changes()
                self.last_commit_time = current_time
        except Exception as e:
            logging.error(f"Error processing event: {e}")

    def commit_changes(self):
        """Commit pending changes to Git."""
        if not self.pending_changes:
            return
            
        try:
            # Get the GitHub token from environment
            github_token = os.environ.get('GITHUB_TOKEN')
            if not github_token:
                logging.error("GitHub token not found in environment")
                return
                
            changed_files = list(self.pending_changes)
            self.pending_changes.clear()
            
            # Create commit message with list of changed files
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-commit: Changes to {', '.join(changed_files)} at {timestamp}"
            
            # Add files to git
            subprocess.run(["git", "add"] + changed_files, cwd=REPO_PATH, check=True)
            
            # Commit changes
            subprocess.run(["git", "commit", "-m", commit_message], cwd=REPO_PATH, check=True)
            
            # Push changes using the GitHub token
            push_url = f"https://oauth2:{github_token}@github.com/HananiahKao/Web-App.git"
            subprocess.run(["git", "push", push_url, "main"], cwd=REPO_PATH, check=True)
            
            logging.info(f"Committed and pushed {len(changed_files)} files")
        except subprocess.CalledProcessError as e:
            logging.error(f"Git operation failed: {e}")
        except Exception as e:
            logging.error(f"Error during commit: {e}")


def main():
    """Main function to start the file watcher."""
    logging.info(f"Starting Git auto-commit watcher for {REPO_PATH}")
    
    # Create event handler and observer
    event_handler = GitAutoCommitHandler()
    observer = Observer()
    
    # Schedule watching the repository
    observer.schedule(event_handler, REPO_PATH, recursive=True)
    observer.start()
    
    try:
        logging.info("Watching for file changes (press Ctrl+C to stop)...")
        while True:
            time.sleep(1)
            # Check for accumulated changes
            if event_handler.pending_changes and (time.time() - event_handler.last_commit_time > event_handler.commit_delay):
                event_handler.commit_changes()
                event_handler.last_commit_time = time.time()
                
    except KeyboardInterrupt:
        logging.info("Stopping file watcher...")
        observer.stop()
        
    observer.join()
    logging.info("Git auto-commit watcher stopped")


if __name__ == "__main__":
    main()