# layout_system.py
from typing import List, Tuple, Optional, Dict
from data_structures import Part, PartType
import numpy as np

class Grid:
    def __init__(self, rows: int = 3, cols: int = 3):
        self.rows = rows
        self.cols = cols
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.parts: Dict[str, Part] = {}  # part_id -> Part

    def place_part(self, part: Part, position: Tuple[int, int]) -> bool:
        row, col = position
        if self.can_place_part(part, position):
            # Parçayı yerleştir
            part.position = position
            self.parts[part.id] = part
            
            # Grid hücrelerini güncelle
            width, height = part.size
            for i in range(height):
                for j in range(width):
                    if row + i < self.rows and col + j < self.cols:
                        self.grid[row + i][col + j] = part.id
            return True
        return False

    def can_place_part(self, part: Part, position: Tuple[int, int]) -> bool:
        row, col = position
        width, height = part.size
        
        # Grid sınırlarını kontrol et
        if row + height > self.rows or col + width > self.cols:
            return False
            
        # Çakışma kontrolü
        for i in range(height):
            for j in range(width):
                if row + i < self.rows and col + j < self.cols:
                    if self.grid[row + i][col + j] is not None:
                        return False
        return True

    def remove_part(self, part_id: str) -> bool:
        if part_id in self.parts:
            part = self.parts[part_id]
            row, col = part.position
            width, height = part.size
            
            # Grid hücrelerini temizle
            for i in range(height):
                for j in range(width):
                    if row + i < self.rows and col + j < self.cols:
                        self.grid[row + i][col + j] = None
                        
            del self.parts[part_id]
            return True
        return False

class LayoutManager:
    def __init__(self):
        self.grid = Grid()
        self.default_sizes = {
            PartType.FRONT_VIEW: (2, 2),
            PartType.SIDE_VIEW: (1, 2),
            PartType.TOP_VIEW: (2, 1),
            PartType.PERSPECTIVE: (1, 1),
            PartType.DETAIL: (1, 1),
            PartType.DIMENSIONS: (1, 1),
            PartType.SECTION: (1, 1),
            PartType.ASSEMBLY: (2, 2),
            PartType.PARTS_LIST: (1, 2)
        }

    def auto_layout(self, parts: List[Part]) -> bool:
        # Grid'i temizle
        self.grid = Grid()
        
        # Parçaları boyutlarına göre sırala (büyükten küçüğe)
        sorted_parts = sorted(
            parts,
            key=lambda p: p.size[0] * p.size[1],
            reverse=True
        )
        
        # Her parça için uygun pozisyon bul
        for part in sorted_parts:
            placed = False
            for row in range(self.grid.rows):
                for col in range(self.grid.cols):
                    if self.grid.place_part(part, (row, col)):
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                return False
        return True

    def optimize_layout(self, parts: List[Part]) -> Optional[Dict[str, Tuple[int, int]]]:
        best_layout = None
        best_score = float('-inf')
        
        for _ in range(100):  # 100 farklı deneme
            self.grid = Grid()
            shuffled_parts = parts.copy()
            np.random.shuffle(shuffled_parts)
            
            if self.auto_layout(shuffled_parts):
                score = self._evaluate_layout()
                if score > best_score:
                    best_score = score
                    best_layout = {
                        part.id: part.position 
                        for part in shuffled_parts
                    }
        
        return best_layout

    def _evaluate_layout(self) -> float:
        score = 0.0
        
        # Boşluk değerlendirmesi
        empty_cells = sum(
            1 for row in self.grid.grid 
            for cell in row 
            if cell is None
        )
        score -= empty_cells * 0.5
        
        # Hizalama değerlendirmesi
        for row in range(self.grid.rows):
            if all(cell is not None for cell in self.grid.grid[row]):
                score += 2.0
                
        for col in range(self.grid.cols):
            if all(self.grid.grid[row][col] is not None for row in range(self.grid.rows)):
                score += 2.0
        
        return score