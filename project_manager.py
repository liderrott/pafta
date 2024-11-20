# project_manager.py
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from data_structures import Project, Part
from template_manager import TemplateManager
from layout_system import LayoutManager

class ProjectManager:
    def __init__(self):
        self.current_project: Optional[Project] = None
        self.template_manager = TemplateManager()
        self.layout_manager = LayoutManager()
        
        # Temel dizinleri oluştur
        self.project_path = "projects/"
        self.autosave_path = "autosave/"
        os.makedirs(self.project_path, exist_ok=True)
        os.makedirs(self.autosave_path, exist_ok=True)

    def create_project(self, name: str) -> Project:
        project = Project(name)
        project.metadata.update({
            'created_at': datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        })
        self.current_project = project
        return project

    def save_project(self, path: str) -> bool:
        if not self.current_project:
            return False
            
        try:
            project_data = {
                'id': self.current_project.id,
                'name': self.current_project.name,
                'metadata': self.current_project.metadata,
                'pages': [self.serialize_page(page) for page in self.current_project.pages]
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=4)
                
            # Otomatik yedek oluştur
            self._create_autosave()
            return True
            
        except Exception as e:
            print(f"Kaydetme hatası: {str(e)}")
            return False

    def load_project(self, path: str) -> bool:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            project = Project(data['name'])
            project.id = data['id']
            project.metadata = data['metadata']
            project.pages = [self.deserialize_page(page) for page in data['pages']]
            
            self.current_project = project
            return True
            
        except Exception as e:
            print(f"Yükleme hatası: {str(e)}")
            return False

    def serialize_page(self, page: dict) -> dict:
        return {
            'parts': [self.serialize_part(part) for part in page.get('parts', [])],
            'layout': page.get('layout', {})
        }

    def deserialize_page(self, page_data: dict) -> dict:
        return {
            'parts': [self.deserialize_part(part) for part in page_data.get('parts', [])],
            'layout': page_data.get('layout', {})
        }

    def serialize_part(self, part: Part) -> dict:
        return {
            'id': part.id,
            'type': part.type.value,
            'name': part.name,
            'size': part.size,
            'position': part.position,
            'rotation': part.rotation,
            'scale': part.scale,
            'image_path': part.image_path
        }

    def deserialize_part(self, part_data: dict) -> Part:
        return Part(
            id=part_data['id'],
            type=PartType(part_data['type']),
            name=part_data['name'],
            size=tuple(part_data['size']),
            position=tuple(part_data['position']) if part_data.get('position') else None,
            rotation=part_data.get('rotation', 0),
            scale=part_data.get('scale', 1.0),
            image_path=part_data.get('image_path')
        )

    def _create_autosave(self) -> None:
        if self.current_project:
            autosave_path = os.path.join(
                self.autosave_path,
                f"{self.current_project.name}_autosave.pafta"
            )
            self.save_project(autosave_path)