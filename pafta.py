import sys
import json
import os
from PIL import Image
import io
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from data_structures import *
from export_system import ExportManager
from layout_system import LayoutManager
from optimization_engine import LayoutOptimizer
from project_manager import ProjectManager
from template_manager import TemplateManager
from template_system import Template
from language_system import LanguageManager
from part_detail_manager import PartDetailManager
from security_manager import SecurityManager
from version_control import VersionControl
from resolution_checker import ResolutionChecker
from ai_exporter import AIExporter


class PreviewArea(QLabel):
    image_dropped = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Görüntü yüklemek için sürükle bırak")
        self.current_image = None
        self.zoom_factor = 1.0
        self.template_path = "templates/"
        self.current_page = 0
        self.pages = [{}]
        self.undo_stack = UndoStack()
    
        # Önce layout manager'ı oluştur
        self.layout_manager = LayoutManager()
    
        # Sonra diğer yöneticileri başlat
        self.part_group_manager = PartGroupManager()
        self.collision_manager = CollisionManager()
        self.layout_optimizer = LayoutOptimizer(self.layout_manager)
        self.project_manager = ProjectManager()
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self.image_dropped.emit(file_path)
                break
class ExportManager:
    def __init__(self):
        self.exporters = {
            'pdf': PDFExporter(),
            'png': PNGExporter()
        }
    
    def export(self, data, format_type, path):
        if format_type in self.exporters:
            return self.exporters[format_type].export(data, path)
        return False

class PDFExporter:
    def export(self, data, path):
        try:
            # PDF oluştur
            c = canvas.Canvas(path, pagesize=A4)
            
            # Her sayfa için
            for page_num, page_data in enumerate(data['pages']):
                if page_num > 0:
                    c.showPage()  # Yeni sayfa
                
                # Sayfa başlığı
                c.setFont("Helvetica-Bold", 14)
                c.drawString(20*mm, 280*mm, f"Ürün: {page_data.get('urun_adi', '')}")
                c.drawString(20*mm, 273*mm, f"Kod: {page_data.get('urun_kodu', '')}")
                c.drawString(20*mm, 266*mm, f"Seri: {page_data.get('seri', '')}")
                
                # Çizgi çek
                c.line(20*mm, 263*mm, 190*mm, 263*mm)
                
                # Görüntü varsa ekle
                if 'image' in page_data:
                    img_path = page_data['image']
                    c.drawImage(img_path, 20*mm, 50*mm, width=170*mm, height=170*mm, preserveAspectRatio=True)
                
                # Sayfa numarası
                c.setFont("Helvetica", 10)
                c.drawString(100*mm, 10*mm, f"Sayfa {page_num + 1} / {len(data['pages'])}")
            
            c.save()
            return True
            
        except Exception as e:
            print(f"PDF export hatası: {str(e)}")
            return False

class PNGExporter:
    def export(self, data, path):
        try:
            if 'current_image' in data and data['current_image']:
                data['current_image'].save(path, 'PNG')
                return True
            return False
            
        except Exception as e:
            print(f"PNG export hatası: {str(e)}")
            return False

class PartGroup:
    def __init__(self, name, parts=None):
        self.name = name
        self.parts = parts or []
        self.constraints = []  # Grup kısıtlamaları
        self.relationships = []  # Parçalar arası ilişkiler

class PartGroupManager:
    def __init__(self):
        self.groups = {}
        self.default_groups = {
            "Görünüşler": ["Ön Görünüş", "Yan Görünüş", "Üst Görünüş"],
            "Detaylar": ["Detay", "Kesit", "Ölçüler"],
            "Montaj": ["Montaj", "Parça Listesi", "Perspektif"]
        }

    def create_group(self, name, parts):
        self.groups[name] = PartGroup(name, parts)
        
    def get_group_constraints(self, group_name):
        if group_name in self.groups:
            return self.groups[group_name].constraints
        return []

    def validate_group_placement(self, group_name, layout):
        # Grup yerleşim kurallarını kontrol et
        pass

class CollisionManager:
    def __init__(self):
        self.collision_matrix = {}  # Parça çakışma matrisi
        self.priority_rules = {}    # Öncelik kuralları
        
    def check_collision(self, part1, part2, position1, position2):
        # İki parça arasında çakışma kontrolü
        rect1 = self.get_part_bounds(part1, position1)
        rect2 = self.get_part_bounds(part2, position2)
        return self.rectangles_overlap(rect1, rect2)
    
    def get_part_bounds(self, part, position):
        # Parçanın sınırlarını hesapla
        size = self.layout_manager.get_part_size(part)
        return {
            'x': position[1],
            'y': position[0],
            'width': size[0],
            'height': size[1]
        }
    
    def rectangles_overlap(self, rect1, rect2):
        return not (rect1['x'] + rect1['width'] <= rect2['x'] or
                   rect1['x'] >= rect2['x'] + rect2['width'] or
                   rect1['y'] + rect1['height'] <= rect2['y'] or
                   rect1['y'] >= rect2['y'] + rect2['height'])
    
    def resolve_collision(self, part1, part2):
        # Çakışma durumunda öncelik kurallarına göre çözüm
        if self.priority_rules.get(part1, 0) > self.priority_rules.get(part2, 0):
            return part1
        return part2

