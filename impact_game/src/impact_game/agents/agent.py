from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class WorkMode(Enum):
    COLLABORATE = "collaborate"
    COMPETE = "compete"


@dataclass
class AgentState:
    motto: str
    strategy: str
    credits: int = 0
    coworker_guesses: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        if self.coworker_guesses is None:
            self.coworker_guesses = {}


class Agent:
    def __init__(self, agent_id: str, initial_motto: str, initial_strategy: str):
        self.agent_id = agent_id
        self.state = AgentState(motto=initial_motto, strategy=initial_strategy)
        self.history = []
    
    def review_and_strategize(self, game_state: Dict, leaderboard: Dict) -> None:
        """Phase 1: Review status and form strategy"""
        pass
    
    def choose_project(self, available_projects: List[str], others_choices: List[str]) -> str:
        """Phase 2: Pick a project"""
        pass
    
    def choose_work_mode(self, project: str, coworkers: List[str]) -> WorkMode:
        """Phase 3: Choose collaboration or competition"""
        pass
    
    def update_credits(self, earned_credits: int) -> None:
        """Update agent's total credits"""
        self.state.credits += earned_credits
    
    def update_coworker_guess(self, agent_id: str, motto_guess: str, strategy_guess: str) -> None:
        """Update guess about another agent's motto and strategy"""
        self.state.coworker_guesses[agent_id] = {
            "motto": motto_guess,
            "strategy": strategy_guess
        }