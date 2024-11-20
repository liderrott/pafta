# data_structures.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import uuid

class PartType(Enum):
    FRONT_VIEW = "Ön Görünüş"
    SIDE_VIEW = "Yan Görünüş"
    TOP_VIEW = "Üst Görünüş"
    PERSPECTIVE = "Perspektif"
    DETAIL = "Detay"
    DIMENSIONS = "Ölçüler"
    SECTION = "Kesit"
    ASSEMBLY = "Montaj"
    PARTS_LIST = "Parça Listesi"

@dataclass
class Part:
    id: str
    type: PartType
    name: str
    size: tuple
    position: Optional[tuple] = None
    rotation: int = 0
    scale: float = 1.0
    image_path: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class Template:
    id: str
    name: str
    description: str
    layout_rules: Dict
    default_parts: List[PartType]
    
class Project:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.pages = []
        self.current_page = 0
        self.metadata = {
            'created_at': None,
            'modified_at': None,
            'author': None,
            'version': '1.0'
        }