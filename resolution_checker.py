# resolution_checker.py
from PIL import Image
from typing import Dict, Tuple, Optional
import os

class ResolutionChecker:
    def __init__(self):
        self.min_dpi = 300
        self.min_dimensions = {
            'A0': (9933, 14043),  # 300 DPI'da A0 boyutu
            'A1': (7016, 9933),   # 300 DPI'da A1 boyutu
            'A2': (4961, 7016),   # 300 DPI'da A2 boyutu
            'A3': (3508, 4961),   # 300 DPI'da A3 boyutu
            'A4': (2480, 3508),   # 300 DPI'da A4 boyutu
            'A5': (1748, 2480)    # 300 DPI'da A5 boyutu
        }
        
        self.optimal_dpi = {
            'print': 300,
            'web': 72,
            'preview': 150
        }
    
    def check_image(self, image_path: str, format: str = 'A3') -> Dict:
        """Görüntü çözünürlüğünü ve boyutlarını kontrol et"""
        try:
            if not os.path.exists(image_path):
                return {'error': 'Dosya bulunamadı'}
                
            with Image.open(image_path) as img:
                width, height = img.size
                dpi = img.info.get('dpi', (72, 72))
                
                min_width, min_height = self.min_dimensions.get(format, (0, 0))
                
                result = {
                    'valid': width >= min_width and height >= min_height and dpi[0] >= self.min_dpi,
                    'current_size': (width, height),
                    'current_dpi': dpi,
                    'required_size': (min_width, min_height),
                    'required_dpi': self.min_dpi,
                    'format': format,
                    'file_size': os.path.getsize(image_path) / (1024 * 1024)  # MB cinsinden
                }
                
                if not result['valid']:
                    result['issues'] = self._get_issues(width, height, dpi[0], min_width, min_height)
                
                return result
                
        except Exception as e:
            return {'error': str(e)}
    
    def _get_issues(self, width: int, height: int, dpi: int, min_width: int, min_height: int) -> list:
        """Tespit edilen sorunları listele"""
        issues = []
        if width < min_width or height < min_height:
            issues.append(f"Görüntü boyutu yetersiz: {width}x{height}px (Minimum: {min_width}x{min_height}px)")
        if dpi < self.min_dpi:
            issues.append(f"DPI değeri düşük: {dpi} (Minimum: {self.min_dpi})")
        return issues
    
    def get_required_dimensions(self, format: str) -> Optional[Tuple[int, int]]:
        """Belirli bir format için gereken boyutları getir"""
        return self.min_dimensions.get(format)
    
    def calculate_print_size(self, pixel_dimensions: Tuple[int, int], dpi: int) -> Tuple[float, float]:
        """Piksel boyutlarından fiziksel baskı boyutunu hesapla (mm cinsinden)"""
        width_mm = (pixel_dimensions[0] / dpi) * 25.4
        height_mm = (pixel_dimensions[1] / dpi) * 25.4
        return (width_mm, height_mm)
    
    def suggest_resolution(self, format: str, target_dpi: int = 300) -> Dict:
        """Önerilen çözünürlük bilgilerini getir"""
        if format not in self.min_dimensions:
            return {'error': 'Geçersiz format'}
            
        min_width, min_height = self.min_dimensions[format]
        return {
            'suggested_pixels': (min_width, min_height),
            'suggested_dpi': target_dpi,
            'print_size_mm': self.calculate_print_size((min_width, min_height), target_dpi)
        }