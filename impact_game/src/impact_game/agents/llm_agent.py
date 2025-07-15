import random
from typing import Dict, List
from ..agents.agent import Agent, WorkMode
from ..utils.llm_client import QwenLLMClient, LLMConfig, LLMPromptBuilder


class LLMAgent(Agent):
    """Agent that uses Qwen LLM for decision making"""
    
    def __init__(self, agent_id: str, initial_motto: str, initial_strategy: str, 
                 llm_config: LLMConfig = None):
        super().__init__(agent_id, initial_motto, initial_strategy)
        self.llm_client = QwenLLMClient(llm_config)
        self.prompt_builder = LLMPromptBuilder()
    
    def review_and_strategize(self, game_state: Dict, leaderboard: Dict) -> None:
        """Phase 1: Review status and form strategy using LLM"""
        try:
            prompt = self.prompt_builder.build_strategy_prompt(
                self.agent_id, self.state.motto, self.state.strategy,
                game_state, leaderboard
            )
            
            response = self.llm_client.call_llm(prompt)
            
            if response.startswith("UPDATE:"):
                new_strategy = response[7:].strip()
                self.state.strategy = new_strategy
                self.history.append({
                    "turn": game_state.get("turn", 0),
                    "action": "strategy_update",
                    "new_strategy": new_strategy
                })
            
        except Exception as e:
            # Fallback: keep current strategy
            print(f"Warning: LLM call failed for {self.agent_id} strategy review: {e}")
    
    def choose_project(self, available_projects: List[str], others_choices: List[str]) -> str:
        """Phase 2: Pick a project using LLM"""
        try:
            prompt = self.prompt_builder.build_project_choice_prompt(
                self.agent_id, self.state.motto, self.state.strategy,
                available_projects, others_choices
            )
            
            response = self.llm_client.call_llm(prompt).strip()
            
            # Validate response is in available projects
            if response in available_projects:
                return response
            else:
                # Fallback: random choice if LLM response is invalid
                print(f"Warning: {self.agent_id} LLM chose invalid project '{response}', using fallback")
                return random.choice(available_projects)
                
        except Exception as e:
            # Fallback: random choice
            print(f"Warning: LLM call failed for {self.agent_id} project choice: {e}")
            return random.choice(available_projects)
    
    def choose_work_mode(self, project: str, coworkers: List[str]) -> WorkMode:
        """Phase 3: Choose collaboration or competition using LLM"""
        try:
            prompt = self.prompt_builder.build_work_mode_prompt(
                self.agent_id, self.state.motto, self.state.strategy,
                project, coworkers
            )
            
            response = self.llm_client.call_llm(prompt).strip().upper()
            
            if "COLLABORATE" in response:
                return WorkMode.COLLABORATE
            elif "COMPETE" in response:
                return WorkMode.COMPETE
            else:
                # Fallback based on motto
                print(f"Warning: {self.agent_id} LLM gave unclear work mode '{response}', using fallback")
                return self._fallback_work_mode()
                
        except Exception as e:
            # Fallback based on motto
            print(f"Warning: LLM call failed for {self.agent_id} work mode: {e}")
            return self._fallback_work_mode()
    
    def _fallback_work_mode(self) -> WorkMode:
        """Fallback work mode based on agent's motto"""
        collaborative_keywords = ["help", "team", "together", "collaborate", "unity"]
        competitive_keywords = ["win", "compete", "excel", "best", "first"]
        
        motto_lower = self.state.motto.lower()
        
        if any(keyword in motto_lower for keyword in collaborative_keywords):
            return WorkMode.COLLABORATE
        elif any(keyword in motto_lower for keyword in competitive_keywords):
            return WorkMode.COMPETE
        else:
            # Default to collaboration
            return WorkMode.COLLABORATE


class HybridAgent(Agent):
    """Agent that mixes LLM decisions with rule-based fallbacks"""
    
    def __init__(self, agent_id: str, initial_motto: str, initial_strategy: str,
                 llm_config: LLMConfig = None, llm_probability: float = 0.8):
        super().__init__(agent_id, initial_motto, initial_strategy)
        self.llm_agent = LLMAgent(agent_id, initial_motto, initial_strategy, llm_config)
        self.llm_probability = llm_probability  # Probability of using LLM vs rule-based
    
    def review_and_strategize(self, game_state: Dict, leaderboard: Dict) -> None:
        """Use LLM with some probability, otherwise use simple rules"""
        if random.random() < self.llm_probability:
            self.llm_agent.review_and_strategize(game_state, leaderboard)
            self.state = self.llm_agent.state  # Sync state
        else:
            # Simple rule-based strategy update
            self._rule_based_strategy_update(game_state, leaderboard)
    
    def choose_project(self, available_projects: List[str], others_choices: List[str]) -> str:
        """Use LLM with some probability, otherwise use simple rules"""
        if random.random() < self.llm_probability:
            return self.llm_agent.choose_project(available_projects, others_choices)
        else:
            return self._rule_based_project_choice(available_projects, others_choices)
    
    def choose_work_mode(self, project: str, coworkers: List[str]) -> WorkMode:
        """Use LLM with some probability, otherwise use simple rules"""
        if random.random() < self.llm_probability:
            return self.llm_agent.choose_work_mode(project, coworkers)
        else:
            return self._rule_based_work_mode(coworkers)
    
    def _rule_based_strategy_update(self, game_state: Dict, leaderboard: Dict) -> None:
        """Simple rule-based strategy update"""
        my_credits = leaderboard.get(self.agent_id, 0)
        avg_credits = sum(leaderboard.values()) / len(leaderboard)
        
        if my_credits < avg_credits * 0.8:
            self.state.strategy = "focus on high-value opportunities and compete more"
        elif my_credits > avg_credits * 1.2:
            self.state.strategy = "maintain lead through strategic collaboration"
    
    def _rule_based_project_choice(self, available_projects: List[str], others_choices: List[str]) -> str:
        """Simple rule-based project selection"""
        # Prefer projects with fewer people (less competition)
        project_counts = {proj: others_choices.count(proj) for proj in available_projects}
        return min(project_counts, key=project_counts.get)
    
    def _rule_based_work_mode(self, coworkers: List[str]) -> WorkMode:
        """Simple rule-based work mode selection"""
        # Collaborate if 1-2 coworkers, compete if more
        return WorkMode.COLLABORATE if len(coworkers) <= 2 else WorkMode.COMPETE