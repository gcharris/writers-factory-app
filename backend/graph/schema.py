from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    node_type = Column(String)  # e.g., 'scene', 'character', 'location', 'event'
    name = Column(String)
    description = Column(String)
    content = Column(String) # Textual content if applicable. Can be used for Scene text, Character bio, etc.

    # Backrefs for edges (relationships)
    outgoing_edges = relationship("Edge", back_populates="source_node", foreign_keys="[Edge.source_id]")
    incoming_edges = relationship("Edge", back_populates="target_node", foreign_keys="[Edge.target_id]")

    scene_metadata = relationship("SceneMetadata", back_populates="node", uselist=False)

    def __repr__(self):
        return f"<Node(id={self.id}, type='{self.node_type}', name='{self.name}')>"


class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('nodes.id'))
    target_id = Column(Integer, ForeignKey('nodes.id'))
    relation_type = Column(String)  # e.g., 'related_to', 'part_of', 'occurs_in'

    source_node = relationship("Node", back_populates="outgoing_edges", foreign_keys=[source_id])
    target_node = relationship("Node", back_populates="incoming_edges", foreign_keys=[target_id])

    def __repr__(self):
        return f"<Edge(id={self.id}, source={self.source_id}, target={self.target_id}, type='{self.relation_type}')>"



class SceneMetadata(Base):
    __tablename__ = 'scene_metadata'

    node_id = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    draft_number = Column(Integer, default=0)
    last_edited = Column(DateTime, default=datetime.utcnow)
    is_locked = Column(Boolean, default=False)

    # Scoring dimensions from the spec.
    voice_authenticity = Column(Float)
    pacing_tension = Column(Float)
    dialogue_naturalness = Column(Float)
    show_dont_tell = Column(Float)
    character_development = Column(Float)
    graph_consistency = Column(Float)

    node = relationship("Node", back_populates="scene_metadata")


    def __repr__(self):
        return f"<SceneMetadata(node_id={self.node_id}, draft={self.draft_number}, locked={self.is_locked})>"
