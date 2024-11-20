# template_system.py
import json
import os
from typing import Dict, List, Optional
from data_structures import Template, PartType

class TemplateManager:
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.templates_path = "templates/"
        os.makedirs(self.templates_path, exist_ok=True)
        self.load_default_templates()
        
    def load_default_templates(self):
        default_templates = {
            'standard': {
                'name': 'Standart Layout',
                'description': 'Temel 3x3 yerleşim',
                'layout_rules': {
                    'front_view': {'position': (0,0), 'size': (2,2)},
                    'side_view': {'position': (0,2), 'size': (2,1)},
                    'top_view': {'position': (2,0), 'size': (1,2)}
                },
                'default_parts': [
                    PartType.FRONT_VIEW,
                    PartType.SIDE_VIEW,
                    PartType.TOP_VIEW
                ]
            },
            'detailed': {
                'name': 'Detaylı Layout',
                'description': 'Detay görünümlü yerleşim',
                'layout_rules': {
                    'front_view': {'position': (0,0), 'size': (2,2)},
                    'detail': {'position': (0,2), 'size': (1,1)},
                    'section': {'position': (1,2), 'size': (1,1)},
                    'dimensions': {'position': (2,0), 'size': (1,3)}
                },
                'default_parts': [
                    PartType.FRONT_VIEW,
                    PartType.DETAIL,
                    PartType.SECTION,
                    PartType.DIMENSIONS
                ]
            }
        }
        
        for template_id, data in default_templates.items():
            self.templates[template_id] = Template(
                id=template_id,
                name=data['name'],
                description=data['description'],
                layout_rules=data['layout_rules'],
                default_parts=data['default_parts']
            )
            
    def save_template(self, template: Template) -> bool:
        try:
            template_data = {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'layout_rules': template.layout_rules,
                'default_parts': [part.value for part in template.default_parts]
            }
            
            path = os.path.join(self.templates_path, f"{template.id}.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Şablon kaydetme hatası: {str(e)}")
            return False
            
    def load_template(self, template_id: str) -> Optional[Template]:
        try:
            path = os.path.join(self.templates_path, f"{template_id}.json")
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return Template(
                    id=data['id'],
                    name=data['name'],
                    description=data['description'],
                    layout_rules=data['layout_rules'],
                    default_parts=[PartType(part) for part in data['default_parts']]
                )
        except Exception as e:
            print(f"Şablon yükleme hatası: {str(e)}")
            return None

    def get_all_templates(self) -> List[Template]:
        """Tüm şablonları listele"""
        return list(self.templates.values())

    def delete_template(self, template_id: str) -> bool:
        """Şablon sil"""
        try:
            path = os.path.join(self.templates_path, f"{template_id}.json")
            if os.path.exists(path):
                os.remove(path)
                if template_id in self.templates:
                    del self.templates[template_id]
                return True
            return False
        except Exception as e:
            print(f"Şablon silme hatası: {str(e)}")
            return False