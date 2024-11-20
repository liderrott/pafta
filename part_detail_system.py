# part_detail_system.py
class PartDetailManager:
    def __init__(self):
        self.max_parts_per_page = 6
        self.parts = {}
        
    def add_part(self, part_code, part_data):
        if len(self.parts) >= self.max_parts_per_page:
            raise Exception("Maksimum parça sayısına ulaşıldı!")
        
        self.parts[part_code] = {
            'name': part_data.get('name', ''),
            'specs': part_data.get('specs', {}),
            'material': part_data.get('material', ''),
            'image': part_data.get('image', None)
        }
    
    def validate_part(self, part_data):
        required_fields = ['name', 'specs', 'material']
        return all(field in part_data for field in required_fields)