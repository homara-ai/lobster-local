"""
Professional agent configuration system for Genie AI.

This module provides a flexible, type-safe configuration system that allows
per-agent model configuration for easy testing and deployment.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelProvider(Enum):
    """Supported model providers."""
    BEDROCK_ANTHROPIC = "bedrock_anthropic"
    OPENAI = "openai"
    BEDROCK_META = "bedrock_meta"
    BEDROCK_AMAZON = "bedrock_amazon"

class ModelTier(Enum):
    """Model performance tiers."""
    LIGHTWEIGHT = "lightweight"
    STANDARD = "standard" 
    HEAVY = "heavy"
    ULTRA = "ultra"

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    provider: ModelProvider
    model_id: str
    tier: ModelTier
    temperature: float = 0.7
    region: str = "us-east-1"
    description: str = ""
    
    def __post_init__(self):
        if isinstance(self.provider, str):
            self.provider = ModelProvider(self.provider)
        if isinstance(self.tier, str):
            self.tier = ModelTier(self.tier)

@dataclass
class AgentConfig:
    """Configuration for a specific agent."""
    name: str
    model_config: ModelConfig
    fallback_model: Optional[str] = None
    enabled: bool = True
    custom_params: Dict = field(default_factory=dict)

class GenieAgentConfigurator:
    """
    Professional configuration manager for Genie AI agents.
    
    Features:
    - Per-agent model configuration
    - Environment-based overrides
    - Fallback mechanisms
    - Easy testing profiles
    - Production-ready validation
    """
    
    # Pre-defined model configurations
    MODEL_PRESETS = {
        # Anthropic Claude Models - Lightweight (Haiku family)
        "claude-3-haiku": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-haiku-20240307-v1:0",
            tier=ModelTier.LIGHTWEIGHT,
            temperature=0.7,
            description="Fast, cost-effective Claude 3 Haiku for simple tasks"
        ),
        
        "claude-3-5-haiku": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            tier=ModelTier.LIGHTWEIGHT,
            temperature=0.7,
            description="Fast, cost-effective Claude 3.5 Haiku for simple tasks"
        ),
        
        "claude-3-5-sonnet": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-5-sonnet-20240620-v1:0",
            tier=ModelTier.STANDARD,
            temperature=0.7,
            description="Enhanced Claude 3.5 Sonnet with improved performance"
        ),
        
        "claude-3-5-sonnet-v2": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
            tier=ModelTier.STANDARD,
            temperature=0.7,
            description="Latest Claude 3.5 Sonnet v2 with enhanced capabilities"
        ),
        
        "claude-4-sonnet": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-sonnet-4-20250514-v1:0",
            tier=ModelTier.STANDARD,
            temperature=0.7,
            description="Next-generation Claude 4 Sonnet model"
        ),
        
        # Anthropic Claude Models - Heavy (Opus family)
        "claude-3-opus": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-opus-20240229-v1:0",
            tier=ModelTier.HEAVY,
            temperature=1.0,
            description="Most capable Claude 3 Opus for complex analysis"
        ),
        
        "claude-4-opus": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-opus-4-20250514-v1:0",
            tier=ModelTier.HEAVY,
            temperature=1.0,
            description="Advanced Claude 4 Opus for complex reasoning"
        ),
        
        "claude-4-1-opus": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-opus-4-1-20250805-v1:0",
            tier=ModelTier.HEAVY,
            temperature=1.0,
            description="Latest Claude 4.1 Opus with cutting-edge capabilities"
        ),
        
        # Ultra Performance Models
        "claude-3-7-sonnet": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            tier=ModelTier.ULTRA,
            temperature=1.0,
            description="Highest-performance Claude 3.7 Sonnet model"
        ),
        
        # EU Region Models (for EU compliance)
        "claude-3-5-haiku-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-3-5-haiku-20241022-v1:0",
            tier=ModelTier.LIGHTWEIGHT,
            temperature=0.7,
            region="eu-central-1",
            description="EU region Claude 3.5 Haiku model"
        ),
        
        "claude-3-5-sonnet-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
            tier=ModelTier.STANDARD,
            temperature=0.7,
            region="eu-central-1",
            description="EU region Claude 3.5 Sonnet model"
        ),
        
        "claude-3-5-sonnet-v2-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-3-5-sonnet-20241022-v2:0",
            tier=ModelTier.STANDARD,
            temperature=0.7,
            region="eu-central-1",
            description="EU region Claude 3.5 Sonnet v2 model"
        ),
        
        "claude-4-opus-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-opus-4-20250514-v1:0",
            tier=ModelTier.HEAVY,
            temperature=1.0,
            region="eu-central-1",
            description="EU region Claude 4 Opus model"
        ),
        
        "claude-4-1-opus-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-opus-4-1-20250805-v1:0",
            tier=ModelTier.HEAVY,
            temperature=1.0,
            region="eu-central-1",
            description="EU region Claude 4.1 Opus model"
        ),
        
        "claude-3-7-sonnet-eu": ModelConfig(
            provider=ModelProvider.BEDROCK_ANTHROPIC,
            model_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
            tier=ModelTier.ULTRA,
            temperature=1.0,
            region="eu-central-1",
            description="EU region Claude 3.7 Sonnet model"
        )
    }
    
    # Default agents configuration - modify this to add/remove agents dynamically
    DEFAULT_AGENTS = [
        "supervisor",
        "transcriptomics_expert", 
        "method_agent",
        "general_conversation"
    ]
    
    # Pre-defined testing profiles - automatically includes all agents
    TESTING_PROFILES = {
        "development": {
            "supervisor": "claude-3-5-haiku",
            "transcriptomics_expert": "claude-3-5-haiku", 
            "method_agent": "claude-3-5-haiku",
            "general_conversation": "claude-3-5-haiku"
        },
        
        "production": {
            "supervisor": "claude-3-5-sonnet-v2",
            "transcriptomics_expert": "claude-4-opus",
            "method_agent": "claude-3-5-sonnet",
            "general_conversation": "claude-3-5-sonnet"
        },
        
        "high-performance": {
            "supervisor": "claude-4-opus",
            "transcriptomics_expert": "claude-3-7-sonnet",
            "method_agent": "claude-4-sonnet",
            "general_conversation": "claude-3-5-haiku"
        },
        
        "ultra-performance": {
            "supervisor": "claude-3-7-sonnet",
            "transcriptomics_expert": "claude-3-7-sonnet",
            "method_agent": "claude-4-1-opus",
            "general_conversation": "claude-4-sonnet"
        },
        
        "cost-optimized": {
            "supervisor": "claude-3-haiku",
            "transcriptomics_expert": "claude-3-5-sonnet",
            "method_agent": "claude-3-haiku",
            "general_conversation": "claude-3-haiku"
        },
        
        "heavyweight": {
            "supervisor": "claude-4-1-opus",
            "transcriptomics_expert": "claude-4-1-opus",
            "method_agent": "claude-4-opus",
            "general_conversation": "claude-4-opus"
        },
        
        "eu-compliant": {
            "supervisor": "claude-3-5-sonnet-v2-eu",
            "transcriptomics_expert": "claude-4-1-opus-eu",
            "method_agent": "claude-3-5-sonnet-eu",
            "general_conversation": "claude-3-5-sonnet-eu"
        },
        
        "eu-high-performance": {
            "supervisor": "claude-3-7-sonnet-eu",
            "transcriptomics_expert": "claude-3-7-sonnet-eu",
            "method_agent": "claude-4-opus-eu",
            "general_conversation": "claude-3-5-sonnet-v2-eu"
        }
    }
    
    def __init__(self, profile: str = None, config_file: str = None):
        """
        Initialize the configurator.
        
        Args:
            profile: Testing profile name (e.g., 'development', 'production')
            config_file: Path to custom configuration file
        """
        self.profile = profile or os.environ.get('GENIE_PROFILE', 'production')
        self.config_file = config_file
        self._agent_configs = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from profile or custom file."""
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file()
        else:
            self._load_from_profile()
        
        # Apply environment overrides
        self._apply_env_overrides()
    
    def _load_from_profile(self):
        """Load configuration from a testing profile."""
        if self.profile not in self.TESTING_PROFILES:
            raise ValueError(f"Unknown profile: {self.profile}. Available: {list(self.TESTING_PROFILES.keys())}")
        
        profile_config = self.TESTING_PROFILES[self.profile]
        
        for agent_name, model_preset in profile_config.items():
            if model_preset not in self.MODEL_PRESETS:
                raise ValueError(f"Unknown model preset: {model_preset}")
            
            self._agent_configs[agent_name] = AgentConfig(
                name=agent_name,
                model_config=self.MODEL_PRESETS[model_preset]
            )
    
    def _load_from_file(self):
        """Load configuration from JSON file."""
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)
        
        for agent_name, agent_data in config_data.get('agents', {}).items():
            model_data = agent_data['model_config']
            
            model_config = ModelConfig(
                provider=model_data['provider'],
                model_id=model_data['model_id'],
                tier=model_data['tier'],
                temperature=model_data.get('temperature', 0.7),
                region=model_data.get('region', 'us-east-1'),
                description=model_data.get('description', '')
            )
            
            self._agent_configs[agent_name] = AgentConfig(
                name=agent_name,
                model_config=model_config,
                fallback_model=agent_data.get('fallback_model'),
                enabled=agent_data.get('enabled', True),
                custom_params=agent_data.get('custom_params', {})
            )
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        # Global overrides
        if os.environ.get('GENIE_GLOBAL_MODEL'):
            model_preset = os.environ.get('GENIE_GLOBAL_MODEL')
            if model_preset in self.MODEL_PRESETS:
                for agent_config in self._agent_configs.values():
                    agent_config.model_config = self.MODEL_PRESETS[model_preset]
        
        # Per-agent overrides
        for agent_name in self._agent_configs:
            env_key = f'GENIE_{agent_name.upper()}_MODEL'
            if os.environ.get(env_key):
                model_preset = os.environ.get(env_key)
                if model_preset in self.MODEL_PRESETS:
                    self._agent_configs[agent_name].model_config = self.MODEL_PRESETS[model_preset]
        
        # Temperature overrides
        for agent_name in self._agent_configs:
            env_key = f'GENIE_{agent_name.upper()}_TEMPERATURE'
            if os.environ.get(env_key):
                try:
                    temperature = float(os.environ.get(env_key))
                    self._agent_configs[agent_name].model_config.temperature = temperature
                except ValueError:
                    pass
    
    def get_agent_config(self, agent_name: str) -> AgentConfig:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            AgentConfig for the specified agent
            
        Raises:
            KeyError: If agent configuration not found
        """
        if agent_name not in self._agent_configs:
            raise KeyError(f"No configuration found for agent: {agent_name}")
        
        return self._agent_configs[agent_name]
    
    def get_model_config(self, agent_name: str) -> ModelConfig:
        """
        Get model configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            ModelConfig for the specified agent
        """
        return self.get_agent_config(agent_name).model_config
    
    def get_llm_params(self, agent_name: str) -> Dict:
        """
        Get LLM initialization parameters for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary of parameters for LLM initialization
        """
        model_config = self.get_model_config(agent_name)
        
        # Base parameters
        params = {
            "model_id": model_config.model_id,
            "temperature": model_config.temperature,
            "region_name": model_config.region,
        }
        
        # Add provider-specific parameters
        if model_config.provider == ModelProvider.BEDROCK_ANTHROPIC:
            params.update({
                "aws_access_key_id": os.environ.get('AWS_BEDROCK_ACCESS_KEY'),
                "aws_secret_access_key": os.environ.get('AWS_BEDROCK_SECRET_ACCESS_KEY'),
            })
        elif model_config.provider == ModelProvider.OPENAI:
            params.update({
                "openai_api_key": os.environ.get('OPENAI_API_KEY'),
            })
        
        return params
    
    def list_available_models(self) -> Dict[str, ModelConfig]:
        """List all available model presets."""
        return self.MODEL_PRESETS.copy()
    
    def list_available_profiles(self) -> Dict[str, Dict]:
        """List all available testing profiles."""
        return self.TESTING_PROFILES.copy()
    
    def get_current_profile(self) -> str:
        """Get current active profile."""
        return self.profile
    
    def export_config(self, filepath: str):
        """
        Export current configuration to JSON file.
        
        Args:
            filepath: Path to save configuration file
        """
        config_data = {
            "profile": self.profile,
            "agents": {}
        }
        
        for agent_name, agent_config in self._agent_configs.items():
            config_data["agents"][agent_name] = {
                "model_config": {
                    "provider": agent_config.model_config.provider.value,
                    "model_id": agent_config.model_config.model_id,
                    "tier": agent_config.model_config.tier.value,
                    "temperature": agent_config.model_config.temperature,
                    "region": agent_config.model_config.region,
                    "description": agent_config.model_config.description
                },
                "fallback_model": agent_config.fallback_model,
                "enabled": agent_config.enabled,
                "custom_params": agent_config.custom_params
            }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def print_current_config(self):
        """Print current configuration in a readable format."""
        print("\n🔧 Genie AI Configuration")
        print(f"Profile: {self.profile}")
        print(f"{'='*60}")
        
        for agent_name, agent_config in self._agent_configs.items():
            model = agent_config.model_config
            print(f"\n🤖 {agent_name.title()}")
            print(f"   Model: {model.model_id}")
            print(f"   Tier: {model.tier.value}")
            print(f"   Region: {model.region}")
            print(f"   Temperature: {model.temperature}")
            if model.description:
                print(f"   Description: {model.description}")

# Singleton instance
_configurator = None

def get_agent_configurator() -> GenieAgentConfigurator:
    """
    Get the global agent configurator instance.
    
    Returns:
        GenieAgentConfigurator instance
    """
    global _configurator
    if _configurator is None:
        _configurator = GenieAgentConfigurator()
    return _configurator

def initialize_configurator(profile: str = None, config_file: str = None) -> GenieAgentConfigurator:
    """
    Initialize or reinitialize the global configurator.
    
    Args:
        profile: Testing profile name
        config_file: Path to custom configuration file
        
    Returns:
        GenieAgentConfigurator instance
    """
    global _configurator
    _configurator = GenieAgentConfigurator(profile=profile, config_file=config_file)
    return _configurator
