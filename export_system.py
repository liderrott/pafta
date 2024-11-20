# export_system.py
from abc import ABC, abstractmethod
from data_structures import Project, Part, PartType
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3  # A3 kullanıyoruz
from reportlab.lib.units import mm
from PIL import Image
import os

class Exporter(ABC):
    @abstractmethod
    def export(self, project: Project, path: str) -> bool:
        pass

class PDFExporter(Exporter):
    def export(self, project: Project, path: str) -> bool:
        try:
            c = canvas.Canvas(path, pagesize=A3)
            for page_num, page in enumerate(project.pages):
                if page_num > 0:
                    c.showPage()
                self._create_page(c, page, project)
            c.save()
            return True
        except Exception as e:
            print(f"PDF export hatası: {str(e)}")
            return False
    
    def _create_page(self, c, page, project):
        # Sayfa başlığı
        c.setFont("Helvetica-Bold", 14)
        c.drawString(20*mm, 400*mm, f"Proje: {project.name}")
        c.drawString(20*mm, 390*mm, f"Sayfa: {project.current_page + 1}/{len(project.pages)}")
        
        # Parçaları yerleştir
        for part in page.get('parts', []):
            if isinstance(part, Part):
                self._place_part(c, part)
    
    def _place_part(self, c, part: Part):
        if part.image_path and os.path.exists(part.image_path):
            x, y = part.position or (0, 0)
            width, height = part.size
            
            # Rotasyon ve ölçek uygula
            c.saveState()
            c.translate(x*mm, y*mm)
            c.rotate(part.rotation)
            c.scale(part.scale, part.scale)
            
            try:
                c.drawImage(
                    part.image_path,
                    0, 0,
                    width=width*mm,
                    height=height*mm,
                    preserveAspectRatio=True
                )
            except Exception as e:
                print(f"Görsel yerleştirme hatası: {str(e)}")
            
            c.restoreState()

class PNGExporter(Exporter):
    def export(self, project: Project, path: str) -> bool:
        try:
            # Aktif sayfayı PNG olarak kaydet
            page = project.pages[project.current_page]
            
            # Boş bir A3 görsel oluştur
            img = Image.new('RGB', (3508, 4961), 'white')  # A3 300dpi
            
            # Parçaları yerleştir
            for part in page.get('parts', []):
                if isinstance(part, Part) and part.image_path:
                    self._place_part(img, part)
            
            img.save(path, 'PNG', dpi=(300, 300))
            return True
            
        except Exception as e:
            print(f"PNG export hatası: {str(e)}")
            return False
    
    def _place_part(self, img: Image.Image, part: Part):
        if os.path.exists(part.image_path):
            try:
                part_img = Image.open(part.image_path)
                
                # Rotasyon ve ölçek uygula
                if part.rotation:
                    part_img = part_img.rotate(part.rotation, expand=True)
                if part.scale != 1.0:
                    new_size = tuple(int(dim * part.scale) for dim in part_img.size)
                    part_img = part_img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Parçayı yerleştir
                x, y = part.position or (0, 0)
                img.paste(part_img, (int(x), int(y)))
                
            except Exception as e:
                print(f"Parça yerleştirme hatası: {str(e)}")

class ExportManager:
    def __init__(self):
        self.exporters = {
            'pdf': PDFExporter(),
            'png': PNGExporter()
        }
    
    def export(self, project: Project, format_type: str, path: str) -> bool:
        if format_type in self.exporters:
            return self.exporters[format_type].export(project, path)
        return False