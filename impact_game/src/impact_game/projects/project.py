from typing import List, Dict
from enum import Enum
from dataclasses import dataclass


class ProjectType(Enum):
    CARING_FOR_ELDERS = "caring for the elders"
    HELPING_WORKFORCE = "helping the workforce"
    CARING_FOR_YOUTH = "caring for the youth"


@dataclass
class ProjectResult:
    project_type: ProjectType
    participants: List[str]
    work_modes: Dict[str, str]  # agent_id -> work_mode
    credits_earned: Dict[str, int]  # agent_id -> credits
    is_collaboration: bool
    total_value: int


class Project:
    COLLABORATION_VALUES = {
        1: 100,
        2: 180,
        3: 240,
        4: 280,
        5: 300
    }
    
    COMPETITION_VALUE = 120
    
    def __init__(self, project_type: ProjectType):
        self.project_type = project_type
        self.participants = []
        self.work_modes = {}
    
    def add_participant(self, agent_id: str, work_mode: str) -> None:
        """Add a participant with their chosen work mode"""
        self.participants.append(agent_id)
        self.work_modes[agent_id] = work_mode
    
    def calculate_results(self) -> ProjectResult:
        """Calculate the results based on participants and their work modes"""
        num_participants = len(self.participants)
        
        # Check if all participants chose collaboration
        all_collaborate = all(mode == "collaborate" for mode in self.work_modes.values())
        
        if all_collaborate and num_participants > 0:
            # Collaboration scenario
            total_value = self.COLLABORATION_VALUES[num_participants]
            credits_per_agent = total_value // num_participants
            credits_earned = {agent_id: credits_per_agent for agent_id in self.participants}
            is_collaboration = True
        else:
            # Competition scenario - one random winner gets all credits
            import random
            winner = random.choice(self.participants)
            total_value = self.COMPETITION_VALUE
            credits_earned = {agent_id: 0 for agent_id in self.participants}
            credits_earned[winner] = total_value
            is_collaboration = False
        
        return ProjectResult(
            project_type=self.project_type,
            participants=self.participants.copy(),
            work_modes=self.work_modes.copy(),
            credits_earned=credits_earned,
            is_collaboration=is_collaboration,
            total_value=total_value
        )