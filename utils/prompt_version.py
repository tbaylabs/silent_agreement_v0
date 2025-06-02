"""
Prompt version control utilities for the Silent Agreement evaluation framework.
"""

import subprocess
import json
import hashlib
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from datetime import datetime

class PromptVersion:
    """Handles prompt version control using Git and a version tracking file."""
    
    def __init__(self):
        self.versions_file = Path(__file__).parent.parent / "dataset_generation" / "PROMPT_VERSIONS.json"
        self.prompt_files = {
            "base": [
                "dataset_generation/prompts.py",
                "dataset_generation/base/base_conditions.py"
            ],
            "reasoning": [
                "dataset_generation/prompts.py",
                "dataset_generation/reasoning/reasoning_conditions.py"
            ]
        }
        self.versions_data = self._load_versions()
    
    def _load_versions(self) -> Dict:
        """Load the prompt versions data."""
        if not self.versions_file.exists():
            raise FileNotFoundError(f"PROMPT_VERSIONS.json not found at {self.versions_file}")
        
        with open(self.versions_file, 'r') as f:
            return json.load(f)
    
    def _save_versions(self):
        """Save the prompt versions data."""
        with open(self.versions_file, 'w') as f:
            json.dump(self.versions_data, f, indent=2)
    
    def get_current_version(self, eval_type: str) -> str:
        """Get the current (latest) version for an evaluation type."""
        if eval_type not in self.versions_data:
            raise ValueError(f"Unknown evaluation type: {eval_type}")
        
        return f"{eval_type}/{self.versions_data[eval_type]['latest']}"
    
    def get_version_info(self, eval_type: str, version: Optional[str] = None) -> Dict:
        """Get information about a specific version."""
        if eval_type not in self.versions_data:
            raise ValueError(f"Unknown evaluation type: {eval_type}")
        
        if version is None:
            version = self.versions_data[eval_type]['latest']
        else:
            # Handle full version format (e.g., "base/v1")
            if "/" in version:
                _, version = version.split("/", 1)
        
        if version not in self.versions_data[eval_type]['versions']:
            raise ValueError(f"Unknown version: {eval_type}/{version}")
        
        return self.versions_data[eval_type]['versions'][version]
    
    def check_modifications(self, eval_type: str) -> Tuple[bool, List[str]]:
        """
        Check if prompt files have been modified since the current version.
        
        Returns:
            Tuple of (has_modifications, list_of_modified_files)
        """
        if eval_type not in self.prompt_files:
            raise ValueError(f"Unknown evaluation type: {eval_type}")
        
        current_version = self.versions_data[eval_type]['latest']
        version_info = self.get_version_info(eval_type, current_version)
        version_commit = version_info['commit']
        
        modified_files = []
        
        for file_path in self.prompt_files[eval_type]:
            # Check if file has been modified since the version commit
            result = subprocess.run(
                ["git", "diff", version_commit, "HEAD", "--name-only", file_path],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                modified_files.append(file_path)
        
        # Also check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"] + self.prompt_files[eval_type],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            # Parse the status output to get modified files
            for line in result.stdout.strip().split('\n'):
                if line:
                    file_path = line[3:]  # Skip status code and space
                    if file_path not in modified_files:
                        modified_files.append(file_path)
        
        return len(modified_files) > 0, modified_files
    
    def create_new_version(self, eval_type: str, description: str) -> str:
        """Create a new version for the given evaluation type."""
        if eval_type not in self.versions_data:
            raise ValueError(f"Unknown evaluation type: {eval_type}")
        
        # Determine new version number
        current_version = self.versions_data[eval_type]['latest']
        version_num = int(current_version[1:])  # Remove 'v' prefix
        new_version = f"v{version_num + 1}"
        
        # Get current git commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True
        )
        commit_hash = result.stdout.strip()
        
        # Calculate hash of current prompt files
        files_hash = self._calculate_files_hash(eval_type)
        
        # Extract current constants
        constants = self._extract_constants(eval_type)
        
        # Create new version entry
        self.versions_data[eval_type]['versions'][new_version] = {
            "commit": commit_hash,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "description": description,
            "files_hash": files_hash,
            "constants": constants
        }
        
        # Update latest version
        self.versions_data[eval_type]['latest'] = new_version
        
        # Save the updated versions
        self._save_versions()
        
        return f"{eval_type}/{new_version}"
    
    def _calculate_files_hash(self, eval_type: str) -> str:
        """Calculate a combined hash of all prompt-related files."""
        hasher = hashlib.sha256()
        
        # Add prompt file contents
        for file_path in sorted(self.prompt_files[eval_type]):
            if Path(file_path).exists():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        # Add relevant constants
        constants = self._extract_constants(eval_type)
        hasher.update(json.dumps(constants, sort_keys=True).encode())
        
        return f"sha256:{hasher.hexdigest()}"
    
    def _extract_constants(self, eval_type: str) -> Dict:
        """Extract relevant constants for the evaluation type."""
        # Import dynamically to get current values
        if eval_type == "base":
            from dataset_generation.prompts import SUPPRESS_COT_SUFFIX, ELICIT_COT_SUFFIX
            return {
                "SUPPRESS_COT_SUFFIX": SUPPRESS_COT_SUFFIX,
                "ELICIT_COT_SUFFIX": ELICIT_COT_SUFFIX
            }
        elif eval_type == "reasoning":
            from utils.constants import LOW_REASONING_TOKENS, HIGH_REASONING_TOKENS
            from dataset_generation.prompts import ELICIT_THOUGHT_SUFFIX
            return {
                "LOW_REASONING_TOKENS": LOW_REASONING_TOKENS,
                "HIGH_REASONING_TOKENS": HIGH_REASONING_TOKENS,
                "ELICIT_THOUGHT_SUFFIX": ELICIT_THOUGHT_SUFFIX
            }
        else:
            return {}
    
    def list_versions(self, eval_type: Optional[str] = None) -> Dict:
        """List all available versions, optionally filtered by eval type."""
        if eval_type:
            if eval_type not in self.versions_data:
                raise ValueError(f"Unknown evaluation type: {eval_type}")
            return {eval_type: self.versions_data[eval_type]}
        else:
            return self.versions_data
    
    def validate_version(self, version_string: str) -> Tuple[str, str]:
        """
        Validate and parse a version string.
        
        Args:
            version_string: Version in format "eval_type/version" (e.g., "base/v1")
        
        Returns:
            Tuple of (eval_type, version_number)
        """
        if "/" not in version_string:
            raise ValueError(f"Invalid version format: {version_string}. Use format: eval_type/version (e.g., base/v1)")
        
        eval_type, version = version_string.split("/", 1)
        
        if eval_type not in self.versions_data:
            raise ValueError(f"Unknown evaluation type: {eval_type}")
        
        if version not in self.versions_data[eval_type]['versions']:
            raise ValueError(f"Unknown version: {version_string}")
        
        return eval_type, version