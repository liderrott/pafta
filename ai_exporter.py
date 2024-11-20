# ai_exporter.py
import os
from typing import Dict, List, Optional, Union
from data_structures import Project, Part

class AIExporter:
    def __init__(self):
        self.supported_versions = {
            'AI CS6': 'v16.0',
            'AI CC 2020': 'v24.0',
            'AI CC 2023': 'v27.0'
        }
        self.export_path = "exports/ai/"
        os.makedirs(self.export_path, exist_ok=True)
        
    def export_to_ai(self, data: Union[Project, Part], path: str, version: str = 'AI CC 2020') -> bool:
        """Veriyi AI formatında dışa aktar"""
        if version not in self.supported_versions:
            raise ValueError(f"Desteklenmeyen AI versiyonu: {version}")
            
        try:
            # AI dosya formatı oluşturma
            ai_data = self._convert_to_ai_format(data, version)
            
            # Dosya uzantısını kontrol et
            if not path.lower().endswith('.ai'):
                path += '.ai'
                
            # Dosyayı kaydet
            with open(path, 'wb') as f:
                f.write(ai_data)
                
            return True
        except Exception as e:
            print(f"AI export hatası: {str(e)}")
            return False
    
    def _convert_to_ai_format(self, data: Union[Project, Part], version: str) -> bytes:
        """AI dosya formatına dönüştür"""
        version_code = self.supported_versions[version]
        
        # AI dosya header'ı
        header = self._create_ai_header(version_code)
        
        # Veri dönüşümü
        if isinstance(data, Project):
            content = self._convert_project(data)
        else:
            content = self._convert_part(data)
            
        # Footer
        footer = self._create_ai_footer()
        
        return header + content + footer
    
    def _create_ai_header(self, version: str) -> bytes:
        """AI dosya header'ını oluştur"""
        # AI dosya formatı için gerekli header
        header = f"%!PS-Adobe-3.0\n"
        header += f"%%Creator: Adobe Illustrator {version}\n"
        header += f"%%BoundingBox: 0 0 595.276 841.89\n"  # A4 boyutu
        return header.encode()
    
    def _convert_project(self, project: Project) -> bytes:
        """Projeyi AI formatına dönüştür"""
        # Proje dönüşüm mantığı
        pass
    
    def _convert_part(self, part: Part) -> bytes:
        """Parçayı AI formatına dönüştür"""
        # Parça dönüşüm mantığı
        pass
    
    def _create_ai_footer(self) -> bytes:
        """AI dosya footer'ını oluştur"""
        return b"%%EOF\n"
    
    def get_supported_versions(self) -> List[str]:
        """Desteklenen AI versiyonlarını listele"""
        return list(self.supported_versions.keys())
    
    def validate_version(self, version: str) -> bool:
        """Versiyon geçerliliğini kontrol et"""
        return version in self.supported_versions