import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from database import Database
from auth import Auth

# Cargar variables de entorno
load_dotenv()

# Crear aplicación Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'clave_secreta_default'

# Configuración
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Inicializar base de datos y autenticación
db = Database()
auth = Auth(db)

# Crear carpetas necesarias
os.makedirs('instance', exist_ok=True)
os.makedirs('uploads', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# ==================== RUTAS PÚBLICAS ====================

@app.route('/')
def index():
    """Página principal"""
    if 'user_id' in session:
        # Redirigir al dashboard según rol
        rol = session.get('rol')
        if rol == 'admin':
            return redirect(url_for('dashboard_admin'))
        elif rol == 'funcionario':
            return redirect(url_for('dashboard_funcionario'))
        elif rol == 'jefe':
            return redirect(url_for('dashboard_jefe'))
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    
    # Generar código de verificación si no existe en sesión
    if 'codigo_verificacion' not in session:
        session['codigo_verificacion'] = auth.generar_codigo_verificacion()
    
    if request.method == 'POST':
        # Obtener datos del formulario
        tipo_usuario = request.form.get('tipo_usuario')
        ci = request.form.get('ci')
        username = request.form.get('username')
        password = request.form.get('password')
        codigo_ingresado = request.form.get('codigo_verificacion')
        
        # Validar código de verificación
        if codigo_ingresado != session.get('codigo_verificacion'):
            flash('Código de verificación incorrecto', 'danger')
            session['codigo_verificacion'] = auth.generar_codigo_verificacion()
            return render_template('login.html', codigo=session['codigo_verificacion'])
        
        # Buscar usuario
        usuario = db.get_usuario_by_username(username)
        
        if usuario and usuario['ci'] == ci:
            # Verificar contraseña
            if auth.verify_password(password, usuario['password_hash']):
                # Verificar que el rol coincida
                if usuario['rol'] == tipo_usuario:
                    # Iniciar sesión
                    session['user_id'] = usuario['id']
                    session['username'] = usuario['username']
                    session['ci'] = usuario['ci']
                    session['email'] = usuario['email']
                    session['rol'] = usuario['rol']
                    
                    # Actualizar último acceso
                    db.actualizar_ultimo_acceso(usuario['id'])
                    
                    flash(f'¡Bienvenido(a) {usuario["username"]}!', 'success')
                    
                    # Redirigir según rol
                    if usuario['rol'] == 'admin':
                        return redirect(url_for('dashboard_admin'))
                    elif usuario['rol'] == 'funcionario':
                        return redirect(url_for('dashboard_funcionario'))
                    elif usuario['rol'] == 'jefe':
                        return redirect(url_for('dashboard_jefe'))
                else:
                    flash('El tipo de usuario no coincide con su rol asignado', 'danger')
            else:
                flash('Contraseña incorrecta', 'danger')
        else:
            flash('Usuario o CI incorrectos', 'danger')
        
        # Generar nuevo código
        session['codigo_verificacion'] = auth.generar_codigo_verificacion()
    
    return render_template('login.html', codigo=session['codigo_verificacion'])

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('index'))

@app.route('/generar-codigo')
def generar_codigo():
    """Generar nuevo código de verificación"""
    session['codigo_verificacion'] = auth.generar_codigo_verificacion()
    return {'codigo': session['codigo_verificacion']}

# ==================== RUTAS DE ADMIN ====================

@app.route('/admin/dashboard')
@auth.login_required
@auth.role_required(['admin'])
def dashboard_admin():
    """Dashboard para administradores"""
    # Obtener estadísticas
    conteo_estados = db.contar_funcionarios_por_estado()
    total_funcionarios = sum(conteo_estados.values())
    
    return render_template('dashboard_admin.html',
                         total_funcionarios=total_funcionarios,
                         pendientes=conteo_estados['pendiente'],
                         activos=conteo_estados['activo'])

