# optimization_engine.py
from typing import List, Dict, Tuple, Optional
from data_structures import Part, PartType
from layout_system import LayoutManager
import numpy as np

class OptimizationEngine:
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager
        self.weights = {
            'spacing': 0.3,
            'alignment': 0.3,
            'grouping': 0.2,
            'balance': 0.2
        }

    def optimize(self, parts: List[Part]) -> Optional[Dict[str, Tuple[int, int]]]:
        best_layout = None
        best_score = float('-inf')
        
        for _ in range(100):  # 100 farklı deneme
            layout = self._generate_layout(parts)
            if layout:
                score = self._evaluate_layout(layout, parts)
                if score > best_score:
                    best_score = score
                    best_layout = layout
                    
        return best_layout

    def _generate_layout(self, parts: List[Part]) -> Optional[Dict[str, Tuple[int, int]]]:
        # Parçaları rastgele karıştır
        shuffled_parts = parts.copy()
        np.random.shuffle(shuffled_parts)
        
        # Layout manager'ı kullanarak yerleştirmeyi dene
        if self.layout_manager.auto_layout(shuffled_parts):
            return {
                part.id: part.position 
                for part in shuffled_parts
            }
        return None

    def _evaluate_layout(self, layout: Dict[str, Tuple[int, int]], parts: List[Part]) -> float:
        score = 0.0
        
        # Boşluk değerlendirmesi
        spacing_score = self._evaluate_spacing(layout)
        score += spacing_score * self.weights['spacing']
        
        # Hizalama değerlendirmesi
        alignment_score = self._evaluate_alignment(layout)
        score += alignment_score * self.weights['alignment']
        
        # Grup değerlendirmesi
        grouping_score = self._evaluate_grouping(layout, parts)
        score += grouping_score * self.weights['grouping']
        
        # Denge değerlendirmesi
        balance_score = self._evaluate_balance(layout)
        score += balance_score * self.weights['balance']
        
        return score

    def _evaluate_spacing(self, layout: Dict[str, Tuple[int, int]]) -> float:
        # Parçalar arası boşlukları değerlendir
        used_cells = set()
        for position in layout.values():
            used_cells.add(position)
        
        total_cells = self.layout_manager.grid.rows * self.layout_manager.grid.cols
        empty_cells = total_cells - len(used_cells)
        
        return 1.0 - (empty_cells / total_cells)

    def _evaluate_alignment(self, layout: Dict[str, Tuple[int, int]]) -> float:
        # Yatay ve dikey hizalamaları değerlendir
        rows = set()
        cols = set()
        
        for row, col in layout.values():
            rows.add(row)
            cols.add(col)
            
        row_alignment = len(rows) / self.layout_manager.grid.rows
        col_alignment = len(cols) / self.layout_manager.grid.cols
        
        return (row_alignment + col_alignment) / 2

    def _evaluate_grouping(self, layout: Dict[str, Tuple[int, int]], parts: List[Part]) -> float:
        # Benzer parçaların gruplandırılmasını değerlendir
        groups = {}
        for part in parts:
            if part.id in layout:
                if part.type not in groups:
                    groups[part.type] = []
                groups[part.type].append(layout[part.id])
        
        score = 0.0
        for positions in groups.values():
            if len(positions) > 1:
                # Grup içi mesafeleri hesapla
                distances = []
                for i, pos1 in enumerate(positions):
                    for pos2 in positions[i+1:]:
                        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                        distances.append(distance)
                
                if distances:
                    avg_distance = sum(distances) / len(distances)
                    score += 1.0 / (1.0 + avg_distance)
                    
        return score / len(groups) if groups else 0.0

    def _evaluate_balance(self, layout: Dict[str, Tuple[int, int]]) -> float:
        # Yerleşimin görsel dengesini değerlendir
        if not layout:
            return 0.0
            
        rows = [pos[0] for pos in layout.values()]
        cols = [pos[1] for pos in layout.values()]
        
        row_center = sum(rows) / len(rows)
        col_center = sum(cols) / len(cols)
        
        ideal_row_center = (self.layout_manager.grid.rows - 1) / 2
        ideal_col_center = (self.layout_manager.grid.cols - 1) / 2
        
        row_balance = 1.0 - abs(row_center - ideal_row_center) / self.layout_manager.grid.rows
        col_balance = 1.0 - abs(col_center - ideal_col_center) / self.layout_manager.grid.cols
        
        return (row_balance + col_balance) / 2

class LayoutOptimizer:
    def __init__(self, layout_manager: LayoutManager):
        self.engine = OptimizationEngine(layout_manager)
    
    def optimize_layout(self, parts: List[Part]) -> Optional[Dict[str, Tuple[int, int]]]:
        return self.engine.optimize(parts)