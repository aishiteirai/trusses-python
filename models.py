import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Support:
    # Equivalente a Support.cs
    restrain_x: bool = False
    restrain_y: bool = False


@dataclass
class Load:
    # Equivalente a Load.cs
    magnitude: float
    angle: float  # Em graus


@dataclass
class Node:
    # Equivalente a Node.cs
    id: int
    x: float
    y: float
    support: Optional[Support] = None
    load: Optional[Load] = None
    # Armazena os resultados calculados
    reaction_x: float = 0.0
    reaction_y: float = 0.0
    displacement_x: float = 0.0
    displacement_y: float = 0.0


@dataclass
class Member:
    # Equivalente a Member.cs
    id: int
    start_node: Node
    end_node: Node
    # MELHORIA PARA MDSOLIDS:
    # O código C# usava rigidez fixa. Aqui usamos física real.
    elastic_modulus: float = 200e9  # Ex: Aço em Pascal (Pa)
    area: float = 0.005  # Área da seção em m²

    # Resultados
    force: float = 0.0  # + Tração, - Compressão
    stress: float = 0.0  # Tensão


@dataclass
class Truss:
    # Equivalente a Truss.cs
    nodes: List[Node] = field(default_factory=list)
    members: List[Member] = field(default_factory=list)