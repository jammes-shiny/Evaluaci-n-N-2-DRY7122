from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "usuarios.db"

# 1. Base de datos para almacenar usuarios y contraseñas en texto plano
def init_database():
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS credenciales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        password TEXT
    )
    ''')
    conexion.commit()
   # Insertar automáticamente los usuarios de los integrantes si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM credenciales")
    if cursor.fetchone()[0] == 0:
        integrantes = [
            ("jammes", "ClaveDifi%&!"),
            ("companero", "ClaveDificil123")
        ]
        cursor.executemany("INSERT INTO credenciales (usuario, password) VALUES (?, ?)", integrantes)
        conexion.commit()
        print("[+] Integrantes de la evaluación cargados exitosamente en la base de datos.")
    conexion.close()

# 2. Primera fase del contenido web de la ruta raíz
@app.route('/', methods=['GET'])
def index():
    return "Servidor Flask operativo", 200

# 3. Almacenar nombres y contraseñas en texto plano y verificar nuevas credenciales
@app.route('/registro', methods=['POST'])
def registrar_usuario():
    if request.is_json:
        parametros = request.get_json()
    else:
        parametros = request.form
        
    usuario = parametros.get("usuario")
    password = parametros.get("password")
    
    if not usuario or not password:
        return jsonify({"status": "Error", "message": "Faltan parámetros obligatorios"}), 400
        
    try:
        conexion = sqlite3.connect(DB_FILE)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO credenciales (usuario, password) VALUES (?, ?)", (usuario, password))
        conexion.commit()
        conexion.close()
        return jsonify({"status": "Exito", "message": f"Usuario '{usuario}' registrado en texto plano"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "Error", "message": "El nombre de usuario ya existe"}), 400

# 4. En cada intento de sesión leer los parámetros HTTP y verificar la cuenta
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    if request.is_json:
        parametros = request.get_json()
    else:
        parametros = request.form
        
    usuario = parametros.get("usuario")
    password = parametros.get("password")
    
    if not usuario or not password:
        return jsonify({"status": "Error", "message": "Campos incompletos"}), 400
        
    conexion = sqlite3.connect(DB_FILE)
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM credenciales WHERE usuario = ? AND password = ?", (usuario, password))
    user_record = cursor.fetchone()
    conexion.close()
    
    if user_record:
        return jsonify({"status": "Autenticado", "message": f"Acceso Concedido a {usuario}"}), 200
    else:
        return jsonify({"status": "Rechazado", "message": "Fallo de autenticación"}), 401

# 5. El sitio web utilizará el puerto 5000
if __name__ == '__main__':
    init_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
