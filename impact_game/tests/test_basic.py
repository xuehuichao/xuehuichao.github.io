import pytest
from impact_game.agents.agent import Agent, WorkMode
from impact_game.projects.project import Project, ProjectType
from impact_game.game.game_engine import GameEngine


class TestAgent:
    def test_agent_creation(self):
        agent = Agent("test_agent", "help others", "collaborate always")
        assert agent.agent_id == "test_agent"
        assert agent.state.motto == "help others"
        assert agent.state.strategy == "collaborate always"
        assert agent.state.credits == 0
    
    def test_update_credits(self):
        agent = Agent("test_agent", "motto", "strategy")
        agent.update_credits(100)
        assert agent.state.credits == 100
        agent.update_credits(50)
        assert agent.state.credits == 150


class TestProject:
    def test_collaboration_scoring(self):
        project = Project(ProjectType.CARING_FOR_ELDERS)
        project.add_participant("agent1", "collaborate")
        project.add_participant("agent2", "collaborate")
        
        result = project.calculate_results()
        
        assert result.is_collaboration == True
        assert result.total_value == 180
        assert result.credits_earned["agent1"] == 90
        assert result.credits_earned["agent2"] == 90
    
    def test_competition_scoring(self):
        project = Project(ProjectType.HELPING_WORKFORCE)
        project.add_participant("agent1", "collaborate")
        project.add_participant("agent2", "compete")
        
        result = project.calculate_results()
        
        assert result.is_collaboration == False
        assert result.total_value == 120
        # One agent should get 120, the other 0
        total_earned = sum(result.credits_earned.values())
        assert total_earned == 120


class TestGameEngine:
    def create_test_agents(self):
        return [
            Agent(f"agent_{i}", f"motto_{i}", f"strategy_{i}") 
            for i in range(1, 6)
        ]
    
    def test_game_creation(self):
        agents = self.create_test_agents()
        game = GameEngine(agents)
        assert len(game.agents) == 5
    
    def test_leaderboard(self):
        agents = self.create_test_agents()
        agents[0].update_credits(100)
        agents[1].update_credits(50)
        
        game = GameEngine(agents)
        leaderboard = game._get_current_leaderboard()
        
        assert leaderboard["agent_1"] == 100
        assert leaderboard["agent_2"] == 50
        assert leaderboard["agent_3"] == 0