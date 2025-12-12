import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

class Auth:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password):
        """Hash simple de contraseña (para desarrollo)"""
        salt = "talento_humano_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password, password_hash):
        """Verificar contraseña"""
        return self.hash_password(password) == password_hash
    
    def login_required(self, f):
        """Decorador para requerir login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Por favor inicie sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def role_required(self, roles):
        """Decorador para requerir rol específico"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    flash('Por favor inicie sesión.', 'warning')
                    return redirect(url_for('login'))
                
                if session.get('rol') not in roles:
                    flash('No tiene permisos para acceder a esta página.', 'danger')
                    return redirect(url_for('dashboard'))
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def generar_codigo_verificacion(self):
        """Generar código de verificación de 4 dígitos"""
        return ''.join(secrets.choice('0123456789') for _ in range(4))