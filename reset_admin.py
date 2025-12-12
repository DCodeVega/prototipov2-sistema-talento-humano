#!/usr/bin/env python3
import sqlite3
import hashlib

def reset_admin_password():
    """Resetear contraseña del admin a 'admin123'"""
    
    # Conectar a la base de datos
    conn = sqlite3.connect('instance/talento.db')
    cursor = conn.cursor()
    
    # Calcular hash
    salt = "talento_humano_2025"
    password = "admin123"
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Actualizar contraseña
    cursor.execute('''
    UPDATE usuarios 
    SET password_hash = ?
    WHERE username = 'admin'
    ''', (password_hash,))
    
    if cursor.rowcount > 0:
        print(f"✅ Contraseña de admin actualizada a: {password}")
        print(f"🔑 Hash generado: {password_hash}")
    else:
        print("❌ No se encontró usuario admin")
        # Crearlo si no existe
        cursor.execute('''
        INSERT INTO usuarios (ci, username, email, password_hash, rol, activo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('0000000', 'admin', 'admin@gobierno.talento.bo', 
              password_hash, 'admin', 1))
        print("✅ Usuario admin creado")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    reset_admin_password()