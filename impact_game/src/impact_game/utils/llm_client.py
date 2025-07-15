import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5:32b-instruct"
    timeout: int = 30


class QwenLLMClient:
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.session = requests.Session()
    
    def call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Call Qwen LLM with the given prompt"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.config.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Qwen LLM: {e}")
        except KeyError as e:
            raise ValueError(f"Unexpected LLM response format: {e}")
    
    def test_connection(self) -> bool:
        """Test if the LLM is accessible"""
        try:
            response = self.call_llm("Hello, are you working?")
            return len(response) > 0
        except Exception:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = self.session.get(f"{self.config.base_url}/api/tags")
            response.raise_for_status()
            
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception:
            return []


class LLMPromptBuilder:
    @staticmethod
    def build_strategy_prompt(agent_id: str, motto: str, current_strategy: str, 
                            game_state: Dict, leaderboard: Dict) -> str:
        """Build prompt for strategy review phase"""
        turn = game_state.get("turn", 0)
        history = game_state.get("history", [])
        
        prompt = f"""You are {agent_id}, an agent in a competitive team mission.

YOUR IDENTITY:
- Motto: "{motto}"
- Current Strategy: "{current_strategy}"

CURRENT SITUATION (Turn {turn}):
- Leaderboard: {leaderboard}
- Your current credits: {leaderboard.get(agent_id, 0)}

MISSION CONTEXT:
You're in a team of 5 agents competing on important projects. At the end of 10 turns, the lowest performer gets eliminated.

Based on the current situation, should you update your strategy? Consider:
1. Your current standing
2. Other agents' apparent strategies
3. How to balance collaboration vs competition

Respond with either:
- KEEP: [brief reason why current strategy still works]
- UPDATE: [new strategy description]"""

        if history:
            prompt += f"\n\nRECENT HISTORY:\n"
            for turn_result in history[-3:]:  # Last 3 turns
                prompt += f"Turn {turn_result['turn_number']}: {turn_result['project_assignments']}\n"
        
        return prompt
    
    @staticmethod
    def build_project_choice_prompt(agent_id: str, motto: str, strategy: str,
                                  available_projects: List[str], others_choices: List[str]) -> str:
        """Build prompt for project selection phase"""
        prompt = f"""You are {agent_id} with motto "{motto}" and strategy "{strategy}".

PROJECT SELECTION:
Available projects: {available_projects}
Others have chosen: {others_choices}

Choose ONE project from the available list. Consider:
1. Your motto and strategy
2. Which projects others have chosen (potential collaborators/competitors)
3. Strategic positioning for this turn

Respond with only the project name exactly as listed."""
        
        return prompt
    
    @staticmethod
    def build_work_mode_prompt(agent_id: str, motto: str, strategy: str,
                             project: str, coworkers: List[str]) -> str:
        """Build prompt for work mode selection phase"""
        prompt = f"""You are {agent_id} with motto "{motto}" and strategy "{strategy}".

WORK MODE DECISION:
- Project: {project}
- Coworkers on this project: {coworkers}

Choose your work mode:
- COLLABORATE: Work together, split credits equally (more total value with more people)
- COMPETE: Race to finish first, winner takes all $120

SCORING:
- Collaboration: 1 person=$100, 2 people=$90 each, 3 people=$80 each, 4 people=$70 each, 5 people=$60 each
- Competition: One random winner gets $120, others get $0

Respond with either "COLLABORATE" or "COMPETE" and a brief reason."""
        
        return prompt