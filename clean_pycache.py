#!/usr/bin/env python
"""
Script to clean __pycache__ directories before pushing to GitHub.
This helps prevent accidentally pushing compiled Python files that might contain API keys.
"""

import os
import shutil
import sys

def clean_pycache(root_dir='.'):
    """Remove all __pycache__ directories and .pyc files from the project."""
    count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"Removing: {pycache_path}")
            shutil.rmtree(pycache_path)
            count += 1
            dirs.remove('__pycache__')  # Don't recurse into deleted directory
        
        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"Removing: {pyc_path}")
                os.remove(pyc_path)
                count += 1
    
    return count

if __name__ == '__main__':
    # Get the root directory from command line args or use current directory
    root_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print(f"Cleaning __pycache__ directories and .pyc files from {root_dir}...")
    count = clean_pycache(root_dir)
    
    print(f"Cleaned {count} __pycache__ directories and .pyc files.")
    print("Done!")