@app.route('/admin/funcionarios')
@auth.login_required
@auth.role_required(['admin'])
def funcionarios_lista():
    """Lista de funcionarios"""
    funcionarios = db.get_all_funcionarios()
    return render_template('funcionarios_lista.html', funcionarios=funcionarios)

@app.route('/admin/funcionarios/nuevo', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['admin'])
def funcionario_nuevo():
    """Registrar nuevo funcionario - COMPLETO"""
    if request.method == 'POST':
        try:
            # Obtener todos los datos del formulario
            datos = {
                # Datos personales
                'ci': request.form.get('ci'),
                'primer_apellido': request.form.get('primer_apellido'),
                'segundo_apellido': request.form.get('segundo_apellido'),
                'tercer_apellido': request.form.get('tercer_apellido'),
                'primer_nombre': request.form.get('primer_nombre'),
                'segundo_nombre': request.form.get('segundo_nombre'),
                'tercer_nombre': request.form.get('tercer_nombre'),
                'tipo_identificacion': request.form.get('tipo_identificacion'),
                
                # Datos de resolución
                'nro_resolucion': request.form.get('nro_resolucion'),
                'fecha_resolucion': request.form.get('fecha_resolucion'),
                'fecha_posesion': request.form.get('fecha_posesion'),
                'nro_memorandum_designacion': request.form.get('nro_memorandum_designacion'),
                'fecha_memorandum': request.form.get('fecha_memorandum'),
                
                # Datos de ítem
                'nro_item': request.form.get('nro_item'),
                'administracion': request.form.get('administracion'),
                'jerarquia': request.form.get('jerarquia'),
                'depende_de': request.form.get('depende_de'),
                'unidad_organizacional': request.form.get('unidad_organizacional'),
                'cargo': request.form.get('cargo'),
                'puesto': request.form.get('puesto'),
                'direccion_oficina': request.form.get('direccion_oficina'),
                'piso_interno': request.form.get('piso_interno'),
                
                # Archivos (por ahora solo nombres)
                'firma_path': '',  # Aquí irían las rutas si subimos archivos
                'foto_path': '',
                'huella_path': '',
            }
            
            # Generar usuario y datos automáticos
            primer_nombre = datos['primer_nombre'].lower()
            primer_apellido = datos['primer_apellido'].lower()
            username_base = f"{primer_nombre}.{primer_apellido}"
            
            # Verificar si el username ya existe
            usuario_existente = db.get_usuario_by_username(username_base)
            contador = 1
            username_final = username_base
            
            while usuario_existente:
                if datos.get('segundo_apellido'):
                    inicial = datos['segundo_apellido'][0].lower()
                    username_final = f"{username_base}.{inicial}"
                else:
                    username_final = f"{username_base}{contador}"
                    contador += 1
                usuario_existente = db.get_usuario_by_username(username_final)
            
            # Agregar datos generados al diccionario
            datos['usuario_aplicacion'] = username_final
            datos['clave_generada'] = datos['ci']  # Contraseña inicial = CI
            datos['correo_interno'] = f"{username_final}@gobierno.talento.bo"
            
            # Crear funcionario
            funcionario_id = db.crear_funcionario(datos)
            
            # Crear usuario para el funcionario
            password_hash = auth.hash_password(datos['ci'])
            user_id = db.crear_usuario(
                ci=datos['ci'],
                username=username_final,
                email=datos['correo_interno'],
                password_hash=password_hash,
                rol='funcionario'
            )
            
            flash(f'✅ Funcionario registrado exitosamente!', 'success')
            flash(f'📋 Usuario: {username_final}', 'info')
            flash(f'🔑 Contraseña: {datos["ci"]} (CI del funcionario)', 'info')
            flash(f'📧 Correo: {datos["correo_interno"]}', 'info')
            
            return redirect(url_for('funcionarios_lista'))
            
        except Exception as e:
            flash(f'❌ Error al registrar funcionario: {str(e)}', 'danger')
    
    return render_template('funcionario_nuevo.html')

# ==================== RUTAS DE FUNCIONARIO ====================

