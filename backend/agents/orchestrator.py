import os
import random
from typing import List, Dict, Any

# Add root to path to allow sibling imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.registry import AgentRegistry

class SceneTournament:
    """
    Manages the running of a multi-agent tournament for drafting scenes.
    """
    def __init__(self, registry: AgentRegistry):
        """
        Initializes the tournament orchestrator.

        Args:
            registry: An instance of AgentRegistry.
        """
        self.registry = registry

    def run_tournament(self, scene_context: str, agent_ids: List[str], strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Runs a drafting tournament with a given set of agents, each using a specific strategy.

        Args:
            scene_context: The contextual information for the scene draft.
            agent_ids: A list of agent IDs to participate in the tournament.
            strategies: A list of strategy dictionaries to be assigned to agents.

        Returns:
            A list of draft dictionaries, each containing the agent and the generated text.
        """
        print(f"--- Running Tournament for Scene ---\nContext: '{scene_context}'")
        print(f"Participants: {', '.join(agent_ids)}\n")
        
        drafts = []
        for i, agent_id in enumerate(agent_ids):
            agent_config = self.registry.get_agent(agent_id)
            if not agent_config:
                print(f"Warning: Agent '{agent_id}' not found in registry. Skipping.")
                continue
            
            # Assign a strategy to the agent
            strategy = strategies[i % len(strategies)] # Cycle through strategies
            print(f"Assigning strategy '{strategy['name']}' to agent '{agent_config['name']}'.")

            # Mock generating a draft that incorporates the strategy
            mock_draft_text = (
                f"DRAFT by '{agent_config['name']}'.\n"
                f"STRATEGY: {strategy['name']}.\n"
                f"DIRECTIVE: {strategy['directive']}\n---\n"
                f"Based on the scene context, this draft focuses on the assigned directive. "
                f"The character should feel conflicted, and the prose reflects this strategic focus."
            )
            
            # Mock token usage and log cost
            mock_tokens_used = random.randint(1000, 5000)
            self.registry.log_transaction(agent_id, mock_tokens_used)
            
            drafts.append({
                "agent": agent_config,
                "strategy": strategy,
                "draft_text": mock_draft_text,
                "tokens_used": mock_tokens_used
            })
            print(f"'{agent_config['name']}' completed its draft ({mock_tokens_used} tokens).")

        return drafts


class DraftCritic:
    """
    Evaluates scene drafts based on a set of scoring dimensions.
    """
    # As per docs/02_scene_pipeline.md, Section 3, Step 3
    SCORING_DIMENSIONS = [
        "Voice Authenticity",
        "Narrative Impact",
        "Philosophy Integration",
        "Character Alignment",
        "Graph Consistency"
    ]

    def evaluate_drafts(self, drafts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scores drafts and returns a sorted list with the winner first.

        Args:
            drafts: A list of draft dictionaries from the tournament.

        Returns:
            A sorted list of results, including scores and a total.
        """
        print("\n--- Critic is Evaluating Drafts ---")
        results = []
        for draft in drafts:
            scores = {dim: round(random.uniform(6.0, 9.8), 1) for dim in self.SCORING_DIMENSIONS}
            total_score = sum(scores.values())
            
            results.append({
                "agent_name": draft["agent"]["name"],
                "strategy_name": draft["strategy"]["name"],
                "draft_text": draft["draft_text"],
                "scores": scores,
                "total_score": round(total_score, 2)
            })
            print(f"Scored '{draft['agent']['name']}' (Strategy: {draft['strategy']['name']}) with a total of {total_score:.2f}.")
        
        # Sort by total score, descending
        sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
        return sorted_results


if __name__ == "__main__":
    import yaml
    print("--- Mock Tournament & Critique (with Strategies) ---")
    
    try:
        # 1. Initialize Registry
        registry_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agents.yaml')
        registry = AgentRegistry(config_path=registry_config_path)

        # 2. Load Strategies from reference file
        strategies_path = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'reference_skills', 'reference_multiplier.yaml')
        with open(strategies_path, 'r') as f:
            strategies_config = yaml.safe_load(f)
        strategies = strategies_config.get('strategies', [])

        # 3. Initialize Tournament and Critic
        tournament = SceneTournament(registry)
        critic = DraftCritic()

        # 4. Select agents for the tournament
        tournament_agents = [
            agent['id'] for agent in registry.list_enabled_agents() 
            if "tournament" in agent.get('use_cases', [])
        ]
        
        if not tournament_agents or not strategies:
            print("Could not find tournament agents or strategies.")
        else:
            # 5. Run the tournament
            mock_context = "Alice confronts Bob about the missing data."
            drafts = tournament.run_tournament(mock_context, tournament_agents, strategies)

            # 6. Evaluate the drafts
            results = critic.evaluate_drafts(drafts)

            # 7. Print results
            print("\n--- FINAL TOURNAMENT RESULTS ---")
            winner = results[0]
            print(f"\n🏆 Winner: {winner['agent_name']} with '{winner['strategy_name']}' (Score: {winner['total_score']}) 🏆")
            
            print("\n--- Scoreboard ---")
            for i, result in enumerate(results):
                print(f"{i+1}. {result['agent_name']} ({result['strategy_name']}) - Score: {result['total_score']}")
                for dim, score in result['scores'].items():
                    print(f"   - {dim}: {score}")
                print("-" * 20)

            # 8. Print final cost summary
            print("\n--- Final Cost Report ---")
            registry.get_summary()

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
