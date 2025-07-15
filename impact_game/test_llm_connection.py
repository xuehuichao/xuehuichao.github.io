#!/usr/bin/env python3
"""
Test script to verify Qwen LLM connection and functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from impact_game.utils.llm_client import QwenLLMClient, LLMConfig
from impact_game.agents.llm_agent import LLMAgent


def test_basic_connection():
    """Test basic LLM connection"""
    print("🔍 Testing basic LLM connection...")
    
    client = QwenLLMClient()
    
    # Test connection
    if client.test_connection():
        print("✅ LLM connection successful!")
    else:
        print("❌ LLM connection failed!")
        return False
    
    # Test available models
    models = client.get_available_models()
    if models:
        print(f"📋 Available models: {models}")
    else:
        print("⚠️  Could not retrieve model list")
    
    return True


def test_simple_prompt():
    """Test a simple prompt"""
    print("\n🧪 Testing simple prompt...")
    
    client = QwenLLMClient()
    
    try:
        response = client.call_llm("What is 2+2? Answer briefly.")
        print(f"📝 LLM Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Simple prompt failed: {e}")
        return False


def test_agent_decision():
    """Test LLM agent decision making"""
    print("\n🤖 Testing LLM agent decision making...")
    
    try:
        agent = LLMAgent(
            agent_id="test_agent",
            initial_motto="help others!",
            initial_strategy="collaborate when possible"
        )
        
        # Test project choice
        available_projects = ["caring for the elders", "helping the workforce", "caring for the youth"]
        others_choices = ["caring for the elders"]
        
        choice = agent.choose_project(available_projects, others_choices)
        print(f"🎯 Agent chose project: {choice}")
        
        # Test work mode choice
        work_mode = agent.choose_work_mode("caring for the elders", ["agent_2"])
        print(f"⚙️  Agent chose work mode: {work_mode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent decision test failed: {e}")
        return False


def test_game_simulation():
    """Test a simple game simulation with LLM agents"""
    print("\n🎮 Testing mini game simulation...")
    
    try:
        from impact_game.agents.llm_agent import LLMAgent
        from impact_game.game.game_engine import GameEngine
        
        # Create LLM agents with different personalities
        agents = [
            LLMAgent("agent_1", "help others!", "collaborate when possible"),
            LLMAgent("agent_2", "excellence through competition", "compete strategically"),
        ]
        
        # Add simple rule-based agents to fill the team
        from impact_game.agents.agent import Agent, WorkMode
        import random
        
        class SimpleAgent(Agent):
            def choose_project(self, available_projects, others_choices):
                return random.choice(available_projects)
            
            def choose_work_mode(self, project, coworkers):
                return WorkMode.COLLABORATE
        
        agents.extend([
            SimpleAgent("agent_3", "steady progress", "simple rules"),
            SimpleAgent("agent_4", "team player", "simple rules"),
            SimpleAgent("agent_5", "balanced approach", "simple rules"),
        ])
        
        print(f"🎯 Created {len(agents)} agents (2 LLM, 3 simple)")
        
        # Run a single turn
        game = GameEngine(agents)
        turn_result = game.run_turn()
        
        print(f"✅ Turn completed successfully!")
        print(f"📊 Project assignments: {turn_result.project_assignments}")
        print(f"🏆 Leaderboard: {turn_result.leaderboard}")
        
        return True
        
    except Exception as e:
        print(f"❌ Game simulation test failed: {e}")
        return False


def main():
    print("🚀 QWEN LLM CONNECTION TEST")
    print("=" * 50)
    
    # Test basic connection
    if not test_basic_connection():
        print("\n❌ Basic connection failed. Check if Qwen LLM is running on localhost:11434")
        print("💡 Start Qwen with: ollama serve")
        return
    
    # Test simple prompt
    if not test_simple_prompt():
        print("\n❌ Simple prompt test failed")
        return
    
    # Test agent decisions
    if not test_agent_decision():
        print("\n❌ Agent decision test failed")
        return
    
    # Test game simulation
    if not test_game_simulation():
        print("\n❌ Game simulation test failed")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Your Qwen LLM is ready for the Impact Game!")
    
    print("\n🎮 Next steps:")
    print("1. Run full simulation: python -m impact_game.main --simulations 10")
    print("2. Create LLM agent configs and run experiments")


if __name__ == "__main__":
    main()