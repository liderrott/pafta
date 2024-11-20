# security_manager.py
import hashlib
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class SecurityManager:
    def __init__(self):
        self.secret_key = "your-secret-key"  # Gerçek uygulamada environment variable'dan alınmalı
        self.users = {}
        self.active_tokens = set()  # Aktif tokenları takip etmek için
        
        self.permissions = {
            'admin': ['read', 'write', 'export', 'delete', 'manage_users'],
            'editor': ['read', 'write', 'export'],
            'viewer': ['read']
        }
    
    def create_token(self, username: str, role: str) -> str:
        """Kullanıcı için JWT token oluştur"""
        payload = {
            'username': username,
            'role': role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.active_tokens.add(token)
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Token'ı doğrula"""
        try:
            if token not in self.active_tokens:
                return None
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            self.active_tokens.discard(token)
            return None
        except:
            return None
    
    def check_permission(self, token: str, action: str) -> bool:
        """Kullanıcının yetkisini kontrol et"""
        payload = self.verify_token(token)
        if not payload:
            return False
        
        role = payload.get('role')
        return action in self.permissions.get(role, [])
    
    def invalidate_token(self, token: str) -> bool:
        """Token'ı geçersiz kıl (logout için)"""
        if token in self.active_tokens:
            self.active_tokens.discard(token)
            return True
        return False
    
    def get_user_permissions(self, role: str) -> List[str]:
        """Rol için izinleri getir"""
        return self.permissions.get(role, [])
    
    def is_token_expired(self, token: str) -> bool:
        """Token'ın süresi dolmuş mu kontrol et"""
        try:
            jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except:
            return True