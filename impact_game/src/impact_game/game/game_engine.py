from typing import List, Dict, Tuple
import random
from dataclasses import dataclass

from ..agents.agent import Agent
from ..projects.project import Project, ProjectType, ProjectResult


@dataclass
class TurnResult:
    turn_number: int
    project_assignments: Dict[str, str]  # agent_id -> project_type
    project_results: List[ProjectResult]
    leaderboard: Dict[str, int]  # agent_id -> total_credits


@dataclass
class GameResult:
    winner_ids: List[str]
    loser_id: str
    final_leaderboard: Dict[str, int]
    turn_results: List[TurnResult]
    total_team_value: int


class GameEngine:
    def __init__(self, agents: List[Agent]):
        self.agents = agents
        self.turn_results = []
        self.current_turn = 0
        
    def run_game(self, num_turns: int = 10) -> GameResult:
        """Run the complete game for specified number of turns"""
        for turn in range(1, num_turns + 1):
            self.current_turn = turn
            turn_result = self.run_turn()
            self.turn_results.append(turn_result)
        
        return self._calculate_final_results()
    
    def run_turn(self) -> TurnResult:
        """Run a single turn of the game"""
        # Phase 1: Review and strategize
        current_leaderboard = self._get_current_leaderboard()
        game_state = self._get_game_state()
        
        for agent in self.agents:
            agent.review_and_strategize(game_state, current_leaderboard)
        
        # Phase 2: Project selection (random order)
        project_assignments = self._conduct_project_selection()
        
        # Phase 3: Work and create value
        project_results = self._conduct_work_phase(project_assignments)
        
        # Update agent credits
        for result in project_results:
            for agent_id, credits in result.credits_earned.items():
                agent = self._get_agent_by_id(agent_id)
                agent.update_credits(credits)
        
        return TurnResult(
            turn_number=self.current_turn,
            project_assignments=project_assignments,
            project_results=project_results,
            leaderboard=self._get_current_leaderboard()
        )
    
    def _conduct_project_selection(self) -> Dict[str, str]:
        """Phase 2: Agents select projects in random order"""
        project_assignments = {}
        available_projects = [proj.value for proj in ProjectType]
        others_choices = []
        
        # Randomize agent order
        agent_order = self.agents.copy()
        random.shuffle(agent_order)
        
        for agent in agent_order:
            chosen_project = agent.choose_project(available_projects, others_choices)
            project_assignments[agent.agent_id] = chosen_project
            others_choices.append(chosen_project)
        
        return project_assignments
    
    def _conduct_work_phase(self, project_assignments: Dict[str, str]) -> List[ProjectResult]:
        """Phase 3: Agents work on projects and earn credits"""
        # Group agents by project
        projects_to_agents = {}
        for agent_id, project_type in project_assignments.items():
            if project_type not in projects_to_agents:
                projects_to_agents[project_type] = []
            projects_to_agents[project_type].append(agent_id)
        
        project_results = []
        
        for project_type_str, agent_ids in projects_to_agents.items():
            # Find the corresponding ProjectType enum
            project_type = ProjectType(project_type_str)
            project = Project(project_type)
            
            # Each agent chooses their work mode
            for agent_id in agent_ids:
                agent = self._get_agent_by_id(agent_id)
                coworkers = [id for id in agent_ids if id != agent_id]
                work_mode = agent.choose_work_mode(project_type_str, coworkers)
                project.add_participant(agent_id, work_mode.value)
            
            # Calculate and store results
            result = project.calculate_results()
            project_results.append(result)
        
        return project_results
    
    def _get_current_leaderboard(self) -> Dict[str, int]:
        """Get current leaderboard with agent credits"""
        return {agent.agent_id: agent.state.credits for agent in self.agents}
    
    def _get_game_state(self) -> Dict:
        """Get current game state for agents to review"""
        return {
            "turn": self.current_turn,
            "history": self.turn_results,
            "leaderboard": self._get_current_leaderboard()
        }
    
    def _get_agent_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    def _calculate_final_results(self) -> GameResult:
        """Calculate final game results"""
        final_leaderboard = self._get_current_leaderboard()
        
        # Find winner(s) and loser
        max_credits = max(final_leaderboard.values())
        min_credits = min(final_leaderboard.values())
        
        winners = [agent_id for agent_id, credits in final_leaderboard.items() 
                  if credits == max_credits]
        losers = [agent_id for agent_id, credits in final_leaderboard.items() 
                 if credits == min_credits]
        
        # Calculate total team value
        total_team_value = sum(result.total_value 
                              for turn_result in self.turn_results 
                              for result in turn_result.project_results)
        
        return GameResult(
            winner_ids=winners,
            loser_id=losers[0] if losers else None,
            final_leaderboard=final_leaderboard,
            turn_results=self.turn_results,
            total_team_value=total_team_value
        )