# part_detail_manager.py
from typing import Dict, Optional, List
from data_structures import Part, PartType

class PartDetailManager:
    def __init__(self):
        self.current_part: Optional[Part] = None
        self.part_details: Dict[str, Dict] = {}
        
    def set_current_part(self, part: Part):
        """Aktif parçayı ayarla"""
        self.current_part = part
        if part.id not in self.part_details:
            self.part_details[part.id] = {
                'notes': '',
                'materials': [],
                'dimensions': {},
                'annotations': [],
                'revision_history': []
            }
    
    def add_note(self, note: str) -> bool:
        """Parçaya not ekle"""
        if self.current_part:
            self.part_details[self.current_part.id]['notes'] = note
            return True
        return False
    
    def add_material(self, material: str) -> bool:
        """Parçaya malzeme ekle"""
        if self.current_part:
            if material not in self.part_details[self.current_part.id]['materials']:
                self.part_details[self.current_part.id]['materials'].append(material)
            return True
        return False
    
    def set_dimensions(self, dimensions: Dict[str, float]) -> bool:
        """Parça boyutlarını ayarla"""
        if self.current_part:
            self.part_details[self.current_part.id]['dimensions'].update(dimensions)
            return True
        return False
    
    def add_annotation(self, annotation: Dict) -> bool:
        """Parçaya açıklama ekle"""
        if self.current_part:
            self.part_details[self.current_part.id]['annotations'].append(annotation)
            return True
        return False
    
    def add_revision(self, revision: Dict) -> bool:
        """Revizyon ekle"""
        if self.current_part:
            self.part_details[self.current_part.id]['revision_history'].append(revision)
            return True
        return False
    
    def get_part_details(self, part_id: str) -> Optional[Dict]:
        """Parça detaylarını getir"""
        return self.part_details.get(part_id)
    
    def get_notes(self) -> str:
        """Aktif parçanın notlarını getir"""
        if self.current_part:
            return self.part_details[self.current_part.id]['notes']
        return ''
    
    def get_materials(self) -> List[str]:
        """Aktif parçanın malzemelerini getir"""
        if self.current_part:
            return self.part_details[self.current_part.id]['materials']
        return []
    
    def get_dimensions(self) -> Dict:
        """Aktif parçanın boyutlarını getir"""
        if self.current_part:
            return self.part_details[self.current_part.id]['dimensions']
        return {}
    
    def get_annotations(self) -> List[Dict]:
        """Aktif parçanın açıklamalarını getir"""
        if self.current_part:
            return self.part_details[self.current_part.id]['annotations']
        return []
    
    def get_revision_history(self) -> List[Dict]:
        """Aktif parçanın revizyon geçmişini getir"""
        if self.current_part:
            return self.part_details[self.current_part.id]['revision_history']
        return []
    
    def clear_part_details(self, part_id: str) -> bool:
        """Parça detaylarını temizle"""
        if part_id in self.part_details:
            del self.part_details[part_id]
            if self.current_part and self.current_part.id == part_id:
                self.current_part = None
            return True
        return False