# ==================== RUTAS PARA GESTIÓN DE FUNCIONARIOS ====================

@app.route('/admin/funcionarios/ver/<ci>')
@auth.login_required
@auth.role_required(['admin'])
def funcionario_ver(ci):
    """Ver detalles de un funcionario"""
    funcionario = db.get_funcionario_by_ci(ci)
    if not funcionario:
        flash('Funcionario no encontrado', 'danger')
        return redirect(url_for('funcionarios_lista'))
    
    return render_template('funcionario_ver.html', funcionario=funcionario)

@app.route('/admin/funcionarios/editar/<ci>', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['admin'])
def funcionario_editar(ci):
    """Editar funcionario existente"""
    funcionario = db.get_funcionario_by_ci(ci)
    if not funcionario:
        flash('Funcionario no encontrado', 'danger')
        return redirect(url_for('funcionarios_lista'))
    
    if request.method == 'POST':
        try:
            # Actualizar los datos (simplificado por ahora)
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Datos actualizables (excluyendo CI y campos generados)
            campos_actualizables = [
                'primer_apellido', 'segundo_apellido', 'tercer_apellido',
                'primer_nombre', 'segundo_nombre', 'tercer_nombre',
                'tipo_identificacion', 'nro_resolucion', 'fecha_resolucion',
                'fecha_posesion', 'nro_memorandum_designacion', 'fecha_memorandum',
                'nro_item', 'administracion', 'jerarquia', 'depende_de',
                'unidad_organizacional', 'cargo', 'puesto', 'direccion_oficina',
                'piso_interno', 'estado'
            ]
            
            # Construir query de actualización
            set_clause = []
            valores = []
            
            for campo in campos_actualizables:
                valor = request.form.get(campo)
                if valor is not None:
                    set_clause.append(f"{campo} = ?")
                    valores.append(valor)
            
            # Agregar fecha de actualización
            set_clause.append("fecha_actualizacion = CURRENT_TIMESTAMP")
            
            # Agregar CI al final para WHERE
            valores.append(ci)
            
            query = f"UPDATE funcionarios SET {', '.join(set_clause)} WHERE ci = ?"
            cursor.execute(query, valores)
            conn.commit()
            conn.close()
            
            flash('✅ Funcionario actualizado correctamente', 'success')
            return redirect(url_for('funcionario_ver', ci=ci))
            
        except Exception as e:
            flash(f'❌ Error al actualizar funcionario: {str(e)}', 'danger')
    
    return render_template('funcionario_editar.html', funcionario=funcionario)

@app.route('/admin/funcionarios/baja/<ci>', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['admin'])
def funcionario_baja(ci):
    """Dar de baja a un funcionario"""
    funcionario = db.get_funcionario_by_ci(ci)
    if not funcionario:
        flash('Funcionario no encontrado', 'danger')
        return redirect(url_for('funcionarios_lista'))
    
     # Obtener fecha actual
    from datetime import datetime
    hoy = datetime.now().strftime('%Y-%m-%d')
    
    if request.method == 'POST':
        try:
            motivo = request.form.get('motivo_baja')
            nro_memorandum = request.form.get('nro_memorandum_retiro')
            fecha_retiro = request.form.get('fecha_retiro')
            
            # Actualizar estado del funcionario
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE funcionarios 
            SET estado = 'baja', 
                fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE ci = ?
            ''', (ci,))
            
            # También desactivar usuario asociado
            cursor.execute('''
            UPDATE usuarios 
            SET activo = 0 
            WHERE ci = ?
            ''', (ci,))
            
            conn.commit()
            conn.close()
            
            flash(f'✅ Funcionario {funcionario["primer_nombre"]} {funcionario["primer_apellido"]} dado de baja', 'success')
            return redirect(url_for('funcionarios_lista'))
            
        except Exception as e:
            flash(f'❌ Error al dar de baja: {str(e)}', 'danger')
    
    return render_template('funcionario_baja.html', funcionario=funcionario)

@app.route('/admin/funcionarios/activar/<ci>')
@auth.login_required
@auth.role_required(['admin'])
def funcionario_activar(ci):
    """Reactivar un funcionario dado de baja"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE funcionarios 
        SET estado = 'activo', 
            fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE ci = ?
        ''', (ci,))
        
        # Reactivar usuario asociado
        cursor.execute('''
        UPDATE usuarios 
        SET activo = 1 
        WHERE ci = ?
        ''', (ci,))
        
        conn.commit()
        conn.close()
        
        flash('✅ Funcionario reactivado correctamente', 'success')
        
    except Exception as e:
        flash(f'❌ Error al reactivar: {str(e)}', 'danger')
    
    return redirect(url_for('funcionarios_lista'))

