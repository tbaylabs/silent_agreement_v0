"""
Generalized prompt registry system for managing multiple evaluation types.
Supports different prompt versions and condition sets.
"""

import json
import hashlib
from typing import Dict, Any, Type, List
from pathlib import Path
from enum import Enum

from dataset_generation.base.base_conditions import create_chat_messages


class PromptRegistry:
    """Generic registry for managing prompt versions across evaluation types."""
    
    def __init__(self, registry_file: str, condition_enum: Type[Enum], prompt_name: str = "experiment_prompts", message_factory: callable = None):
        """
        Initialize prompt registry.
        
        Args:
            registry_file: Path to the JSON file storing prompt hashes
            condition_enum: Enum class defining the experimental conditions
            prompt_name: Name for this set of prompts (e.g., "experiment_prompts", "thinking_prompts")
            message_factory: Optional custom message factory function (defaults to create_chat_messages)
        """
        self.registry_file = Path(registry_file)
        self.condition_enum = condition_enum
        self.prompt_name = prompt_name
        self.message_factory = message_factory or create_chat_messages
        
        # Placeholder options for generating sample prompts
        self.placeholder_options = ["first_option", "second_option", "third_option", "fourth_option"]
    
    def generate_sample_prompts(self) -> Dict[str, str]:
        """
        Generate sample prompts for all conditions using placeholder options.
        
        Returns:
            Dict mapping condition names to prompt strings
        """
        prompts = {}
        
        for condition in self.condition_enum:
            # Generate chat messages for this condition using the factory
            messages = self.message_factory(
                options=self.placeholder_options,
                condition=condition
            )
            # Extract just the user message content
            prompts[condition.value] = messages[0].content
        
        return prompts
    
    def compute_prompt_hash(self, prompts: Dict[str, str]) -> str:
        """
        Compute a deterministic hash of a set of prompts.
        
        Args:
            prompts: Dictionary mapping condition names to prompt strings
            
        Returns:
            SHA-256 hash of the prompts
        """
        # Sort keys to ensure deterministic ordering
        sorted_prompts = {k: prompts[k] for k in sorted(prompts.keys())}
        
        # Create a canonical JSON representation
        canonical_json = json.dumps(sorted_prompts, sort_keys=True, ensure_ascii=True)
        
        # Compute SHA-256 hash
        return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    
    def create_version_entry(self, prompts: Dict[str, str], timestamp: str) -> Dict[str, Any]:
        """
        Create a version entry for a set of prompts.
        
        Args:
            prompts: Dictionary of prompts by condition
            timestamp: ISO date string for when this version was created
            
        Returns:
            Version entry dictionary
        """
        return {
            "hash": self.compute_prompt_hash(prompts),
            "timestamp": timestamp,
            "prompts": prompts
        }
    
    def save_version(self, version_name: str, timestamp: str = None) -> None:
        """
        Generate and save a new prompt version.
        
        Args:
            version_name: Name for this version (e.g., "v1_standard", "v1_thinking")
            timestamp: Optional timestamp, defaults to current date
        """
        if timestamp is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d")
        
        # Generate current prompts
        prompts = self.generate_sample_prompts()
        
        # Load existing registry or create new one
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                registry = json.load(f)
        else:
            registry = {}
        
        # Ensure the prompt name section exists
        if self.prompt_name not in registry:
            registry[self.prompt_name] = {}
        
        # Add new version
        registry[self.prompt_name][version_name] = self.create_version_entry(prompts, timestamp)
        
        # Save registry
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Prompt version '{version_name}' saved to: {self.registry_file}")
        print(f"   Hash: {registry[self.prompt_name][version_name]['hash'][:16]}...")
    
    def verify_version(self, version_name: str) -> bool:
        """
        Verify that current prompts match the specified version.
        
        Args:
            version_name: Version name to check against
            
        Returns:
            True if prompts match, False otherwise
            
        Raises:
            RuntimeError: If verification fails with details
        """
        # Load saved registry
        if not self.registry_file.exists():
            raise RuntimeError(
                f"Prompt registry file not found: {self.registry_file}\\n"
                f"Run save_version() to create it."
            )
        
        with open(self.registry_file) as f:
            registry = json.load(f)
        
        # Check if prompt name and version exist
        if self.prompt_name not in registry:
            raise RuntimeError(f"Prompt type '{self.prompt_name}' not found in registry")
        
        if version_name not in registry[self.prompt_name]:
            raise RuntimeError(f"Version '{version_name}' not found for '{self.prompt_name}'")
        
        # Generate current prompts and compare hash
        current_prompts = self.generate_sample_prompts()
        current_hash = self.compute_prompt_hash(current_prompts)
        
        saved_hash = registry[self.prompt_name][version_name]["hash"]
        
        if saved_hash != current_hash:
            raise RuntimeError(
                f"Prompts for '{self.prompt_name}' have changed!\\n"
                f"Expected hash ({version_name}): {saved_hash[:16]}...\\n"
                f"Current hash:                   {current_hash[:16]}...\\n"
                f"This likely means the prompt templates have been modified.\\n"
                f"If this is intentional, create a new version."
            )
        
        return True
    
    def list_versions(self) -> List[str]:
        """
        List all available versions for this prompt type.
        
        Returns:
            List of version names
        """
        if not self.registry_file.exists():
            return []
        
        with open(self.registry_file) as f:
            registry = json.load(f)
        
        return list(registry.get(self.prompt_name, {}).keys())
    
    def get_version_info(self, version_name: str) -> Dict[str, Any]:
        """
        Get information about a specific version.
        
        Args:
            version_name: Version to get info for
            
        Returns:
            Version information dictionary
        """
        if not self.registry_file.exists():
            raise RuntimeError(f"Registry file not found: {self.registry_file}")
        
        with open(self.registry_file) as f:
            registry = json.load(f)
        
        if self.prompt_name not in registry or version_name not in registry[self.prompt_name]:
            raise RuntimeError(f"Version '{version_name}' not found")
        
        return registry[self.prompt_name][version_name]