import json
import datetime
from typing import List, Dict, Any
from pathlib import Path

from ..agents.agent import Agent
from ..game.game_engine import GameEngine, GameResult
from .data_collector import DataCollector


class SimulationRunner:
    def __init__(self, data_output_dir: str = "data/results"):
        self.data_output_dir = Path(data_output_dir)
        self.data_output_dir.mkdir(parents=True, exist_ok=True)
        self.data_collector = DataCollector()
    
    def create_agents(self, agent_configs: List[Dict[str, str]]) -> List[Agent]:
        """Create agents from configuration"""
        agents = []
        for i, config in enumerate(agent_configs):
            agent = Agent(
                agent_id=f"agent_{i+1}",
                initial_motto=config["motto"],
                initial_strategy=config["strategy"]
            )
            agents.append(agent)
        return agents
    
    def run_single_simulation(self, agent_configs: List[Dict[str, str]], 
                            num_turns: int = 10) -> GameResult:
        """Run a single simulation game"""
        agents = self.create_agents(agent_configs)
        game_engine = GameEngine(agents)
        return game_engine.run_game(num_turns)
    
    def run_experiment(self, agent_configs: List[Dict[str, str]], 
                      num_simulations: int = 100, num_turns: int = 10) -> Dict[str, Any]:
        """Run multiple simulations and collect data"""
        all_results = []
        
        print(f"Running {num_simulations} simulations...")
        
        for sim_num in range(1, num_simulations + 1):
            if sim_num % 10 == 0:
                print(f"Completed {sim_num}/{num_simulations} simulations")
            
            result = self.run_single_simulation(agent_configs, num_turns)
            all_results.append(result)
        
        # Analyze results
        analysis = self.data_collector.analyze_experiment_results(all_results, agent_configs)
        
        # Save results
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self._save_experiment_data(all_results, analysis, timestamp)
        
        print(f"Experiment completed! Results saved to {self.data_output_dir}")
        return analysis
    
    def _save_experiment_data(self, results: List[GameResult], 
                            analysis: Dict[str, Any], timestamp: str) -> None:
        """Save experiment data to files"""
        # Save raw results
        raw_data_file = self.data_output_dir / f"raw_results_{timestamp}.json"
        with open(raw_data_file, 'w') as f:
            json.dump([self._serialize_game_result(result) for result in results], 
                     f, indent=2)
        
        # Save analysis
        analysis_file = self.data_output_dir / f"analysis_{timestamp}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Save summary report
        summary_file = self.data_output_dir / f"summary_{timestamp}.txt"
        with open(summary_file, 'w') as f:
            self._write_summary_report(f, analysis)
    
    def _serialize_game_result(self, result: GameResult) -> Dict[str, Any]:
        """Convert GameResult to serializable dictionary"""
        return {
            "winner_ids": result.winner_ids,
            "loser_id": result.loser_id,
            "final_leaderboard": result.final_leaderboard,
            "total_team_value": result.total_team_value,
            "turn_results": [
                {
                    "turn_number": turn.turn_number,
                    "project_assignments": turn.project_assignments,
                    "leaderboard": turn.leaderboard,
                    "project_results": [
                        {
                            "project_type": proj.project_type.value,
                            "participants": proj.participants,
                            "work_modes": proj.work_modes,
                            "credits_earned": proj.credits_earned,
                            "is_collaboration": proj.is_collaboration,
                            "total_value": proj.total_value
                        }
                        for proj in turn.project_results
                    ]
                }
                for turn in result.turn_results
            ]
        }
    
    def _write_summary_report(self, file, analysis: Dict[str, Any]) -> None:
        """Write a human-readable summary report"""
        file.write("IMPACT GAME SIMULATION SUMMARY\n")
        file.write("=" * 50 + "\n\n")
        
        file.write(f"Total Simulations: {analysis['total_simulations']}\n")
        file.write(f"Average Team Value: {analysis['avg_team_value']:.2f}\n")
        file.write(f"Theoretical Maximum: {analysis['theoretical_max']:.2f}\n")
        file.write(f"Efficiency: {analysis['efficiency']:.2%}\n\n")
        
        file.write("WINNER ANALYSIS:\n")
        for motto, stats in analysis['winner_mottos'].items():
            file.write(f"  '{motto}': {stats['count']} wins ({stats['percentage']:.1%})\n")
        
        file.write("\nLOSER ANALYSIS:\n")
        for motto, stats in analysis['loser_mottos'].items():
            file.write(f"  '{motto}': {stats['count']} losses ({stats['percentage']:.1%})\n")
        
        file.write("\nCOLLABORATION RATE:\n")
        file.write(f"  Overall: {analysis['collaboration_rate']:.2%}\n")
        
        file.write("\nTOP PERFORMING STRATEGIES:\n")
        for strategy, stats in list(analysis['winner_strategies'].items())[:3]:
            file.write(f"  '{strategy[:50]}...': {stats['count']} wins\n")