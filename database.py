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
        
        cursor.execute('''
    CREATE TABLE IF NOT EXISTS datos_adicionales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    genero TEXT,
    expedido_en TEXT,
    fecha_nacimiento DATE,
    pais_nacimiento TEXT,
    depto_nacimiento TEXT,
    provincia_nacimiento TEXT,
    lugar_nacimiento TEXT,
    nro_libreta_militar TEXT,
    afp TEXT,
    nro_nua TEXT,
    tipo_sangre TEXT,
    fecha_caducidad_ci DATE,
    estado_civil TEXT,
    nro_hijos INTEGER DEFAULT 0,
    nro_dependientes INTEGER DEFAULT 0,
    direccion_domicilio TEXT,
    nro_domicilio TEXT,
    zona_domicilio TEXT,
    ciudad_localidad TEXT,
    tipo_vivienda TEXT,
    nombre_tipo_vivienda TEXT,
    piso TEXT,
    depto TEXT,
    casilla TEXT,
    correo_electronico1 TEXT,
    correo_electronico2 TEXT,
    telefono_fijo1 TEXT,
    telefono_fijo2 TEXT,
    telefono_celular1 TEXT,
    telefono_celular2 TEXT,
    nro_carrera_administrativa TEXT,
    fecha_cas DATE,
    anos_cas INTEGER,
    meses_cas INTEGER,
    dias_cas INTEGER,
    licencia_conducir TEXT,
    categoria_licencia TEXT,
    emergencia_contacto TEXT,
    nro_declaracion_jurada TEXT,
    fecha_declaracion_jurada DATE,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para parientes
        cursor.execute('''
CREATE TABLE IF NOT EXISTS parientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    parentesco TEXT,
    primer_apellido TEXT,
    segundo_apellido TEXT,
    nombres TEXT,
    nacionalidad TEXT,
    telefono TEXT,
    genero TEXT,
    fecha_nacimiento DATE,
    tipo_identificacion TEXT,
    numero_identificacion TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para formación académica
        cursor.execute('''
CREATE TABLE IF NOT EXISTS formacion_academica (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    pais_estudio TEXT,
    estado_instruccion TEXT,
    nivel_instruccion TEXT,
    area TEXT,
    tipo_entidad_academica TEXT,
    institucion_academica TEXT,
    nombre_institucion TEXT,
    carrera TEXT,
    titulado TEXT,
    documento_respaldo TEXT,
    detalle_documento TEXT,
    fecha_inicio DATE,
    fecha_final DATE,
    nro_titulo_academico TEXT,
    fecha_emision_titulo DATE,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para bachillerato
        cursor.execute('''
CREATE TABLE IF NOT EXISTS bachillerato (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    es_bachiller TEXT,
    ano INTEGER,
    unidad_educativa TEXT,
    ultimo_curso_vencido TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para cursos
        cursor.execute('''
CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    nivel_instruccion TEXT,
    area TEXT,
    nombre_curso TEXT,
    tipo_entidad_academica TEXT,
    institucion_academica TEXT,
    nro_horas INTEGER,
    fecha_inicio DATE,
    fecha_final DATE,
    documento_respaldo TEXT,
    detalle_documento TEXT,
    pais_estudio TEXT,
    depto_estudio TEXT,
    capacitacion TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para idiomas
        cursor.execute('''
CREATE TABLE IF NOT EXISTS idiomas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    idioma TEXT,
    habla TEXT,
    escribe TEXT,
    lee TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para experiencia laboral
        cursor.execute('''
CREATE TABLE IF NOT EXISTS experiencia_laboral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    entidad_empresa TEXT,
    area_departamento TEXT,
    tipo_entidad TEXT,
    puesto TEXT,
    jerarquia TEXT,
    cargo_mando TEXT,
    nro_dependientes INTEGER,
    fecha_inicio DATE,
    fecha_final DATE,
    forma_ingreso TEXT,
    causa_retiro TEXT,
    nit_empresa TEXT,
    haber_basico REAL,
    pais TEXT,
    descripcion_labores TEXT,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

# Tabla para capacitaciones impartidas
        cursor.execute('''
CREATE TABLE IF NOT EXISTS capacitaciones_impartidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    tipo_entidad_academica TEXT,
    institucion_academica TEXT,
    nombre_institucion TEXT,
    tipo_capacitacion TEXT,
    carrera TEXT,
    asignatura_tema TEXT,
    nro_horas INTEGER,
    fecha_desde DATE,
    fecha_hasta DATE,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
)
''')

        print("✅ Tablas de datos de funcionario creadas")
        
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
        
        # Tablas de parámetros (catálogos)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_genero (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_departamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_paises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_estado_civil (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_tipo_sangre (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_gestora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_parentesco (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS parametros_nacionalidad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            activo INTEGER DEFAULT 1
        )
        ''')

        # Insertar datos básicos en parámetros
        parametros_basicos = {
            'genero': [
                ('M', 'MASCULINO'),
                ('F', 'FEMENINO')
            ],
            'departamentos': [
                ('LP', 'LA PAZ'),
                ('CB', 'COCHABAMBA'),
                ('SC', 'SANTA CRUZ'),
                ('OR', 'ORURO'),
                ('PT', 'POTOSÍ'),
                ('TJ', 'TARIJA'),
                ('CH', 'CHUQUISACA'),
                ('BN', 'BENI'),
                ('PD', 'PANDO')
            ],
            'paises': [
                ('BOL', 'BOLIVIA'),
                ('ARG', 'ARGENTINA'),
                ('BRA', 'BRASIL'),
                ('CHL', 'CHILE'),
                ('PER', 'PERÚ')
            ],
            'estado_civil': [
                ('S', 'SOLTERO(A)'),
                ('C', 'CASADO(A)'),
                ('D', 'DIVORCIADO(A)'),
                ('V', 'VIUDO(A)'),
                ('U', 'UNIÓN LIBRE')
            ],
            'tipo_sangre': [
                ('A+', 'A+'),
                ('A-', 'A-'),
                ('B+', 'B+'),
                ('B-', 'B-'),
                ('AB+', 'AB+'),
                ('AB-', 'AB-'),
                ('O+', 'O+'),
                ('O-', 'O-')
            ],
            'gestora': [
                ('CSS', 'CAJA DE SALUD DE SEGUROS SOCIALES'),
                ('CPS', 'CAJA PETROLERA DE SALUD'),
                ('CNS', 'CAJA NACIONAL DE SALUD'),
                ('CSM', 'CAJA DE SALUD DE LA MUJER'),
                ('CSR', 'CAJA DE SALUD RURAL')
            ],
            'parentesco': [
                ('PAD', 'PADRE'),
                ('MAD', 'MADRE'),
                ('CON', 'CÓNYUGUE'),
                ('HIJ', 'HIJO(A)'),
                ('HER', 'HERMANO(A)'),
                ('OTR', 'OTRO')
            ],
            'nacionalidad': [
                ('BOL', 'BOLIVIANA'),
                ('ARG', 'ARGENTINA'),
                ('BRA', 'BRASILEÑA'),
                ('CHL', 'CHILENA'),
                ('PER', 'PERUANA'),
                ('OTR', 'OTRA')
            ]
        }

        for tabla, datos in parametros_basicos.items():
            cursor.execute(f"SELECT COUNT(*) FROM parametros_{tabla}")
            if cursor.fetchone()[0] == 0:
                for codigo, nombre in datos:
                    cursor.execute(f"INSERT INTO parametros_{tabla} (codigo, nombre) VALUES (?, ?)", (codigo, nombre))
                print(f"✅ Datos insertados en: parametros_{tabla}")

        conn.commit()
        conn.close()
        print("✅ Tablas de parámetros creadas e inicializadas")
    
    def get_parametros(self, tipo):
        """Obtener lista de parámetros por tipo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tablas_validas = ['genero', 'departamentos', 'paises', 'estado_civil', 
                        'tipo_sangre', 'gestora', 'parentesco', 'nacionalidad']
        
        if tipo not in tablas_validas:
            conn.close()
            return []
        
        cursor.execute(f"SELECT codigo, nombre FROM parametros_{tipo} WHERE activo = 1 ORDER BY nombre")
        resultados = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in resultados]

    def get_datos_adicionales(self, funcionario_id):
        """Obtener datos adicionales del funcionario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM datos_adicionales WHERE funcionario_id = ?", (funcionario_id,))
        datos = cursor.fetchone()
        conn.close()
        return datos

    def get_parientes(self, funcionario_id):
        """Obtener parientes del funcionario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parientes WHERE funcionario_id = ? ORDER BY parentesco", (funcionario_id,))
        parientes = cursor.fetchall()
        conn.close()
        return [dict(p) for p in parientes]

    def guardar_datos_adicionales(self, funcionario_id, datos):
        """Guardar o actualizar datos adicionales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existen datos
        cursor.execute("SELECT id FROM datos_adicionales WHERE funcionario_id = ?", (funcionario_id,))
        existe = cursor.fetchone()
        
        if existe:
            # Actualizar
            campos = []
            valores = []
            for campo, valor in datos.items():
                if valor is not None:
                    campos.append(f"{campo} = ?")
                    valores.append(valor)
            
            valores.append(funcionario_id)
            query = f"UPDATE datos_adicionales SET {', '.join(campos)} WHERE funcionario_id = ?"
            cursor.execute(query, valores)
        else:
            # Insertar
            campos = ['funcionario_id'] + list(datos.keys())
            placeholders = ['?'] * len(campos)
            valores = [funcionario_id] + list(datos.values())
            
            query = f"INSERT INTO datos_adicionales ({', '.join(campos)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, valores)
        
        conn.commit()
        conn.close()
        return True

    def guardar_pariente(self, funcionario_id, datos_pariente):
        """Guardar un pariente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        campos = ['funcionario_id'] + list(datos_pariente.keys())
        placeholders = ['?'] * len(campos)
        valores = [funcionario_id] + list(datos_pariente.values())
        
        query = f"INSERT INTO parientes ({', '.join(campos)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(query, valores)
        
        pariente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pariente_id

    def eliminar_pariente(self, pariente_id):
        """Eliminar un pariente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parientes WHERE id = ?", (pariente_id,))
        conn.commit()
        conn.close()
        return True    
          
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
    
    # Agrega este método en database.py para calcular progreso
    def calcular_progreso_funcionario(self, funcionario_id):
        """Calcular progreso de completado de ficha TALENTO"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar qué tablas tienen datos
        secciones = {
            'datos_personales': False,
            'formacion': False,
            'seguro_social': False,
            'experiencia': False
        }
        
    def get_formacion_academica(self, funcionario_id):
        """Obtener formación académica del funcionario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener bachillerato
        cursor.execute("SELECT * FROM bachillerato WHERE funcionario_id = ?", (funcionario_id,))
        bachillerato = cursor.fetchone()
        
        # Obtener estudios superiores
        cursor.execute("SELECT * FROM formacion_academica WHERE funcionario_id = ?", (funcionario_id,))
        estudios_superiores = cursor.fetchall()
        
        # Obtener cursos
        cursor.execute("SELECT * FROM cursos WHERE funcionario_id = ?", (funcionario_id,))
        cursos = cursor.fetchall()
        
        # Obtener idiomas
        cursor.execute("SELECT * FROM idiomas WHERE funcionario_id = ?", (funcionario_id,))
        idiomas = cursor.fetchall()
        
        conn.close()
        
        return {
            'bachillerato': dict(bachillerato) if bachillerato else None,
            'estudios_superiores': [dict(e) for e in estudios_superiores],
            'cursos': [dict(c) for c in cursos],
            'idiomas': [dict(i) for i in idiomas]
        }

    def guardar_bachillerato(self, funcionario_id, datos):
        """Guardar o actualizar bachillerato"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe
        cursor.execute("SELECT id FROM bachillerato WHERE funcionario_id = ?", (funcionario_id,))
        existe = cursor.fetchone()
        
        if existe:
            # Actualizar
            cursor.execute('''
            UPDATE bachillerato SET 
                es_bachiller = ?,
                ano = ?,
                unidad_educativa = ?,
                ultimo_curso_vencido = ?
            WHERE funcionario_id = ?
            ''', (
                datos.get('es_bachiller'),
                datos.get('ano'),
                datos.get('unidad_educativa'),
                datos.get('ultimo_curso_vencido'),
                funcionario_id
            ))
        else:
            # Insertar
            cursor.execute('''
            INSERT INTO bachillerato (
                funcionario_id, es_bachiller, ano, unidad_educativa, ultimo_curso_vencido
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                funcionario_id,
                datos.get('es_bachiller'),
                datos.get('ano'),
                datos.get('unidad_educativa'),
                datos.get('ultimo_curso_vencido')
            ))
        
        conn.commit()
        conn.close()
        return True

    def guardar_estudio_superior(self, funcionario_id, datos):
        """Guardar un estudio superior"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO formacion_academica (
            funcionario_id, pais_estudio, estado_instruccion, nivel_instruccion,
            area, tipo_entidad_academica, institucion_academica, nombre_institucion,
            carrera, titulado, documento_respaldo, detalle_documento,
            fecha_inicio, fecha_final, nro_titulo_academico, fecha_emision_titulo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            funcionario_id,
            datos.get('pais_estudio'),
            datos.get('estado_instruccion'),
            datos.get('nivel_instruccion'),
            datos.get('area'),
            datos.get('tipo_entidad_academica'),
            datos.get('institucion_academica'),
            datos.get('nombre_institucion'),
            datos.get('carrera'),
            datos.get('titulado'),
            datos.get('documento_respaldo'),
            datos.get('detalle_documento'),
            datos.get('fecha_inicio'),
            datos.get('fecha_final'),
            datos.get('nro_titulo_academico'),
            datos.get('fecha_emision_titulo')
        ))
        
        estudio_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return estudio_id

    def guardar_curso(self, funcionario_id, datos):
        """Guardar un curso o capacitación"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO cursos (
            funcionario_id, nivel_instruccion, area, nombre_curso,
            tipo_entidad_academica, institucion_academica, nro_horas,
            fecha_inicio, fecha_final, documento_respaldo, detalle_documento,
            pais_estudio, depto_estudio, capacitacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            funcionario_id,
            datos.get('nivel_instruccion'),
            datos.get('area'),
            datos.get('nombre_curso'),
            datos.get('tipo_entidad_academica'),
            datos.get('institucion_academica'),
            datos.get('nro_horas'),
            datos.get('fecha_inicio'),
            datos.get('fecha_final'),
            datos.get('documento_respaldo'),
            datos.get('detalle_documento'),
            datos.get('pais_estudio'),
            datos.get('depto_estudio'),
            datos.get('capacitacion')
        ))
        
        curso_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return curso_id

    def guardar_idioma(self, funcionario_id, datos):
        """Guardar un idioma"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO idiomas (
            funcionario_id, idioma, habla, escribe, lee
        ) VALUES (?, ?, ?, ?, ?)
        ''', (
            funcionario_id,
            datos.get('idioma'),
            datos.get('habla'),
            datos.get('escribe'),
            datos.get('lee')
        ))
        
        idioma_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return idioma_id

    def eliminar_estudio_superior(self, estudio_id):
        """Eliminar un estudio superior"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM formacion_academica WHERE id = ?", (estudio_id,))
        conn.commit()
        conn.close()
        return True

    def eliminar_curso(self, curso_id):
        """Eliminar un curso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cursos WHERE id = ?", (curso_id,))
        conn.commit()
        conn.close()
        return True

    def eliminar_idioma(self, idioma_id):
        """Eliminar un idioma"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM idiomas WHERE id = ?", (idioma_id,))
        conn.commit()
        conn.close()
        return True    
        
        # Verificar datos personales
        cursor.execute("SELECT COUNT(*) FROM datos_adicionales WHERE funcionario_id = ?", (funcionario_id,))
        if cursor.fetchone()[0] > 0:
            secciones['datos_personales'] = True
        
        # Verificar formación académica
        cursor.execute("SELECT COUNT(*) FROM formacion_academica WHERE funcionario_id = ?", (funcionario_id,))
        if cursor.fetchone()[0] > 0:
            secciones['formacion'] = True
        
        # Verificar seguro social
        # Nota: Necesitaríamos una tabla específica o campo en funcionarios
        
        # Verificar experiencia laboral
        cursor.execute("SELECT COUNT(*) FROM experiencia_laboral WHERE funcionario_id = ?", (funcionario_id,))
        if cursor.fetchone()[0] > 0:
            secciones['experiencia'] = True
        
        conn.close()
        
        # Calcular porcentaje
        completadas = sum(1 for sec in secciones.values() if sec)
        total = len(secciones)
        progreso = int((completadas / total) * 100) if total > 0 else 0
        
        return progreso, secciones
    
    def actualizar_ultimo_acceso(self, user_id):
        """Actualizar último acceso del usuario"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        
    