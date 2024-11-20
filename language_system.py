# language_system.py
from typing import Dict, Optional
import json
import os

class LanguageManager:
    def __init__(self):
        self.current_lang = 'TR'
        self.languages_path = "languages/"
        os.makedirs(self.languages_path, exist_ok=True)
        
        self.translations = {
            'TR': {
                # Menü
                'new_project': 'Yeni Proje',
                'save': 'Kaydet',
                'save_as': 'Farklı Kaydet',
                'export': 'Dışa Aktar',
                'import': 'İçe Akta',
                'close': 'Kapat',
                
                # Düzenleme
                'undo': 'Geri Al',
                'redo': 'İleri Al',
                'cut': 'Kes',
                'copy': 'Kopyala',
                'paste': 'Yapıştır',
                'delete': 'Sil',
                
                # Parça Tipleri
                'front_view': 'Ön Görünüş',
                'side_view': 'Yan Görünüş',
                'top_view': 'Üst Görünüş',
                'detail': 'Detay',
                'section': 'Kesit',
                
                # Hata Mesajları
                'error_save': 'Kaydetme hatası!',
                'error_load': 'Yükleme hatası!',
                'error_export': 'Dışa aktarma hatası!'
            },
            'EN': {
                # Menu
                'new_project': 'New Project',
                'save': 'Save',
                'save_as': 'Save As',
                'export': 'Export',
                'import': 'Import',
                'close': 'Close',
                
                # Editing
                'undo': 'Undo',
                'redo': 'Redo',
                'cut': 'Cut',
                'copy': 'Copy',
                'paste': 'Paste',
                'delete': 'Delete',
                
                # Part Types
                'front_view': 'Front View',
                'side_view': 'Side View',
                'top_view': 'Top View',
                'detail': 'Detail',
                'section': 'Section',
                
                # Error Messages
                'error_save': 'Save error!',
                'error_load': 'Load error!',
                'error_export': 'Export error!'
            }
        }
        
        self._load_custom_translations()
    
    def get_text(self, key: str, default: Optional[str] = None) -> str:
        """Belirtilen anahtarın çevirisini döndür"""
        return self.translations[self.current_lang].get(key, default or key)
    
    def change_language(self, lang: str) -> bool:
        """Dili değiştir"""
        if lang in self.translations:
            self.current_lang = lang
            return True
        return False
    
    def get_available_languages(self) -> list:
        """Mevcut dilleri listele"""
        return list(self.translations.keys())
    
    def add_translation(self, lang: str, translations: Dict[str, str]) -> bool:
        """Yeni dil veya çeviri ekle"""
        try:
            if lang not in self.translations:
                self.translations[lang] = {}
            self.translations[lang].update(translations)
            self._save_custom_translations()
            return True
        except:
            return False
    
    def _load_custom_translations(self):
        """Özel çevirileri yükle"""
        try:
            custom_file = os.path.join(self.languages_path, "custom_translations.json")
            if os.path.exists(custom_file):
                with open(custom_file, 'r', encoding='utf-8') as f:
                    custom_translations = json.load(f)
                    for lang, trans in custom_translations.items():
                        if lang not in self.translations:
                            self.translations[lang] = {}
                        self.translations[lang].update(trans)
        except Exception as e:
            print(f"Özel çeviri yükleme hatası: {str(e)}")
    
    def _save_custom_translations(self):
        """Özel çevirileri kaydet"""
        try:
            custom_file = os.path.join(self.languages_path, "custom_translations.json")
            with open(custom_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Özel çeviri kaydetme hatası: {str(e)}")