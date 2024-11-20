# template_manager.py
class TemplateManager:
    def __init__(self):
        self.templates = {}
        self.load_default_templates()
    
    def load_default_templates(self):
        self.templates = {
            'standard': {
                'name': 'Standart Layout',
                'description': 'Temel 3x3 yerleşim',
                'layout': {
                    'grid_size': (3, 3),
                    'default_parts': ['Ön Görünüş', 'Yan Görünüş', 'Üst Görünüş']
                }
            },
            'detailed': {
                'name': 'Detaylı Layout',
                'description': 'Detay görünümlü yerleşim',
                'layout': {
                    'grid_size': (3, 3),
                    'default_parts': ['Ön Görünüş', 'Detay', 'Kesit']
                }
            }
        }
    
    def get_template(self, template_id):
        return self.templates.get(template_id)
    
    def add_template(self, template_id, template_data):
        self.templates[template_id] = template_data