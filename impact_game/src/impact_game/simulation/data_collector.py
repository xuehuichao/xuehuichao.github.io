from typing import List, Dict, Any
from collections import defaultdict, Counter

from ..game.game_engine import GameResult


class DataCollector:
    def analyze_experiment_results(self, results: List[GameResult], 
                                 agent_configs: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze results from multiple simulation runs"""
        total_simulations = len(results)
        
        # Collect winner and loser data
        winner_mottos = []
        loser_mottos = []
        winner_strategies = []
        loser_strategies = []
        team_values = []
        collaboration_counts = []
        
        # Create agent motto/strategy lookup
        agent_lookup = {f"agent_{i+1}": config for i, config in enumerate(agent_configs)}
        
        for result in results:
            team_values.append(result.total_team_value)
            
            # Analyze winners and losers
            for winner_id in result.winner_ids:
                if winner_id in agent_lookup:
                    winner_mottos.append(agent_lookup[winner_id]["motto"])
                    winner_strategies.append(agent_lookup[winner_id]["strategy"])
            
            if result.loser_id and result.loser_id in agent_lookup:
                loser_mottos.append(agent_lookup[result.loser_id]["motto"])
                loser_strategies.append(agent_lookup[result.loser_id]["strategy"])
            
            # Count collaborations
            collaboration_count = 0
            total_projects = 0
            for turn_result in result.turn_results:
                for project_result in turn_result.project_results:
                    total_projects += 1
                    if project_result.is_collaboration:
                        collaboration_count += 1
            
            collaboration_rate = collaboration_count / total_projects if total_projects > 0 else 0
            collaboration_counts.append(collaboration_rate)
        
        # Calculate statistics
        avg_team_value = sum(team_values) / len(team_values)
        theoretical_max = self._calculate_theoretical_max()
        efficiency = avg_team_value / theoretical_max
        
        winner_motto_stats = self._calculate_percentage_stats(winner_mottos, total_simulations)
        loser_motto_stats = self._calculate_percentage_stats(loser_mottos, total_simulations)
        winner_strategy_stats = self._calculate_percentage_stats(winner_strategies, total_simulations)
        loser_strategy_stats = self._calculate_percentage_stats(loser_strategies, total_simulations)
        
        avg_collaboration_rate = sum(collaboration_counts) / len(collaboration_counts)
        
        return {
            "total_simulations": total_simulations,
            "avg_team_value": avg_team_value,
            "theoretical_max": theoretical_max,
            "efficiency": efficiency,
            "winner_mottos": winner_motto_stats,
            "loser_mottos": loser_motto_stats,
            "winner_strategies": winner_strategy_stats,
            "loser_strategies": loser_strategy_stats,
            "collaboration_rate": avg_collaboration_rate,
            "team_values": team_values,
            "individual_collaboration_rates": collaboration_counts
        }
    
    def _calculate_percentage_stats(self, items: List[str], total: int) -> Dict[str, Dict[str, Any]]:
        """Calculate count and percentage statistics for a list of items"""
        counter = Counter(items)
        stats = {}
        for item, count in counter.items():
            stats[item] = {
                "count": count,
                "percentage": count / total
            }
        return dict(sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True))
    
    def _calculate_theoretical_max(self) -> float:
        """Calculate theoretical maximum team value per game"""
        # Theoretical max: 10 turns * 3 projects * optimal collaboration
        # Best case: all 5 agents collaborate on same project each turn
        # This gives 300 credits per turn, but only 3 projects max per turn
        # So: 10 turns * 300 credits = 3000 (if everyone always collaborated on one project)
        # More realistic max: 10 turns * (300 + 180 + 100) = 5800 (3 projects with 3,2,1 agents)
        return 10 * 300  # Conservative estimate assuming best collaboration per turn
    
    def generate_detailed_story(self, result: GameResult, agent_configs: List[Dict[str, str]]) -> str:
        """Generate a detailed narrative of a single game"""
        agent_lookup = {f"agent_{i+1}": config for i, config in enumerate(agent_configs)}
        
        story = ["IMPACT GAME STORY", "=" * 50, ""]
        
        # Introduction
        story.append("AGENTS:")
        for agent_id, config in agent_lookup.items():
            story.append(f"  {agent_id}: \"{config['motto']}\" - {config['strategy']}")
        story.append("")
        
        # Turn by turn narrative
        for turn_result in result.turn_results:
            story.append(f"TURN {turn_result.turn_number}:")
            story.append(f"  Project assignments: {turn_result.project_assignments}")
            
            for project_result in turn_result.project_results:
                project_name = project_result.project_type.value
                participants = project_result.participants
                
                if project_result.is_collaboration:
                    story.append(f"  📈 {project_name}: {len(participants)} agents collaborated")
                    story.append(f"     Each earned: {project_result.credits_earned[participants[0]]} credits")
                else:
                    winner = max(project_result.credits_earned.items(), key=lambda x: x[1])[0]
                    story.append(f"  ⚔️  {project_name}: Competition mode - {winner} won!")
                    story.append(f"     Winner earned: {project_result.credits_earned[winner]} credits")
            
            story.append(f"  Leaderboard: {turn_result.leaderboard}")
            story.append("")
        
        # Final results
        story.append("FINAL RESULTS:")
        story.append(f"  🏆 Winners: {result.winner_ids}")
        story.append(f"  💀 Eliminated: {result.loser_id}")
        story.append(f"  🏗️  Total team value: {result.total_team_value}")
        story.append(f"  📊 Final scores: {result.final_leaderboard}")
        
        return "\n".join(story)