# ==================== RUTAS PARA FUNCIONARIO ====================

@app.route('/funcionario/completar-ficha')
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_completar_ficha():
    """Página principal para completar la ficha TALENTO"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    # Calcular progreso (simulado por ahora)
    progreso = 25
    secciones = {
        'datos_personales': False,
        'formacion': False,
        'seguro_social': False,
        'experiencia': False
    }
    
    return render_template('funcionario/completar_ficha.html', 
                         funcionario=funcionario,
                         progreso=progreso,
                         secciones=secciones)

@app.route('/funcionario/datos-personales', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_datos_personales():
    """Funcionario completa sus datos personales (Actividad 5)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    if not funcionario:
        flash('Funcionario no encontrado', 'danger')
        return redirect(url_for('dashboard_funcionario'))
    
    # Obtener parámetros para los dropdowns
    parametros = {
        'genero': db.get_parametros('genero'),
        'departamentos': db.get_parametros('departamentos'),
        'paises': db.get_parametros('paises'),
        'estado_civil': db.get_parametros('estado_civil'),
        'tipo_sangre': db.get_parametros('tipo_sangre'),
        'gestora': db.get_parametros('gestora'),
        'parentesco': db.get_parametros('parentesco'),
        'nacionalidad': db.get_parametros('nacionalidad')
    }
    
    # Obtener datos adicionales existentes
    datos_adicionales = db.get_datos_adicionales(funcionario['id'])
    
    # Obtener parientes existentes
    parientes = db.get_parientes(funcionario['id'])
    
    # Enriquecer parientes con nombres de parámetros
    for pariente in parientes:
        # Buscar nombre del parentesco
        for parent in parametros['parentesco']:
            if parent['codigo'] == pariente['parentesco']:
                pariente['parentesco_nombre'] = parent['nombre']
                break
        
        # Buscar nombre de nacionalidad
        for nac in parametros['nacionalidad']:
            if nac['codigo'] == pariente['nacionalidad']:
                pariente['nacionalidad_nombre'] = nac['nombre']
                break
    
    if request.method == 'POST':
        try:
            # 1. Guardar datos adicionales
            datos = {
                'genero': request.form.get('genero'),
                'expedido_en': request.form.get('expedido_en'),
                'fecha_nacimiento': request.form.get('fecha_nacimiento'),
                'pais_nacimiento': request.form.get('pais_nacimiento'),
                'depto_nacimiento': request.form.get('depto_nacimiento'),
                'provincia_nacimiento': request.form.get('provincia_nacimiento'),
                'lugar_nacimiento': request.form.get('lugar_nacimiento'),
                'nro_libreta_militar': request.form.get('nro_libreta_militar'),
                'gestora': request.form.get('gestora'),
                'nro_nua': request.form.get('nro_nua'),
                'tipo_sangre': request.form.get('tipo_sangre'),
                'fecha_caducidad_ci': request.form.get('fecha_caducidad_ci'),
                'estado_civil': request.form.get('estado_civil'),
                'nro_hijos': request.form.get('nro_hijos'),
                'nro_dependientes': request.form.get('nro_dependientes'),
                'direccion_domicilio': request.form.get('direccion_domicilio'),
                'nro_domicilio': request.form.get('nro_domicilio'),
                'zona_domicilio': request.form.get('zona_domicilio'),
                'ciudad_localidad': request.form.get('ciudad_localidad'),
                'tipo_vivienda': request.form.get('tipo_vivienda'),
                'nombre_tipo_vivienda': request.form.get('nombre_tipo_vivienda'),
                'piso': request.form.get('piso'),
                'depto': request.form.get('depto'),
                'casilla': request.form.get('casilla'),
                'correo_electronico1': request.form.get('correo_electronico1'),
                'correo_electronico2': request.form.get('correo_electronico2'),
                'telefono_fijo1': request.form.get('telefono_fijo1'),
                'telefono_fijo2': request.form.get('telefono_fijo2'),
                'telefono_celular1': request.form.get('telefono_celular1'),
                'telefono_celular2': request.form.get('telefono_celular2'),
                'nro_carrera_administrativa': request.form.get('nro_carrera_administrativa'),
                'licencia_conducir': request.form.get('licencia_conducir'),
                'categoria_licencia': request.form.get('categoria_licencia'),
                'emergencia_contacto': request.form.get('emergencia_contacto'),
                'nro_declaracion_jurada': request.form.get('nro_declaracion_jurada'),
                'fecha_declaracion_jurada': request.form.get('fecha_declaracion_jurada')
            }
            
            # Validaciones especiales
            if datos['genero'] == 'M' and not datos['nro_libreta_militar']:
                flash('El número de libreta de servicio militar es obligatorio para varones', 'danger')
                return render_template('funcionario/datos_personales.html',
                                     funcionario=funcionario,
                                     parametros=parametros,
                                     datos_adicionales=datos_adicionales,
                                     parientes=parientes,
                                     hoy=datetime.now().strftime('%Y-%m-%d'),
                                     fecha_max_nacimiento=(datetime.now() - timedelta(days=365*18)).strftime('%Y-%m-%d'))
            
            # Guardar datos adicionales
            db.guardar_datos_adicionales(funcionario['id'], datos)
            
            # 2. Procesar parientes nuevos
            parientes_nuevos = []
            i = 0
            while f'parientes_nuevos[{i}][parentesco]' in request.form:
                pariente = {
                    'parentesco': request.form.get(f'parientes_nuevos[{i}][parentesco]'),
                    'primer_apellido': request.form.get(f'parientes_nuevos[{i}][primer_apellido]'),
                    'segundo_apellido': request.form.get(f'parientes_nuevos[{i}][segundo_apellido]'),
                    'nombres': request.form.get(f'parientes_nuevos[{i}][nombres]'),
                    'nacionalidad': request.form.get(f'parientes_nuevos[{i}][nacionalidad]'),
                    'telefono': request.form.get(f'parientes_nuevos[{i}][telefono]'),
                    'genero': request.form.get(f'parientes_nuevos[{i}][genero]'),
                    'fecha_nacimiento': request.form.get(f'parientes_nuevos[{i}][fecha_nacimiento]'),
                    'tipo_identificacion': request.form.get(f'parientes_nuevos[{i}][tipo_identificacion]'),
                    'numero_identificacion': request.form.get(f'parientes_nuevos[{i}][numero_identificacion]')
                }
                parientes_nuevos.append(pariente)
                i += 1
            
            # Guardar parientes nuevos
            for pariente in parientes_nuevos:
                db.guardar_pariente(funcionario['id'], pariente)
            
            # 3. Procesar parientes a eliminar
            parientes_eliminar = request.form.getlist('parientes_eliminar[]')
            for pariente_id in parientes_eliminar:
                db.eliminar_pariente(pariente_id)
            
            flash('✅ Datos personales guardados correctamente', 'success')
            
            # Actualizar estado del funcionario si es la primera vez
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE funcionarios SET estado = 'en_proceso' WHERE id = ?", (funcionario['id'],))
            conn.commit()
            conn.close()
            
            return redirect(url_for('funcionario_completar_ficha'))
            
        except Exception as e:
            flash(f'❌ Error al guardar datos: {str(e)}', 'danger')
    
    # Para GET, calcular fechas límite
    hoy = datetime.now().strftime('%Y-%m-%d')
    fecha_max_nacimiento = (datetime.now() - timedelta(days=365*18)).strftime('%Y-%m-%d')
    
    return render_template('funcionario/datos_personales.html',
                         funcionario=funcionario,
                         parametros=parametros,
                         datos_adicionales=datos_adicionales,
                         parientes=parientes,
                         hoy=hoy,
                         fecha_max_nacimiento=fecha_max_nacimiento)

