import json
from pathlib import Path
from typing import List, Dict, Any


class ConfigLoader:
    @staticmethod
    def load_agent_configs(config_path: str) -> List[Dict[str, str]]:
        """Load agent configurations from JSON file"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            configs = json.load(f)
        
        # Validate configuration structure
        ConfigLoader._validate_agent_configs(configs)
        return configs
    
    @staticmethod
    def _validate_agent_configs(configs: List[Dict[str, str]]) -> None:
        """Validate agent configuration structure"""
        if not isinstance(configs, list):
            raise ValueError("Agent configs must be a list")
        
        if len(configs) != 5:
            raise ValueError("Exactly 5 agent configurations required")
        
        for i, config in enumerate(configs):
            if not isinstance(config, dict):
                raise ValueError(f"Agent config {i} must be a dictionary")
            
            required_fields = ["motto", "strategy"]
            for field in required_fields:
                if field not in config:
                    raise ValueError(f"Agent config {i} missing required field: {field}")
                if not isinstance(config[field], str):
                    raise ValueError(f"Agent config {i} field '{field}' must be a string")
    
    @staticmethod
    def create_sample_config(output_path: str) -> None:
        """Create a sample agent configuration file"""
        sample_configs = [
            {
                "motto": "help others!",
                "strategy": "work on projects that need the most help, and always embrace collaboration"
            },
            {
                "motto": "win at all costs",
                "strategy": "focus on high-value opportunities and compete aggressively"
            },
            {
                "motto": "balance is key",
                "strategy": "adapt strategy based on current situation and team dynamics"
            },
            {
                "motto": "strength in unity",
                "strategy": "promote collaboration and build lasting partnerships"
            },
            {
                "motto": "efficient execution",
                "strategy": "minimize risk, maximize consistent returns through smart choices"
            }
        ]
        
        with open(output_path, 'w') as f:
            json.dump(sample_configs, f, indent=4)
        
        print(f"Sample configuration created at: {output_path}")


class SimulationConfig:
    def __init__(self, config_dict: Dict[str, Any] = None):
        config_dict = config_dict or {}
        
        self.num_simulations = config_dict.get("num_simulations", 100)
        self.num_turns = config_dict.get("num_turns", 10)
        self.output_dir = config_dict.get("output_dir", "data/results")
        self.agent_config_path = config_dict.get("agent_config_path", "config/default_agents.json")
        self.random_seed = config_dict.get("random_seed", None)
    
    @classmethod
    def from_file(cls, config_path: str) -> "SimulationConfig":
        """Load simulation configuration from JSON file"""
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return cls(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            "num_simulations": self.num_simulations,
            "num_turns": self.num_turns,
            "output_dir": self.output_dir,
            "agent_config_path": self.agent_config_path,
            "random_seed": self.random_seed
        }