class LayoutOptimizer:
    def __init__(self, layout_manager):
        self.layout_manager = layout_manager
        self.score_weights = {
            'spacing': 0.3,
            'alignment': 0.3,
            'grouping': 0.2,
            'balance': 0.2
        }
        
    def optimize_layout(self, parts):
        best_layout = None
        best_score = -1
        
        # Farklı yerleşim kombinasyonlarını dene
        for layout in self.generate_layouts(parts):
            score = self.evaluate_layout(layout)
            if score > best_score:
                best_score = score
                best_layout = layout
                
        return best_layout

    def generate_layouts(self, parts):
        # Tüm olası yerleşimleri üret
        layouts = []
        positions = [(i, j) for i in range(3) for j in range(3)]
        
        for perm in itertools.permutations(parts):
            layout = {}
            valid = True
            used = set()
            
            for part in perm:
                placed = False
                for pos in positions:
                    if pos not in used and self.layout_manager.can_place_part(part, pos):
                        layout[part] = pos
                        used.add(pos)
                        placed = True
                        break
                if not placed:
                    valid = False
                    break
                    
            if valid:
                layouts.append(layout)
                
        return layouts
    
    def evaluate_layout(self, layout):
        spacing_score = self.evaluate_spacing(layout)
        alignment_score = self.evaluate_alignment(layout)
        grouping_score = self.evaluate_grouping(layout)
        balance_score = self.evaluate_balance(layout)
        
        return (spacing_score * self.score_weights['spacing'] +
                alignment_score * self.score_weights['alignment'] +
                grouping_score * self.score_weights['grouping'] +
                balance_score * self.score_weights['balance'])
    
    def evaluate_spacing(self, layout):
        # Parçalar arası boşlukları değerlendir
        pass
        
    def evaluate_alignment(self, layout):
        # Hizalamaları değerlendir
        pass
        
    def evaluate_grouping(self, layout):
        # Grup yerleşimlerini değerlendir
        pass
        
    def evaluate_balance(self, layout):
        # Görsel dengeyi değerlendir
        pass

