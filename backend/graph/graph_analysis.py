"""
Graph Analysis for GraphRAG.

Advanced graph analysis for narrative structure including:
- Community detection (plot clustering)
- Bridge character identification
- Narrative tension calculation

Part of GraphRAG Phase 5 - Enhancements.
"""

import logging
from typing import Dict, List, Any, Optional, TYPE_CHECKING

import networkx as nx

if TYPE_CHECKING:
    from .graph_service import KnowledgeGraphService

logger = logging.getLogger(__name__)


class GraphAnalyzer:
    """
    Advanced graph analysis for narrative structure.

    Uses NetworkX algorithms to detect:
    - Character communities (plot threads)
    - Key bridge characters
    - Narrative tension points
    """

    def __init__(self, graph_service: Optional['KnowledgeGraphService'] = None):
        """
        Initialize GraphAnalyzer.

        Args:
            graph_service: KnowledgeGraphService instance (creates one if not provided)
        """
        self._graph_service = graph_service
        logger.info("GraphAnalyzer initialized")

    def _ensure_graph(self) -> 'KnowledgeGraphService':
        """Lazy-load graph service to avoid circular imports."""
        if self._graph_service is None:
            from .graph_service import KnowledgeGraphService
            self._graph_service = KnowledgeGraphService()
        return self._graph_service

    def detect_communities(self) -> Dict[str, List[str]]:
        """
        Detect character communities using Louvain algorithm.

        Communities often represent:
        - Subplots
        - Character factions
        - Thematic clusters

        Returns:
            Dict mapping community names to lists of character names
        """
        graph = self._ensure_graph()
        G = graph.to_networkx()

        # Filter to character nodes only
        character_nodes = [n for n, d in G.nodes(data=True)
                         if d.get("type") == "CHARACTER"]

        if len(character_nodes) < 2:
            return {"main": character_nodes}

        H = G.subgraph(character_nodes).copy()

        try:
            # Louvain community detection
            from networkx.algorithms.community import louvain_communities
            communities = louvain_communities(H.to_undirected())

            result = {}
            for i, community in enumerate(communities):
                # Name communities based on size
                if i == 0:
                    name = "primary_cast"
                elif i == 1:
                    name = "secondary_cast"
                else:
                    name = f"community_{i}"
                result[name] = list(community)

            logger.info(f"Detected {len(result)} character communities")
            return result
        except ImportError:
            logger.warning("Louvain algorithm not available - using connected components")
            # Fallback to connected components
            components = list(nx.connected_components(H.to_undirected()))
            return {f"group_{i}": list(c) for i, c in enumerate(components)}
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return {"main": character_nodes}

    def find_bridge_characters(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find characters that bridge multiple communities.

        These are often:
        - Protagonists (connect all threads)
        - Plot catalysts (bring groups together)
        - Antagonists (create conflict between groups)

        Args:
            top_k: Number of bridge characters to return

        Returns:
            List of dicts with character info and centrality scores
        """
        graph = self._ensure_graph()
        G = graph.to_networkx()

        bridges = []
        try:
            # Betweenness centrality identifies bridge nodes
            centrality = nx.betweenness_centrality(G)

            for node, score in sorted(centrality.items(), key=lambda x: -x[1])[:top_k * 2]:
                node_data = G.nodes[node]
                if node_data.get("type") == "CHARACTER":
                    bridges.append({
                        "name": node,
                        "centrality": round(score, 4),
                        "type": node_data.get("type"),
                        "description": node_data.get("description"),
                        "role": self._infer_role(score, len(bridges))
                    })
                    if len(bridges) >= top_k:
                        break

            logger.info(f"Found {len(bridges)} bridge characters")
        except Exception as e:
            logger.warning(f"Bridge detection failed: {e}")

        return bridges

    def _infer_role(self, centrality: float, rank: int) -> str:
        """Infer character role from centrality score and rank."""
        if rank == 0 and centrality > 0.1:
            return "protagonist"
        elif rank <= 2 and centrality > 0.05:
            return "major_character"
        elif centrality > 0.02:
            return "supporting_character"
        else:
            return "minor_character"

    def calculate_tension(self) -> Dict[str, Any]:
        """
        Calculate narrative tension based on graph structure.

        Tension indicators:
        - Number of active HINDERS edges
        - Unresolved FORESHADOWS
        - CONTRADICTS edges
        - CHALLENGES edges (protagonist's flaw being tested)

        Returns:
            Dict with tension score, level, and breakdown
        """
        graph = self._ensure_graph()
        G = graph.to_networkx()

        # Count tension-creating edges
        edge_counts = {
            "HINDERS": 0,
            "FORESHADOWS": 0,
            "CONTRADICTS": 0,
            "CHALLENGES": 0,
            "CONFLICTS_WITH": 0,
        }

        for _, _, d in G.edges(data=True):
            relation = d.get("relation_type") or d.get("relation", "")
            if relation in edge_counts:
                edge_counts[relation] += 1

        # Calculate tension score (weighted)
        weights = {
            "HINDERS": 2.0,
            "FORESHADOWS": 1.5,
            "CONTRADICTS": 3.0,
            "CHALLENGES": 2.5,
            "CONFLICTS_WITH": 1.5,
        }

        weighted_sum = sum(edge_counts[k] * weights[k] for k in edge_counts)
        total_edges = G.number_of_edges() or 1

        # Normalize to 0-1 range with sigmoid-like scaling
        raw_score = weighted_sum / (total_edges + 10)  # +10 for smoothing
        tension_score = min(raw_score, 1.0)

        # Determine level
        if tension_score > 0.6:
            level = "high"
        elif tension_score > 0.3:
            level = "medium"
        else:
            level = "low"

        result = {
            "tension_score": round(tension_score, 3),
            "level": level,
            "indicators": {
                "active_obstacles": edge_counts["HINDERS"],
                "unresolved_foreshadowing": edge_counts["FORESHADOWS"],
                "contradictions": edge_counts["CONTRADICTS"],
                "flaw_challenges": edge_counts["CHALLENGES"],
                "active_conflicts": edge_counts["CONFLICTS_WITH"],
            },
            "total_edges": total_edges,
            "recommendation": self._get_tension_recommendation(level, edge_counts)
        }

        logger.info(f"Tension calculated: {level} ({tension_score:.3f})")
        return result

    def _get_tension_recommendation(
        self,
        level: str,
        counts: Dict[str, int]
    ) -> str:
        """Generate recommendation based on tension analysis."""
        if level == "low":
            if counts["HINDERS"] == 0:
                return "Consider adding obstacles to increase narrative tension"
            if counts["CHALLENGES"] == 0:
                return "The protagonist's flaw hasn't been challenged - consider testing their weakness"
            return "Tension is low - good for setup scenes, may need escalation soon"
        elif level == "high":
            if counts["CONTRADICTS"] > 2:
                return "High contradiction count - review for consistency issues"
            return "High tension - ensure payoff scenes are planned"
        else:
            return "Balanced tension level"

    def analyze_pacing(self) -> Dict[str, Any]:
        """
        Analyze narrative pacing based on edge type distribution.

        Returns:
            Dict with pacing metrics and recommendations
        """
        graph = self._ensure_graph()
        G = graph.to_networkx()

        # Categorize edges by narrative function
        action_types = {"CAUSES", "HINDERS", "CHALLENGES", "CONFLICTS_WITH"}
        setup_types = {"FORESHADOWS", "KNOWS", "LOCATED_IN", "OWNS"}
        resolution_types = {"CALLBACKS", "REVEALS"}

        counts = {"action": 0, "setup": 0, "resolution": 0, "other": 0}

        for _, _, d in G.edges(data=True):
            relation = d.get("relation_type") or d.get("relation", "")
            if relation in action_types:
                counts["action"] += 1
            elif relation in setup_types:
                counts["setup"] += 1
            elif relation in resolution_types:
                counts["resolution"] += 1
            else:
                counts["other"] += 1

        total = sum(counts.values()) or 1

        ratios = {
            "action_ratio": round(counts["action"] / total, 3),
            "setup_ratio": round(counts["setup"] / total, 3),
            "resolution_ratio": round(counts["resolution"] / total, 3),
        }

        # Determine pacing character
        if ratios["action_ratio"] > 0.5:
            pacing = "fast"
            recommendation = "High action density - ensure emotional beats for reader recovery"
        elif ratios["setup_ratio"] > 0.6:
            pacing = "slow"
            recommendation = "Heavy setup - consider accelerating toward payoffs"
        elif ratios["resolution_ratio"] > 0.3:
            pacing = "concluding"
            recommendation = "Many resolutions happening - appropriate for act endings"
        else:
            pacing = "balanced"
            recommendation = "Balanced pacing across narrative elements"

        return {
            "pacing": pacing,
            "edge_counts": counts,
            "ratios": ratios,
            "recommendation": recommendation
        }

    def get_narrative_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive narrative structure summary.

        Returns:
            Dict with communities, bridges, tension, pacing, and stats
        """
        graph = self._ensure_graph()

        communities = self.detect_communities()
        bridges = self.find_bridge_characters()
        tension = self.calculate_tension()
        pacing = self.analyze_pacing()

        # Get node type counts
        node_counts = {}
        for node_type in ["CHARACTER", "LOCATION", "OBJECT", "EVENT", "THEME", "CONCEPT"]:
            nodes = graph.get_nodes_by_type(node_type)
            if nodes:
                node_counts[node_type.lower()] = len(nodes)

        return {
            "communities": communities,
            "community_count": len(communities),
            "bridge_characters": bridges,
            "tension": tension,
            "pacing": pacing,
            "graph_stats": {
                "total_nodes": graph.get_stats()["nodes"],
                "total_edges": graph.get_stats()["edges"],
                **node_counts
            },
            "health_indicators": {
                "has_protagonist": any(b["role"] == "protagonist" for b in bridges),
                "has_active_tension": tension["level"] != "low",
                "has_foreshadowing": tension["indicators"]["unresolved_foreshadowing"] > 0,
                "has_flaw_challenges": tension["indicators"]["flaw_challenges"] > 0,
            }
        }


# Singleton instance
_graph_analyzer: Optional[GraphAnalyzer] = None


def get_graph_analyzer(graph_service: Optional['KnowledgeGraphService'] = None) -> GraphAnalyzer:
    """
    Get or create the singleton GraphAnalyzer instance.

    Args:
        graph_service: Optional KnowledgeGraphService to use

    Returns:
        GraphAnalyzer instance
    """
    global _graph_analyzer

    if _graph_analyzer is None or graph_service is not None:
        _graph_analyzer = GraphAnalyzer(graph_service)

    return _graph_analyzer


def reset_graph_analyzer():
    """Reset the singleton instance (useful for testing)."""
    global _graph_analyzer
    _graph_analyzer = None
