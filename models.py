import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Support:
    restrain_x: bool = False
    restrain_y: bool = False


@dataclass
class Load:
    magnitude: float
    angle: float  


@dataclass
class Node:
    id: int
    x: float
    y: float
    support: Optional[Support] = None
    load: Optional[Load] = None
    reaction_x: float = 0.0
    reaction_y: float = 0.0
    displacement_x: float = 0.0
    displacement_y: float = 0.0


@dataclass
class Member:
    id: int
    start_node: Node
    end_node: Node
    elastic_modulus: float = 200e9  
    area: float = 0.005 
    force: float = 0.0
    stress: float = 0.0


@dataclass
class Truss:
    nodes: List[Node] = field(default_factory=list)
    members: List[Member] = field(default_factory=list)