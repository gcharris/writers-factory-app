"""
Core knowledge graph service using NetworkX for analysis and SQLAlchemy for persistence.
Handles all graph operations, queries, and analysis by loading from and saving to a database.
"""

import networkx as nx
import logging
from typing import List, Optional
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

# Correctly import from sibling module 'schema'
from .schema import Base, Node, Edge

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """
    Manages the knowledge graph, using a database for storage and NetworkX for in-memory analysis.
    """

    def __init__(self, session: Session):
        """
        Initialize the knowledge graph service with a database session.

        Args:
            session: A SQLAlchemy Session object for database operations.
        """
        self.session = session
        self.graph = nx.MultiDiGraph()
        self.load_graph_from_db()

    def load_graph_from_db(self):
        """
        Loads all nodes and edges from the database to build the in-memory NetworkX graph.
        """
        logger.info("Loading graph from database into memory...")
        nodes = self.session.query(Node).all()
        edges = self.session.query(Edge).all()

        for node in nodes:
            self.graph.add_node(node.id, **node.__dict__)

        for edge in edges:
            self.graph.add_edge(edge.source_id, edge.target_id, key=edge.relation_type, **edge.__dict__)
        
        logger.info(f"Graph loaded: {len(nodes)} nodes, {len(edges)} edges.")

    # ============================================================================
    # NODE (formerly Entity) OPERATIONS
    # ============================================================================

    def add_node(self, node: Node) -> Node:
        """
        Adds a new node to the database and the in-memory graph.

        Args:
            node: The SQLAlchemy Node object to add.

        Returns:
            The added node instance.
        """
        self.session.add(node)
        self.session.commit()
        self.graph.add_node(node.id, **node.__dict__)
        logger.info(f"Added node: {node.name} (ID: {node.id})")
        return node

    def get_node(self, node_id: int) -> Optional[Node]:
        """
        Get a node by its primary key ID.

        Args:
            node_id: The integer ID of the node.

        Returns:
            The Node object or None if not found.
        """
        return self.session.query(Node).get(node_id)

    def find_node_by_name(self, name: str) -> Optional[Node]:
        """
        Finds the first node with a matching name (case-insensitive).

        Args:
            name: The name of the node to find.

        Returns:
            The Node object or None if not found.
        """
        return self.session.query(Node).filter(Node.name.ilike(f"%{name}%")).first()

    def update_node(self, node_id: int, updates: dict) -> Optional[Node]:
        """
        Updates a node's attributes in the database and in-memory graph.

        Args:
            node_id: The ID of the node to update.
            updates: A dictionary of attributes to update.

        Returns:
            The updated Node object or None if not found.
        """
        node = self.get_node(node_id)
        if not node:
            logger.warning(f"Update failed: Node with ID {node_id} not found.")
            return None

        for key, value in updates.items():
            if hasattr(node, key):
                setattr(node, key, value)
        
        self.session.commit()

        # Update in-memory graph
        if self.graph.has_node(node_id):
            self.graph.nodes[node_id].update(node.__dict__)
        
        logger.info(f"Updated node ID {node_id}.")
        return node

    def delete_node(self, node_id: int) -> bool:
        """
        Deletes a node and its associated edges from the database and in-memory graph.

        Args:
            node_id: The ID of the node to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        node = self.get_node(node_id)
        if not node:
            logger.warning(f"Delete failed: Node with ID {node_id} not found.")
            return False

        # Delete associated edges first
        self.session.query(Edge).filter((Edge.source_id == node_id) | (Edge.target_id == node_id)).delete()
        
        self.session.delete(node)
        self.session.commit()

        if self.graph.has_node(node_id):
            self.graph.remove_node(node_id)
        
        logger.info(f"Deleted node ID {node_id} and its edges.")
        return True

    # ============================================================================
    # EDGE (formerly Relationship) OPERATIONS
    # ============================================================================

    def add_edge(self, edge: Edge) -> Optional[Edge]:
        """
        Adds a new edge to the database and the in-memory graph.

        Args:
            edge: The SQLAlchemy Edge object to add.

        Returns:
            The added edge, or None if source/target nodes don't exist.
        """
        # Ensure source and target nodes exist
        if not self.get_node(edge.source_id) or not self.get_node(edge.target_id):
            logger.error(f"Cannot add edge: Source ({edge.source_id}) or Target ({edge.target_id}) node not found.")
            return None

        self.session.add(edge)
        self.session.commit()
        self.graph.add_edge(edge.source_id, edge.target_id, key=edge.relation_type, **edge.__dict__)
        logger.info(f"Added edge: {edge.source_id} --[{edge.relation_type}]--> {edge.target_id}")
        return edge

    def get_edges(self, source_id: int = None, target_id: int = None) -> List[Edge]:
        """
        Retrieves edges based on source and/or target IDs.

        Args:
            source_id: The ID of the source node.
            target_id: The ID of the target node.

        Returns:
            A list of matching Edge objects.
        """
        query = self.session.query(Edge)
        if source_id:
            query = query.filter(Edge.source_id == source_id)
        if target_id:
            query = query.filter(Edge.target_id == target_id)
        return query.all()

    # ============================================================================
    # ANALYSIS METHODS (Operating on the in-memory NetworkX graph)
    # ============================================================================

    def find_path(self, source_id: int, target_id: int) -> Optional[List[int]]:
        """Find shortest path between two nodes."""
        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def get_central_entities(self, top_n: int = 10) -> List[tuple]:
        """Get most central entities using PageRank."""
        if self.graph.number_of_nodes() == 0:
            return []
        
        pagerank = nx.pagerank(self.graph)
        sorted_entities = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        return sorted_entities[:top_n]

    def get_stats(self) -> dict:
        """Get overall graph statistics."""
        num_nodes = self.graph.number_of_nodes()
        return {
            'nodes': num_nodes,
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph) if num_nodes > 1 else 0,
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(num_nodes, 1),
        }