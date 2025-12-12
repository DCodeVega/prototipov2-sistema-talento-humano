import sqlite3
import os
import hashlib  # <-- AÑADE ESTO
from datetime import datetime

class Database:
    def __init__(self, db_path='instance/talento.db'):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        return conn
    
    def hash_password(self, password):
        """Función para hashear contraseñas"""
        salt = "talento_humano_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def init_db(self):
        """Inicializar base de datos con tablas necesarias"""
        # Crear directorio instance si no existe
        os.makedirs('instance', exist_ok=True)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'funcionario',
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ultimo_acceso TIMESTAMP
        )
        ''')
        
        # Tabla de funcionarios (según documento R-100)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ci TEXT UNIQUE NOT NULL,
            primer_apellido TEXT NOT NULL,
            segundo_apellido TEXT,
            tercer_apellido TEXT,
            primer_nombre TEXT NOT NULL,
            segundo_nombre TEXT,
            tercer_nombre TEXT,
            tipo_identificacion TEXT DEFAULT 'CI',
            
            -- Campos básicos del sistema
            estado TEXT DEFAULT 'pendiente',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP,
            
            -- === NUEVOS CAMPOS SEGÚN DOCUMENTO R-100 ===
            -- Datos de resolución
            nro_resolucion TEXT,
            fecha_resolucion DATE,
            fecha_posesion DATE,
            nro_memorandum_designacion TEXT,
            fecha_memorandum DATE,
            
            -- Datos de ítem
            nro_item TEXT,
            administracion TEXT,
            jerarquia TEXT,
            depende_de TEXT,
            unidad_organizacional TEXT,
            cargo TEXT,
            puesto TEXT,
            direccion_oficina TEXT,
            piso_interno TEXT,
            
            -- Archivos (rutas)
            firma_path TEXT,
            foto_path TEXT,
            huella_path TEXT,
            
            -- Datos generados
            usuario_aplicacion TEXT,
            clave_generada TEXT,
            correo_interno TEXT
        )
        ''')
        
        # Tabla para documentos de respaldo
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER NOT NULL,
            tipo_documento TEXT NOT NULL,
            nombre_archivo TEXT NOT NULL,
            ruta_archivo TEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
        ''')
        
        # Insertar usuario admin por defecto
        cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
        if not cursor.fetchone():
            # Calcular hash de la contraseña
            password_hash = self.hash_password("admin123")
            
            cursor.execute('''
            INSERT INTO usuarios (ci, username, email, password_hash, rol, activo)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', ('0000000', 'admin', 'admin@gobierno.talento.bo', 
                  password_hash, 'admin', 1))
            print(f"✅ Usuario admin creado con hash: {password_hash[:20]}...")
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada correctamente")
    
    # Métodos CRUD para usuarios
    def get_usuario_by_username(self, username):
        """Obtener usuario por nombre de usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND activo = 1", (username,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario
    
    def get_usuario_by_ci(self, ci):
        """Obtener usuario por CI"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE ci = ? AND activo = 1", (ci,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario
    
    def crear_usuario(self, ci, username, email, password_hash, rol='funcionario'):
        """Crear nuevo usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO usuarios (ci, username, email, password_hash, rol)
            VALUES (?, ?, ?, ?, ?)
            ''', (ci, username, email, password_hash, rol))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError as e:
            conn.close()
            raise Exception(f"Error al crear usuario: {str(e)}")
    
    # Métodos CRUD para funcionarios
    def crear_funcionario(self, datos):
        """Crear nuevo funcionario según formulario R-100"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Lista completa de campos según el documento
        campos = [
            # Datos personales
            'ci', 'primer_apellido', 'segundo_apellido', 'tercer_apellido',
            'primer_nombre', 'segundo_nombre', 'tercer_nombre', 'tipo_identificacion',
            
            # Datos de resolución
            'nro_resolucion', 'fecha_resolucion', 'fecha_posesion',
            'nro_memorandum_designacion', 'fecha_memorandum',
            
            # Datos de ítem
            'nro_item', 'administracion', 'jerarquia', 'depende_de',
            'unidad_organizacional', 'cargo', 'puesto',
            'direccion_oficina', 'piso_interno',
            
            # Archivos (solo rutas por ahora)
            'firma_path', 'foto_path', 'huella_path',
            
            # Datos generados
            'usuario_aplicacion', 'clave_generada', 'correo_interno'
        ]
        
        # Asegurar que todos los campos existan en el diccionario datos
        valores = [datos.get(campo) for campo in campos]
        
        cursor.execute(f'''
        INSERT INTO funcionarios ({', '.join(campos)})
        VALUES ({', '.join(['?'] * len(campos))})
        ''', valores)
        
        funcionario_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return funcionario_id
    
    def get_funcionario_by_ci(self, ci):
        """Obtener funcionario por CI"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE ci = ?", (ci,))
        funcionario = cursor.fetchone()
        conn.close()
        return funcionario
    
    def get_all_funcionarios(self):
        """Obtener todos los funcionarios"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM funcionarios ORDER BY fecha_registro DESC")
        funcionarios = cursor.fetchall()
        conn.close()
        return funcionarios
    
    def contar_funcionarios_por_estado(self):
        """Contar funcionarios por estado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT estado, COUNT(*) as cantidad FROM funcionarios GROUP BY estado")
        resultados = cursor.fetchall()
        
        # Crear diccionario con todos los estados
        conteo = {
            'pendiente': 0,
            'activo': 0,
            'inactivo': 0,
            'baja': 0
        }
        
        for row in resultados:
            estado = row['estado']
            if estado in conteo:
                conteo[estado] = row['cantidad']
        
        conn.close()
        return conteo
    
    def actualizar_ultimo_acceso(self, user_id):
        """Actualizar último acceso del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()