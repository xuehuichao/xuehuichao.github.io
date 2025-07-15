#!/usr/bin/env python3
"""
Main entry point for the Impact Game simulation.
"""

import argparse
import sys
from pathlib import Path

from .simulation.runner import SimulationRunner
from .utils.config_loader import ConfigLoader, SimulationConfig


def main():
    parser = argparse.ArgumentParser(description="Run Impact Game simulations")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/default_agents.json",
        help="Path to agent configuration file"
    )
    parser.add_argument(
        "--simulations", 
        type=int, 
        default=100,
        help="Number of simulations to run"
    )
    parser.add_argument(
        "--turns", 
        type=int, 
        default=10,
        help="Number of turns per game"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data/results",
        help="Directory to save results"
    )
    parser.add_argument(
        "--create-sample-config",
        action="store_true",
        help="Create a sample agent configuration file"
    )
    
    args = parser.parse_args()
    
    if args.create_sample_config:
        output_path = "config/sample_agents.json"
        Path("config").mkdir(exist_ok=True)
        ConfigLoader.create_sample_config(output_path)
        return
    
    try:
        # Load agent configurations
        agent_configs = ConfigLoader.load_agent_configs(args.config)
        
        print(f"🎮 Starting Impact Game Simulation")
        print(f"📊 Running {args.simulations} simulations with {args.turns} turns each")
        print(f"👥 Using agents from: {args.config}")
        print(f"💾 Results will be saved to: {args.output_dir}")
        print("-" * 60)
        
        # Run simulation
        runner = SimulationRunner(args.output_dir)
        analysis = runner.run_experiment(
            agent_configs=agent_configs,
            num_simulations=args.simulations,
            num_turns=args.turns
        )
        
        # Print summary
        print("\n🎯 SIMULATION COMPLETE!")
        print(f"📈 Average team value: {analysis['avg_team_value']:.2f}")
        print(f"⚡ Efficiency: {analysis['efficiency']:.2%}")
        print(f"🤝 Collaboration rate: {analysis['collaboration_rate']:.2%}")
        
        print("\n🏆 Most successful mottos:")
        for motto, stats in list(analysis['winner_mottos'].items())[:3]:
            print(f"   '{motto}': {stats['count']} wins ({stats['percentage']:.1%})")
        
        print(f"\n📁 Detailed results saved to: {args.output_dir}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print(f"💡 Try running with --create-sample-config to create a sample configuration")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()