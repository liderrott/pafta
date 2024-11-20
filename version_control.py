# version_control.py
from datetime import datetime
import hashlib
from typing import Dict, List, Optional
import json
import os

class VersionControl:
    def __init__(self):
        self.versions: List[Dict] = []
        self.current_version = -1
        self.versions_path = "versions/"
        os.makedirs(self.versions_path, exist_ok=True)
        self._load_versions()
        
    def create_version(self, data: Dict, message: str) -> Dict:
        """Yeni versiyon oluştur"""
        version = {
            'id': len(self.versions),
            'data': data,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'hash': self._generate_hash(data)
        }
        
        self.versions.append(version)
        self.current_version = len(self.versions) - 1
        self._save_versions()
        return version
    
    def _generate_hash(self, data: Dict) -> str:
        """Versiyon için hash oluştur"""
        return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
    
    def rollback(self, version_id: int) -> Optional[Dict]:
        """Belirli bir versiyona geri dön"""
        if 0 <= version_id < len(self.versions):
            self.current_version = version_id
            return self.versions[version_id]
        return None
    
    def get_current_version(self) -> Optional[Dict]:
        """Aktif versiyonu getir"""
        if self.current_version >= 0:
            return self.versions[self.current_version]
        return None
    
    def get_version_history(self) -> List[Dict]:
        """Versiyon geçmişini getir"""
        return [{
            'id': v['id'],
            'message': v['message'],
            'timestamp': v['timestamp'],
            'hash': v['hash']
        } for v in self.versions]
    
    def _save_versions(self) -> None:
        """Versiyonları dosyaya kaydet"""
        try:
            path = os.path.join(self.versions_path, "versions.json")
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Versiyon kaydetme hatası: {str(e)}")
    
    def _load_versions(self) -> None:
        """Versiyonları dosyadan yükle"""
        try:
            path = os.path.join(self.versions_path, "versions.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self.versions = json.load(f)
                    self.current_version = len(self.versions) - 1
        except Exception as e:
            print(f"Versiyon yükleme hatası: {str(e)}")
    
    def compare_versions(self, version_id1: int, version_id2: int) -> Dict:
        """İki versiyonu karşılaştır"""
        if not (0 <= version_id1 < len(self.versions) and 0 <= version_id2 < len(self.versions)):
            return {"error": "Geçersiz versiyon ID"}
            
        v1 = self.versions[version_id1]
        v2 = self.versions[version_id2]
        
        return {
            "timestamp_diff": v2['timestamp'] > v1['timestamp'],
            "hash_diff": v1['hash'] != v2['hash'],
            "message1": v1['message'],
            "message2": v2['message']
        }