@app.route('/funcionario/formacion-academica', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_formacion_academica():
    """Funcionario completa formación académica (Actividad 6)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    if request.method == 'POST':
        flash('Formación académica guardada correctamente', 'success')
        return redirect(url_for('funcionario_completar_ficha'))
    
    return render_template('funcionario/formacion_academica.html', funcionario=funcionario)

@app.route('/funcionario/seguro-social', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_seguro_social():
    """Funcionario completa seguro social (Actividad 7)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    if request.method == 'POST':
        flash('Seguro social guardado correctamente', 'success')
        return redirect(url_for('funcionario_completar_ficha'))
    
    return render_template('funcionario/seguro_social.html', funcionario=funcionario)

@app.route('/funcionario/experiencia-laboral', methods=['GET', 'POST'])
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_experiencia_laboral():
    """Funcionario completa experiencia laboral (Actividad 8)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    if request.method == 'POST':
        flash('Experiencia laboral guardada correctamente', 'success')
        return redirect(url_for('funcionario_completar_ficha'))
    
    return render_template('funcionario/experiencia_laboral.html', funcionario=funcionario)

@app.route('/funcionario/documentos')
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_documentos():
    """Funcionario sube documentos de soporte"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    return render_template('funcionario/documentos.html', funcionario=funcionario)

@app.route('/funcionario/revisar-formulario')
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_revisar_formulario():
    """Funcionario revisa formulario completo (Actividad 9)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    return render_template('funcionario/revisar_formulario.html', funcionario=funcionario)

@app.route('/funcionario/imprimir-formulario')
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_imprimir_formulario():
    """Funcionario imprime formulario (Actividad 10)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    return render_template('funcionario/imprimir_formulario.html', funcionario=funcionario)

@app.route('/funcionario/ver-tramite')
@auth.login_required
@auth.role_required(['funcionario'])
def funcionario_tramite():
    """Funcionario ve número de trámite (Actividad 11)"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    # Generar número de trámite ficticio
    import random
    nro_tramite = f"TAL-{random.randint(1000, 9999)}-2025"
    
    return render_template('funcionario/ver_tramite.html', 
                         funcionario=funcionario,
                         nro_tramite=nro_tramite)

# Actualizar el dashboard del funcionario para pasar datos de progreso
@app.route('/funcionario/dashboard')
@auth.login_required
@auth.role_required(['funcionario'])
def dashboard_funcionario():
    """Dashboard para funcionarios"""
    funcionario = db.get_funcionario_by_ci(session.get('ci', ''))
    
    if not funcionario:
        flash('Funcionario no encontrado', 'danger')
        return redirect(url_for('logout'))
    
    # Calcular progreso real
    progreso, secciones = db.calcular_progreso_funcionario(funcionario['id'])
    
    return render_template('dashboard_funcionario.html', 
                         funcionario=funcionario,
                         progreso=progreso,
                         secciones=secciones)

# ==================== RUTAS DE JEFE ====================

@app.route('/jefe/dashboard')
@auth.login_required
@auth.role_required(['jefe'])
def dashboard_jefe():
    """Dashboard para jefes de departamento"""
    return render_template('dashboard_jefe.html')

# ==================== EJECUCIÓN ====================

if __name__ == '__main__':
    print("🚀 Iniciando Sistema Talento Humano...")
    print("🌐 Accede en: http://localhost:5000")
    print("👤 Usuario admin: admin / admin123")
    app.run(debug=True, port=5000)