class ProjectManager:
    def __init__(self):
        self.current_project = None
        self.autosave_interval = 300  # 5 dakika
        
    def save_project(self, filename):
        project_data = {
            'metadata': {
                'version': '1.0',
                'date': datetime.now().isoformat(),
                'author': getpass.getuser()
            },
            'pages': self.pages,
            'layout': self.layout_manager.serialize(),
            'groups': self.part_group_manager.serialize(),
            'settings': self.get_project_settings()
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            self.log_error(f"Proje kaydedilemedi: {str(e)}")
            return False

    def validate_project_version(self, version):
        try:
            major, minor = map(int, version.split('.'))
            return major == 1 and minor >= 0
        except:
            return False
    
    def load_project(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                
            # Versiyon kontrolü
            if self.validate_project_version(project_data['metadata']['version']):
                self.pages = project_data['pages']
                self.layout_manager.deserialize(project_data['layout'])
                self.part_group_manager.deserialize(project_data['groups'])
                self.apply_project_settings(project_data['settings'])
                return True
        except Exception as e:
            self.log_error(f"Proje yüklenemedi: {str(e)}")
            return False
    
    def autosave(self):
        if self.current_project:
            autosave_file = f"autosave/{self.current_project}_autosave.json"
            self.save_project(autosave_file)
    
    def recover_autosave(self):
        # En son otomatik kaydedilen dosyayı bul ve yükle
        autosave_files = glob.glob("autosave/*_autosave.json")
        if autosave_files:
            latest_autosave = max(autosave_files, key=os.path.getmtime)
            return self.load_project(latest_autosave)
        return False

class LayoutManager:
    def __init__(self):
        self.grid_size = (3, 3)  # 3x3 grid
        self.cells = [[None for _ in range(3)] for _ in range(3)]
        self.part_rotations = {}  # Parça rotasyonlarını sakla
        self.part_scales = {}     # Parça ölçeklerini sakla
        self.part_sizes = {
            "Ön Görünüş": {
                "default": (2, 2),
                "min": (1, 1),
                "max": (3, 3)
            },
            "Yan Görünüş": {
                "default": (1, 2),
                "min": (1, 1),
                "max": (2, 2)
            },
            "Üst Görünüş": {
                "default": (2, 1),
                "min": (1, 1),
                "max": (2, 2)
            },
            "Perspektif": {
                "default": (1, 1),
                "min": (1, 1),
                "max": (2, 2)
            },
            "Detay": {
                "default": (1, 1),
                "min": (1, 1),
                "max": (1, 1)
            },
            "Ölçüler": {
                "default": (1, 1),
                "min": (1, 1),
                "max": (2, 1)
            },
            "Kesit": {
                "default": (1, 1),
                "min": (1, 1),
                "max": (2, 2)
            },
            "Montaj": {
                "default": (2, 2),
                "min": (1, 1),
                "max": (3, 3)
            },
            "Parça Listesi": {
                "default": (1, 2),
                "min": (1, 1),
                "max": (1, 3)
            }
        }
    
    def get_part_size(self, part_name):
        if part_name not in self.part_sizes:
            return (1, 1)
            
        size = self.part_sizes[part_name]["default"]
        rotation = self.part_rotations.get(part_name, 0)
        scale = self.part_scales.get(part_name, 1.0)
        
        # Rotasyona göre boyutu ayarla
        if rotation in [90, 270]:
            size = (size[1], size[0])
            
        # Ölçeğe göre boyutu ayarla
        size = (
            min(max(int(size[0] * scale), self.part_sizes[part_name]["min"][0]), 
                self.part_sizes[part_name]["max"][0]),
            min(max(int(size[1] * scale), self.part_sizes[part_name]["min"][1]), 
                self.part_sizes[part_name]["max"][1])
        )
        
        return size
    
    def rotate_part(self, part_name):
        if part_name in self.part_rotations:
            self.part_rotations[part_name] = (self.part_rotations[part_name] + 90) % 360
        else:
            self.part_rotations[part_name] = 90
            
        # Parçayı yeniden yerleştir
        self.remove_part(part_name)
        return self.auto_layout([part_name])
    
    def scale_part(self, part_name, scale_factor):
        current_scale = self.part_scales.get(part_name, 1.0)
        new_scale = current_scale * scale_factor
        
        # Minimum ve maximum ölçek kontrolü
        new_scale = max(0.5, min(2.0, new_scale))
        
        self.part_scales[part_name] = new_scale
        
        # Parçayı yeniden yerleştir
        self.remove_part(part_name)
        return self.auto_layout([part_name])
    
    def can_place_part(self, part_name, start_pos):
        if part_name not in self.part_sizes:
            return False
            
        width, height = self.part_sizes[part_name]
        row, col = start_pos
        
        # Grid sınırlarını kontrol et
        if row + height > self.grid_size[0] or col + width > self.grid_size[1]:
            return False
            
        # Hücrelerin boş olup olmadığını kontrol et
        for i in range(height):
            for j in range(width):
                if self.cells[row + i][col + j] is not None:
                    return False
                    
        return True
    
    def place_part(self, part_name, start_pos):
        if not self.can_place_part(part_name, start_pos):
            return False
            
        width, height = self.part_sizes[part_name]
        row, col = start_pos
        
        # Parçayı yerleştir
        for i in range(height):
            for j in range(width):
                self.cells[row + i][col + j] = part_name
                
        return True
    
    def remove_part(self, part_name):
        # Parçayı gridden kaldır
        for i in range(self.grid_size[0]):
            for j in range(self.grid_size[1]):
                if self.cells[i][j] == part_name:
                    self.cells[i][j] = None
    
    def auto_layout(self, selected_parts):
        # Gridi temizle
        self.cells = [[None for _ in range(3)] for _ in range(3)]
        
        # Parçaları boyutlarına göre sırala (büyükten küçüğe)
        sorted_parts = sorted(
            selected_parts,
            key=lambda x: self.part_sizes[x][0] * self.part_sizes[x][1],
            reverse=True
        )
        
        for part in sorted_parts:
            placed = False
            # Tüm pozisyonları dene
            for i in range(self.grid_size[0]):
                for j in range(self.grid_size[1]):
                    if self.place_part(part, (i, j)):
                        placed = True
                        break
                if placed:
                    break
                    
        return self.cells

class Template:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.settings = {
            'page_layout': [],
            'default_parts': [],
            'custom_fields': {},
            'export_settings': {}
        }
    
    def save(self, path):
        data = {
            'name': self.name,
            'description': self.description,
            'settings': self.settings
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    @classmethod
    def load(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            template = cls(data['name'], data['description'])
            template.settings = data['settings']
            return template

class UndoStack:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        
    def push(self, state):
        self.undo_stack.append(state)
        self.redo_stack.clear()
        
    def undo(self):
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            return self.undo_stack[-1] if self.undo_stack else None
        return None
        
    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            return state
        return None

class PaftaOlusturucu(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Yöneticileri başlat

        self.export_manager = ExportManager()
        self.layout_manager = LayoutManager()
        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()
        self.layout_optimizer = LayoutOptimizer(self.layout_manager)
        self.language_manager = LanguageManager()
        self.part_detail_manager = PartDetailManager()
        self.security_manager = SecurityManager()
        self.version_control = VersionControl()
        self.resolution_checker = ResolutionChecker()
        self.ai_exporter = AIExporter()

        # Temel özellikleri başlat
        self.current_image = None
        self.zoom_factor = 1.0
        self.template_path = "templates/"
        self.current_page = 0
        self.pages = [{}]
        
        # Manager sınıflarını başlat
        self.layout_manager = LayoutManager()  # Önce bunu oluştur
        self.part_group_manager = PartGroupManager()
        self.collision_manager = CollisionManager()
        self.layout_optimizer = LayoutOptimizer(self.layout_manager)
        self.project_manager = ProjectManager()
        self.undo_stack = UndoStack()
        
        # Otomatik kaydetme için timer
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(300000)  # 5 dakikada bir
        
        # UI'ı başlat
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Pafta Oluşturucu")
        self.setMinimumSize(1400, 800)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Sol ve sağ panelleri oluştur
        self.create_left_panel(main_layout)
        self.create_right_panel(main_layout)
        
        # Menü bar
        self.create_menu_bar()

    def undo(self):
        state = self.undo_stack.undo()
        if state:
            self.load_state(state)
            
    def redo(self):
        state = self.undo_stack.redo()
        if state:
            self.load_state(state)

    def create_new_project(self):
        name, ok = QInputDialog.getText(self, 'Yeni Proje', 'Proje Adı:')
        if ok and name:
            self.project_manager.create_project(name)
            self.update_ui()

    def save_project(self):
        if not self.project_manager.current_project:
            return
            
        path, _ = QFileDialog.getSaveFileName(
            self,
            'Projeyi Kaydet',
            '',
            'Pafta Projeleri (*.pafta)'
        )
        
        if path:
            if self.project_manager.save_project(path):
                QMessageBox.information(self, 'Başarılı', 'Proje kaydedildi!')
            else:
                QMessageBox.warning(self, 'Hata', 'Proje kaydedilemedi!')

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Proje Aç',
            '',
            'Pafta Projeleri (*.pafta)'
        )
        
        if path:
            if self.project_manager.load_project(path):
                self.update_ui()
            else:
                QMessageBox.warning(self, 'Hata', 'Proje yüklenemedi!')
                
    def export_project(self):
        if not self.project_manager.current_project:
            return
            
        format, ok = QInputDialog.getItem(
            self,
            'Export Format',
            'Format seçin:',
            ['pdf', 'png'],
            0,
            False
        )
        
        if ok and format:
            path, _ = QFileDialog.getSaveFileName(
                self,
                'Export',
                '',
                f'{format.upper()} Files (*.{format})'
            )
            
            if path:
                if self.export_manager.export(
                    self.project_manager.current_project,
                    format,
                    path
                ):
                    QMessageBox.information(self, 'Başarılı', 'Export tamamlandı!')
                else:
                    QMessageBox.warning(self, 'Hata', 'Export başarısız!')

    def auto_optimize_layout(self):
        selected_parts = self.get_selected_parts()
        optimized_layout = self.layout_optimizer.optimize_layout(selected_parts)
        if optimized_layout:
            self.apply_layout(optimized_layout)
            self.update_preview()

    def create_part_context_menu(self, part_name, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
            }
            QMenu::item:selected {
                background-color: #2196F3;
            }
        """)
        
        # Rotasyon
        rotate_action = QAction("Döndür (90°)", self)
        rotate_action.triggered.connect(lambda: self.rotate_selected_part(part_name))
        menu.addAction(rotate_action)
        
        # Ölçeklendirme menüsü
        scale_menu = menu.addMenu("Ölçek")
        
        scale_actions = {
            "0.5x": 0.5,
            "0.75x": 0.75,
            "1x": 1.0,
            "1.5x": 1.5,
            "2x": 2.0
        }
        
        for text, factor in scale_actions.items():
            action = QAction(text, self)
            action.triggered.connect(lambda checked, f=factor: self.scale_selected_part(part_name, f))
            scale_menu.addAction(action)
        
        # Kaldır
        remove_action = QAction("Kaldır", self)
        remove_action.triggered.connect(lambda: self.remove_selected_part(part_name))
        menu.addAction(remove_action)
        
        return menu
    
    def cell_clicked(self, row, col):
        current_part = self.layout_manager.cells[row][col]
        
        if current_part:
            # Parça varsa context menüyü göster
            menu = self.create_part_context_menu(current_part, self.grid_buttons[row][col])
            menu.exec_(QCursor.pos())
        else:
            # Parça yoksa yeni parça yerleştirme dialogunu göster
            self.show_part_placement_dialog(row, col)
    
    def show_part_placement_dialog(self, row, col):
        # Seçili parçaları al
        selected_parts = []
        for checkbox, part_name in zip(self.part_checkboxes, [
            "Ön Görünüş", "Yan Görünüş", "Üst Görünüş", 
            "Perspektif", "Detay", "Ölçüler", "Kesit",
            "Montaj", "Parça Listesi"
        ]):
            if checkbox.isChecked():
                selected_parts.append(part_name)
        
        if not selected_parts:
            QMessageBox.warning(self, "Uyarı", "Önce bir parça seçin!")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Parça Yerleştir")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # Parça listesi
        part_list = QListWidget()
        part_list.addItems(selected_parts)
        part_list.setStyleSheet("""
            QListWidget {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
            }
        """)
        
        # Rotasyon seçimi
        rotation_group = QGroupBox("Rotasyon")
        rotation_group.setStyleSheet(self.get_group_style())
        rotation_layout = QHBoxLayout()
        
        rotation_0 = QRadioButton("0°")
        rotation_90 = QRadioButton("90°")
        rotation_180 = QRadioButton("180°")
        rotation_270 = QRadioButton("270°")
        
        rotation_0.setChecked(True)
        
        for radio in [rotation_0, rotation_90, rotation_180, rotation_270]:
            radio.setStyleSheet("color: white;")
            rotation_layout.addWidget(radio)
        
        rotation_group.setLayout(rotation_layout)
        
        # Ölçek seçimi
        scale_group = QGroupBox("Ölçek")
        scale_group.setStyleSheet(self.get_group_style())
        scale_layout = QHBoxLayout()
        
        scale_slider = QSlider(Qt.Horizontal)
        scale_slider.setMinimum(50)
        scale_slider.setMaximum(200)
        scale_slider.setValue(100)
        scale_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #444444;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                width: 16px;
                margin: -4px 0;
                border-radius: 8px;
            }
        """)
        
        scale_label = QLabel("1.0x")
        scale_label.setStyleSheet("color: white;")
        
        scale_slider.valueChanged.connect(
            lambda v: scale_label.setText(f"{v/100:.1f}x")
        )
        
        scale_layout.addWidget(scale_slider)
        scale_layout.addWidget(scale_label)
        
        scale_group.setLayout(scale_layout)
        
        # Yerleştir butonu
        place_btn = QPushButton("Yerleştir")
        place_btn.setStyleSheet(self.get_button_style(primary=True))
        place_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(part_list)
        layout.addWidget(rotation_group)
        layout.addWidget(scale_group)
        layout.addWidget(place_btn)
        
        if dialog.exec() == QDialog.Accepted:
            selected_part = part_list.currentItem()
            if selected_part:
                part_name = selected_part.text()
                
                # Rotasyon değerini al
                rotation = 0
                if rotation_90.isChecked(): rotation = 90
                elif rotation_180.isChecked(): rotation = 180
                elif rotation_270.isChecked(): rotation = 270
                
                # Ölçek değerini al
                scale = scale_slider.value() / 100
                
                # Parçayı yerleştir
                if self.layout_manager.place_part(part_name, (row, col)):
                    # Rotasyon ve ölçeği kaydet
                    self.layout_manager.part_rotations[part_name] = rotation
                    self.layout_manager.part_scales[part_name] = scale
                    self.update_layout_grid()
                else:
                    QMessageBox.warning(self, "Uyarı", "Bu parça buraya yerleştirilemez!")
    
    def create_layout_group(self):
        layout_group = QGroupBox("Yerleşim Düzeni")
        layout_group.setStyleSheet(self.get_group_style())
        
        layout_main = QVBoxLayout()
        
        # Yerleşim grid'i
        self.layout_grid = QGridLayout()
        self.layout_grid.setSpacing(5)
        
        # Layout manager
        self.layout_manager = LayoutManager()
        
        # Grid butonları
        self.grid_buttons = []
        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = QPushButton()
                btn.setFixedSize(60, 60)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #444444;
                        border: 1px solid #555555;
                        border-radius: 3px;
                        color: white;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #2196F3;
                    }
                """)
                btn.clicked.connect(lambda checked, row=i, col=j: self.cell_clicked(row, col))
                self.layout_grid.addWidget(btn, i, j)
                row_buttons.append(btn)
            self.grid_buttons.append(row_buttons)
        
        # Otomatik yerleşim butonu
        auto_layout_btn = QPushButton("Otomatik Yerleşim")
        auto_layout_btn.setStyleSheet(self.get_button_style(primary=True))
        auto_layout_btn.clicked.connect(self.auto_arrange_parts)
        
        # Temizle butonu
        clear_layout_btn = QPushButton("Temizle")
        clear_layout_btn.setStyleSheet(self.get_button_style())
        clear_layout_btn.clicked.connect(self.clear_layout)
        
        layout_main.addLayout(self.layout_grid)
        layout_main.addWidget(auto_layout_btn)
        layout_main.addWidget(clear_layout_btn)
        
        layout_group.setLayout(layout_main)
        return layout_group
    
    def cell_clicked(self, row, col):
        # Seçili parçayı bul
        selected_parts = []
        for checkbox, part_name in zip(self.part_checkboxes, [
            "Ön Görünüş", "Yan Görünüş", "Üst Görünüş", 
            "Perspektif", "Detay", "Ölçüler", "Kesit",
            "Montaj", "Parça Listesi"
        ]):
            if checkbox.isChecked():
                selected_parts.append(part_name)
        
        if not selected_parts:
            QMessageBox.warning(self, "Uyarı", "Önce bir parça seçin!")
            return
        
        # Parça yerleştirme dialogu
        dialog = QDialog(self)
        dialog.setWindowTitle("Parça Seç")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        part_list = QListWidget()
        part_list.addItems(selected_parts)
        part_list.setStyleSheet("""
            QListWidget {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
            }
        """)
        
        layout.addWidget(part_list)
        
        place_btn = QPushButton("Yerleştir")
        place_btn.setStyleSheet(self.get_button_style(primary=True))
        place_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(place_btn)
        
        if dialog.exec() == QDialog.Accepted:
            selected_part = part_list.currentItem()
            if selected_part:
                part_name = selected_part.text()
                if self.layout_manager.place_part(part_name, (row, col)):
                    self.update_layout_grid()
                else:
                    QMessageBox.warning(self, "Uyarı", "Bu parça buraya yerleştirilemez!")
    
    def update_layout_grid(self):
        # Grid görünümünü güncelle
        for i in range(3):
            for j in range(3):
                part = self.layout_manager.cells[i][j]
                btn = self.grid_buttons[i][j]
                if part:
                    btn.setText(part)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            border: 1px solid #1976D2;
                            border-radius: 3px;
                            color: white;
                            font-size: 10px;
                        }
                    """)
                else:
                    btn.setText("")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #444444;
                            border: 1px solid #555555;
                            border-radius: 3px;
                            color: white;
                            font-size: 10px;
                        }
                        QPushButton:hover {
                            background-color: #2196F3;
                        }
                    """)
    
    def auto_arrange_parts(self):
        # Seçili parçaları al
        selected_parts = []
        for checkbox, part_name in zip(self.part_checkboxes, [
            "Ön Görünüş", "Yan Görünüş", "Üst Görünüş", 
            "Perspektif", "Detay", "Ölçüler", "Kesit",
            "Montaj", "Parça Listesi"
        ]):
            if checkbox.isChecked():
                selected_parts.append(part_name)
        
        if not selected_parts:
            QMessageBox.warning(self, "Uyarı", "Önce parça seçin!")
            return
        
        # Otomatik yerleşim
        self.layout_manager.auto_layout(selected_parts)
        self.update_layout_grid()
    
    def clear_layout(self):
        # Gridi temizle
        self.layout_manager.cells = [[None for _ in range(3)] for _ in range(3)]
        self.update_layout_grid()
                
    def load_state(self, state):
        self.pages = state['pages']
        self.current_page = state['current_page']
        self.load_page(self.current_page)
        
    def create_left_panel(self, main_layout):
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview area
        self.preview_area = PreviewArea()
        self.preview_area.setMinimumSize(600, 800)
        self.preview_area.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        self.preview_area.image_dropped.connect(self.handle_dropped_image)
        
        # Zoom ve sayfa kontrolleri
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        
        # Sayfa kontrolleri
        page_widget = QWidget()
        page_layout = QHBoxLayout(page_widget)
        
        prev_page_btn = QPushButton("←")
        self.page_label = QLabel("Sayfa 1")
        next_page_btn = QPushButton("→")
        add_page_btn = QPushButton("+")
        
        for btn in [prev_page_btn, next_page_btn, add_page_btn]:
            btn.setStyleSheet(self.get_button_style())
            
        page_layout.addWidget(prev_page_btn)
        page_layout.addWidget(self.page_label)
        page_layout.addWidget(next_page_btn)
        page_layout.addWidget(add_page_btn)
        
        # Zoom kontrolleri
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        
        zoom_out_btn = QPushButton("-")
        self.zoom_label = QLabel("100%")
        zoom_in_btn = QPushButton("+")
        fit_btn = QPushButton("Fit")
        
        for btn in [zoom_out_btn, zoom_in_btn, fit_btn]:
            btn.setStyleSheet(self.get_button_style())
            
        zoom_layout.addWidget(zoom_out_btn)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in_btn)
        zoom_layout.addWidget(fit_btn)
        
        # Kontrolleri ana layout'a ekle
        controls_layout.addWidget(page_widget)
        controls_layout.addStretch()
        controls_layout.addWidget(zoom_widget)
        
        # Olayları bağla
        prev_page_btn.clicked.connect(self.previous_page)
        next_page_btn.clicked.connect(self.next_page)
        add_page_btn.clicked.connect(self.add_page)
        zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_in_btn.clicked.connect(self.zoom_in)
        fit_btn.clicked.connect(self.zoom_fit)
        
        left_layout.addWidget(self.preview_area)
        left_layout.addWidget(controls_widget)
        
        main_layout.addWidget(left_panel, 2)

    def manage_templates(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Template Yönetimi")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Template listesi
        template_list = QListWidget()
        template_list.setStyleSheet("""
            QListWidget {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #2196F3;
            }
        """)
        
        # Template klasöründeki şablonları yükle
        self.load_template_list(template_list)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("Yeni")
        edit_btn = QPushButton("Düzenle")
        delete_btn = QPushButton("Sil")
        
        for btn in [new_btn, edit_btn, delete_btn]:
            btn.setStyleSheet(self.get_button_style())
            btn_layout.addWidget(btn)
        
        # Olayları bağla
        new_btn.clicked.connect(lambda: self.create_new_template(template_list))
        edit_btn.clicked.connect(lambda: self.edit_template(template_list))
        delete_btn.clicked.connect(lambda: self.delete_template(template_list))
        
        layout.addWidget(template_list)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def load_template_list(self, list_widget):
        list_widget.clear()
        if os.path.exists(self.template_path):
            for file in os.listdir(self.template_path):
                if file.endswith('.json'):
                    try:
                        template = Template.load(os.path.join(self.template_path, file))
                        item = QListWidgetItem(f"{template.name} - {template.description}")
                        item.setData(Qt.UserRole, template)
                        list_widget.addItem(item)
                    except:
                        continue
    
    def create_new_template(self, list_widget):
        name, ok = QInputDialog.getText(self, "Yeni Template", "Template Adı:")
        if ok and name:
            template = Template(name)
            self.edit_template_settings(template)
            self.save_template(template)
            self.load_template_list(list_widget)
    
    def edit_template(self, list_widget):
        current = list_widget.currentItem()
        if current:
            template = current.data(Qt.UserRole)
            self.edit_template_settings(template)
            self.save_template(template)
            self.load_template_list(list_widget)
    
    def edit_template_settings(self, template):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Template Düzenle: {template.name}")
        dialog.setModal(True)
        dialog.resize(800, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Ayarlar sekmesi
        tabs = QTabWidget()
        
        # Genel ayarlar
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        name_edit = QLineEdit(template.name)
        desc_edit = QLineEdit(template.description)
        
        general_layout.addRow("İsim:", name_edit)
        general_layout.addRow("Açıklama:", desc_edit)
        
        # Yerleşim ayarları
        layout_tab = QWidget()
        layout_layout = QVBoxLayout(layout_tab)
        
        # Parça ayarları
        parts_tab = QWidget()
        parts_layout = QVBoxLayout(parts_tab)
        
        # Export ayarları
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)
        
        tabs.addTab(general_tab, "Genel")
        tabs.addTab(layout_tab, "Yerleşim")
        tabs.addTab(parts_tab, "Parçalar")
        tabs.addTab(export_tab, "Export")
        
        layout.addWidget(tabs)
        
        # Kaydet butonu
        save_btn = QPushButton("Kaydet")
        save_btn.setStyleSheet(self.get_button_style(primary=True))
        save_btn.clicked.connect(dialog.accept)
        
        layout.addWidget(save_btn)
        
        if dialog.exec():  # Burayı düzelttim
            template.name = name_edit.text()
            template.description = desc_edit.text()
            # Diğer ayarları kaydet
    
    def save_template(self, template):
        if not os.path.exists(self.template_path):
            os.makedirs(self.template_path)
        
        file_path = os.path.join(self.template_path, f"{template.name}.json")
        template.save(file_path)
    
    def delete_template(self, list_widget):
        current = list_widget.currentItem()
        if current:
            template = current.data(Qt.UserRole)
            reply = QMessageBox.question(
                self,
                "Template Sil",
                f"{template.name} template'ini silmek istediğinize emin misiniz?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                file_path = os.path.join(self.template_path, f"{template.name}.json")
                try:
                    os.remove(file_path)
                    self.load_template_list(list_widget)
                except:
                    QMessageBox.warning(self, "Hata", "Template silinemedi!")
    
    

    def export_as_pdf(self, file_name):
        try:
            # PDF oluştur
            c = canvas.Canvas(file_name, pagesize=A4)
            
            # Her sayfa için
            for page_num, page_data in enumerate(self.pages):
                if page_num > 0:
                    c.showPage()  # Yeni sayfa
                
                # Sayfa başlığı
                c.setFont("Helvetica-Bold", 14)
                c.drawString(20*mm, 280*mm, f"Ürün: {page_data.get('urun_adi', '')}")
                c.drawString(20*mm, 273*mm, f"Kod: {page_data.get('urun_kodu', '')}")
                c.drawString(20*mm, 266*mm, f"Seri: {page_data.get('seri', '')}")
                
                # Çizgi çek
                c.line(20*mm, 263*mm, 190*mm, 263*mm)
                
                # Seçili parçaları listele
                c.setFont("Helvetica", 12)
                y_pos = 250
                for i, (checkbox, part_name) in enumerate(zip(self.part_checkboxes, [
                    "Ön Görünüş", "Yan Görünüş", "Üst Görünüş", 
                    "Perspektif", "Detay", "Ölçüler", "Kesit",
                    "Montaj", "Parça Listesi"
                ])):
                    if checkbox.isChecked():
                        c.drawString(20*mm, y_pos*mm, f"• {part_name}")
                        y_pos -= 7
                
                # Görüntü varsa ekle
                if 'image' in page_data:
                    img_path = page_data['image']
                    c.drawImage(img_path, 20*mm, 50*mm, width=170*mm, height=170*mm, preserveAspectRatio=True)
                
                # Sayfa numarası
                c.setFont("Helvetica", 10)
                c.drawString(100*mm, 10*mm, f"Sayfa {page_num + 1} / {len(self.pages)}")
            
            c.save()
            return True
        
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"PDF oluşturulurken hata: {str(e)}")
            return False

    def create_right_panel(self, main_layout):
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        
        # Ürün Bilgileri Grubu
        info_group = self.create_info_group()
        
        # Parça Seçimi Grubu
        parts_group = self.create_parts_group()
        
        # Parça Yerleşim Grubu
        layout_group = self.create_layout_group()
        
        # Export Grubu
        export_group = self.create_export_group()
        
        # Grupları sağ panel layout'a ekleme
        right_layout.addWidget(info_group)
        right_layout.addWidget(parts_group)
        right_layout.addWidget(layout_group)
        right_layout.addWidget(export_group)
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel, 1)
        
    def create_info_group(self):
        info_group = QGroupBox("Ürün Bilgileri")
        info_group.setStyleSheet(self.get_group_style())
        
        info_layout = QFormLayout()
        info_layout.setSpacing(10)
        
        self.urun_kodu = QLineEdit()
        self.urun_adi = QLineEdit()
        self.seri = QLineEdit()
        
        for widget in [self.urun_kodu, self.urun_adi, self.seri]:
            widget.setStyleSheet(self.get_line_edit_style())
            widget.textChanged.connect(self.save_state)
        
        info_layout.addRow("Ürün Kodu:", self.urun_kodu)
        info_layout.addRow("Ürün Adı:", self.urun_adi)
        info_layout.addRow("Seri:", self.seri)
        
        info_group.setLayout(info_layout)
        return info_group
        
    def create_parts_group(self):
        parts_group = QGroupBox("Parça Seçimi")
        parts_group.setStyleSheet(self.get_group_style())
        
        parts_layout = QVBoxLayout()
        
        # Parça grid'i
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(5)
        
        self.part_checkboxes = []
        parts = ["Ön Görünüş", "Yan Görünüş", "Üst Görünüş", 
                "Perspektif", "Detay", "Ölçüler", "Kesit",
                "Montaj", "Parça Listesi"]
        
        row = 0
        col = 0
        for part in parts:
            checkbox = QCheckBox(part)
            checkbox.setStyleSheet(self.get_checkbox_style())
            checkbox.stateChanged.connect(self.save_state)
            grid_layout.addWidget(checkbox, row, col)
            self.part_checkboxes.append(checkbox)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        parts_layout.addWidget(grid_widget)
        parts_group.setLayout(parts_layout)
        return parts_group

    def create_layout_group(self):
        layout_group = QGroupBox("Yerleşim Düzeni")
        layout_group.setStyleSheet(self.get_group_style())
        
        layout_main = QVBoxLayout()
        
        # Yerleşim grid'i
        self.layout_grid = QGridLayout()
        self.layout_grid.setSpacing(5)
        
        # 3x3 grid oluştur
        for i in range(3):
            for j in range(3):
                cell = QPushButton()
                cell.setFixedSize(50, 50)
                cell.setStyleSheet("""
                    QPushButton {
                        background-color: #444444;
                        border: 1px solid #555555;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #2196F3;
                    }
                """)
                self.layout_grid.addWidget(cell, i, j)
        
        layout_main.addLayout(self.layout_grid)
        layout_group.setLayout(layout_main)
        return layout_group
        
    def create_export_group(self):
        export_group = QGroupBox("Export")
        export_group.setStyleSheet(self.get_group_style())
        
        export_layout = QVBoxLayout()
        
        # Export seçenekleri
        options_layout = QHBoxLayout()
        
        self.pdf_radio = QRadioButton("PDF")
        self.png_radio = QRadioButton("PNG")
        self.pdf_radio.setChecked(True)
        
        for radio in [self.pdf_radio, self.png_radio]:
            radio.setStyleSheet("color: white;")
            options_layout.addWidget(radio)
        
        # Önizleme butonu
        preview_btn = QPushButton("Önizleme")
        preview_btn.setStyleSheet(self.get_button_style())
        preview_btn.clicked.connect(self.show_export_preview)
        
        # Export butonu
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet(self.get_button_style(primary=True))
        export_btn.clicked.connect(self.export_pafta)
        
        export_layout.addLayout(options_layout)
        export_layout.addWidget(preview_btn)
        export_layout.addWidget(export_btn)
        
        export_group.setLayout(export_layout)
        return export_group

    def get_group_style(self):
        return """
            QGroupBox {
                background-color: #333333;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 7px;
                padding: 0 5px 0 5px;
            }
        """
    
    def get_line_edit_style(self):
        return """
            QLineEdit {
                background-color: #444444;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """
    
    def get_checkbox_style(self):
        return """
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border-color: #2196F3;
            }
        """
    
    def get_button_style(self, primary=False):
        color = "#2196F3" if primary else "#333333"
        hover_color = "#1976D2" if primary else "#444444"
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """

    def handle_dropped_image(self, image_path):
        try:
            image = Image.open(image_path)
            # A4 boyutuna ölçekle
            a4_size = (2480, 3508)  # 300 DPI'da A4
            image.thumbnail(a4_size, Image.Resampling.LANCZOS)
            
            # QPixmap'e dönüştür
            buffer = io.BytesIO()
            image.save(buffer, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            
            self.current_image = pixmap
            self.pages[self.current_page]['image'] = image_path
            self.update_preview()
            self.save_state()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Görüntü yüklenemedi: {str(e)}")

    def update_preview(self):
        if self.current_image:
            scaled_pixmap = self.current_image.scaled(
                self.preview_area.size() * self.zoom_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_area.setPixmap(scaled_pixmap)

    def zoom_in(self):
        if self.zoom_factor < 2.0:
            self.zoom_factor += 0.25
            self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
            self.update_preview()

    def zoom_out(self):
        if self.zoom_factor > 0.25:
            self.zoom_factor -= 0.25
            self.zoom_label.setText(f"{int(self.zoom_factor * 100)}%")
            self.update_preview()

    def zoom_fit(self):
        self.zoom_factor = 1.0
        self.zoom_label.setText("100%")
        self.update_preview()

    def previous_page(self):
        if self.current_page > 0:
            self.save_current_page()
            self.current_page -= 1
            self.load_page(self.current_page)
            self.page_label.setText(f"Sayfa {self.current_page + 1}")

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.save_current_page()
            self.current_page += 1
            self.load_page(self.current_page)
            self.page_label.setText(f"Sayfa {self.current_page + 1}")

    def add_page(self):
        self.save_current_page()
        self.pages.append({})
        self.current_page = len(self.pages) - 1
        self.load_page(self.current_page)
        self.page_label.setText(f"Sayfa {self.current_page + 1}")

    def save_current_page(self):
        self.pages[self.current_page] = {
            'urun_kodu': self.urun_kodu.text(),
            'urun_adi': self.urun_adi.text(),
            'seri': self.seri.text(),
            'parcalar': [cb.isChecked() for cb in self.part_checkboxes]
        }

    def load_page(self, page_index):
        page_data = self.pages[page_index]
        self.urun_kodu.setText(page_data.get('urun_kodu', ''))
        self.urun_adi.setText(page_data.get('urun_adi', ''))
        self.seri.setText(page_data.get('seri', ''))
        
        for checkbox, is_checked in zip(self.part_checkboxes, page_data.get('parcalar', [])):
            checkbox.setChecked(is_checked)
            
        if 'image' in page_data:
            self.handle_dropped_image(page_data['image'])
        else:
            self.current_image = None
            self.preview_area.clear()
            self.preview_area.setText("Görüntü yüklemek için sürükle bırak")

    def save_state(self):
        state = {
            'pages': self.pages,
            'current_page': self.current_page
        }
        self.undo_stack.push(state)

    def show_export_preview(self):
        preview = QDialog(self)
        preview.setWindowTitle("Export Önizleme")
        preview.setModal(True)
        preview.resize(600, 800)
        
        layout = QVBoxLayout(preview)
        
        preview_label = QLabel()
        preview_label.setAlignment(Qt.AlignCenter)
        
        if self.current_image:
            preview_label.setPixmap(self.current_image.scaled(
                preview.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        
        layout.addWidget(preview_label)
        preview.exec()

    def export_pafta(self):
        file_format = "pdf" if self.pdf_radio.isChecked() else "png"
        
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Pafta Kaydet",
            "",
            f"{file_format.upper()} Files (*.{file_format})"
        )
        
        if file_name:
            # Export verilerini hazırla
            export_data = {
                'pages': self.pages,
                'current_page': self.current_page,
                'current_image': self.current_image
            }
            
            try:
                if self.export_manager.export(export_data, file_format, file_name):
                    QMessageBox.information(
                        self,
                        "Başarılı",
                        f"Pafta {file_format.upper()} formatında kaydedildi!"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Hata",
                        "Export işlemi başarısız!"
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Hata",
                    f"Export işlemi başarısız: {str(e)}"
                )

    def export_as_pdf(self, file_name):
        # PDF export işlemleri
        pass

    def export_as_png(self, file_name):
        if self.current_image:
            self.current_image.save(file_name, "PNG")

    def autosave(self):
        try:
            if not os.path.exists('autosave'):
                os.makedirs('autosave')
                
            self.save_current_page()
            
            data = {
                'pages': self.pages,
                'current_page': self.current_page
            }
            
            with open('autosave/last_session.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            print(f"Otomatik kaydetme hatası: {str(e)}")

    def create_menu_bar(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #333333;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #444444;
            }
            QMenu {
                background-color: #333333;
                color: white;
                border: 1px solid #444444;
            }
            QMenu::item:selected {
                background-color: #444444;
            }
        """)
        
        # Dosya menüsü
        file_menu = menubar.addMenu("Dosya")
        
        new_action = QAction("Yeni", self)
        open_action = QAction("Aç", self)
        save_action = QAction("Kaydet", self)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        
        # Düzen menüsü
        edit_menu = menubar.addMenu("Düzen")
        
        undo_action = QAction("Geri Al", self)
        redo_action = QAction("İleri Al", self)
        
        undo_action.triggered.connect(self.undo)
        redo_action.triggered.connect(self.redo)
        
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Stil teması
    app.setStyle("Fusion")
    
    window = PaftaOlusturucu()
    window.show()
    sys.exit(app.exec())