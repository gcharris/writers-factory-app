import yaml
import os
from typing import List, Dict, Any, Optional

# Note: This module requires PyYAML. Install with: pip install pyyaml
# It also assumes the presence of a .env file for API keys.

class AgentRegistry:
    """
    Loads and manages agent configurations from a YAML file, and tracks API costs.
    """
    def __init__(self, config_path: str = "agents.yaml"):
        """
        Initializes the registry by loading agent configurations.

        Args:
            config_path: Path to the agents.yaml configuration file.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Agent configuration file not found at: {config_path}")

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self._agents = {agent['id']: agent for agent in self.config.get('agents', [])}
        self._costs = {agent_id: 0.0 for agent_id in self._agents}
        self._load_api_keys()

    def _load_api_keys(self):
        """Loads API keys from environment variables specified in the config."""
        for agent_id, agent_config in self._agents.items():
            if 'api_key_env' in agent_config:
                api_key = os.getenv(agent_config['api_key_env'])
                if not api_key:
                    print(f"Warning: Environment variable {agent_config['api_key_env']} for agent {agent_id} is not set.")
                self._agents[agent_id]['api_key'] = api_key


    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the configuration for a specific agent.

        Args:
            agent_id: The unique identifier for the agent.

        Returns:
            A dictionary with the agent's configuration, or None if not found.
        """
        return self._agents.get(agent_id)

    def list_enabled_agents(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all agents that are marked as enabled in the config.

        Returns:
            A list of agent configuration dictionaries.
        """
        return [agent for agent in self._agents.values() if agent.get('enabled', False)]

    def log_transaction(self, agent_id: str, total_tokens: int):
        """
        Calculates and logs the cost of an API call.

        Args:
            agent_id: The ID of the agent used.
            total_tokens: The total number of tokens used in the transaction.
        
        Raises:
            ValueError: If the agent_id is not found.
        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found in registry.")

        cost_per_1k = agent.get('cost_per_1k_tokens', 0.0)
        transaction_cost = (total_tokens / 1000) * cost_per_1k
        self._costs[agent_id] += transaction_cost

        # Check against monthly budget if applicable
        max_spend = agent.get('max_monthly_spend')
        if max_spend and self._costs[agent_id] > max_spend:
            print(f"Warning: Agent {agent_id} has exceeded its monthly budget of ${max_spend:.2f}. "
                  f"Current spend: ${self._costs[agent_id]:.2f}")


    def get_total_cost(self, agent_id: Optional[str] = None) -> float:
        """
        Gets the total accumulated cost.

        Args:
            agent_id: If specified, returns the cost for only that agent.
                      Otherwise, returns the total cost for all agents.

        Returns:
            The total cost in USD.
        """
        if agent_id:
            return self._costs.get(agent_id, 0.0)
        return sum(self._costs.values())

    def get_summary(self) -> None:
        """Prints a summary of current costs for all agents."""
        print("--- Agent Cost Summary ---")
        for agent_id, total_cost in self._costs.items():
            agent_name = self.get_agent(agent_id).get('name', agent_id)
            print(f"{agent_name}: ${total_cost:.4f}")
        print("--------------------------")
        print(f"Total All Agents: ${self.get_total_cost():.4f}")
        print("--------------------------")

if __name__ == '__main__':
    # Example Usage
    try:
        # Assumes agents.yaml is in the project root, so we go up one level from backend/agents
        config_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'agents.yaml')
        
        registry = AgentRegistry(config_path=config_file_path)

        # List enabled agents
        print("Enabled Agents:")
        for agent_data in registry.list_enabled_agents():
            print(f"- {agent_data['name']} ({agent_data['provider']})")
        
        print("\n--- Logging Transactions ---")
        # Simulate some API calls
        registry.log_transaction('claude-sonnet-3-5', 15000) # 15k tokens
        registry.log_transaction('gemini-pro-1-5', 30000)  # 30k tokens
        registry.log_transaction('claude-sonnet-3-5', 25000) # 25k tokens
        print("Transactions logged.")

        # Get a summary
        print("\n--- Final Report ---")
        registry.get_summary()

    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
