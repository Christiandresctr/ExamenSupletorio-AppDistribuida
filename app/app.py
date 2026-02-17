from flask import Flask, jsonify, request
import time
import os
from cache import cache
from mensajeria import mensajeria
from database import db

app = Flask(__name__)

# Inicializar las tablas al arrancar
try:
    db.inicializar_tablas()
    print(" [✓] Base de datos inicializada")
except Exception as e:
    print(f" [!] Error inicializando DB: {e}")

# ============================================
# INICIO
# ============================================
@app.route('/')
def home():
    return jsonify({
        "mensaje": "API COMPLETA funcionando",
        "servicios": {
            "cache": "Redis ✓",
            "mensajeria": "RabbitMQ ✓",
            "base_de_datos": "PostgreSQL ✓"
        },
        "endpoints": {
            "POST /producto": "Crear producto en DB",
            "GET  /producto/<id>": "Obtener producto (con cache)",
            "GET  /productos": "Listar todos los productos",
            "POST /pedido": "Crear pedido (DB + RabbitMQ)",
            "GET  /pedido/<id>": "Consultar pedido"
        }
    })

# ============================================
# ENDPOINTS DE PRODUCTOS
# ============================================
@app.route('/producto', methods=['POST'])
def crear_producto():
    datos = request.get_json()
    
    if not datos or 'nombre' not in datos or 'precio' not in datos:
        return jsonify({"error": "Faltan datos: nombre, precio, stock"}), 400
    
    producto_id = db.insertar_producto(
        datos['nombre'],
        datos['precio'],
        datos.get('stock', 0)
    )
    
    return jsonify({
        "mensaje": "Producto creado",
        "id": producto_id
    }), 201

@app.route('/producto/<int:producto_id>')
def get_producto(producto_id):
    clave = f"producto:{producto_id}"
    
    # 1. Buscar en caché primero
    resultado = cache.get(clave)
    
    if resultado:
        resultado['fuente'] = '🟢 CACHE'
        return jsonify(resultado)
    
    # 2. Si no está en caché, consultar DB
    resultado = db.obtener_producto(producto_id)
    
    if not resultado:
        return jsonify({"error": "Producto no encontrado"}), 404
    
    # Convertir Decimal a float para JSON
    resultado['precio'] = float(resultado['precio'])
    resultado['created_at'] = str(resultado['created_at'])
    
    # 3. Guardar en caché por 60 segundos
    cache.set(clave, resultado, expira_en=60)
    
    resultado['fuente'] = '🔴 BASE DE DATOS'
    return jsonify(resultado)

@app.route('/productos')
def listar_productos():
    productos = db.listar_productos()
    
    # Convertir tipos para JSON
    for p in productos:
        p['precio'] = float(p['precio'])
        p['created_at'] = str(p['created_at'])
    
    return jsonify(productos)

# ============================================
# ENDPOINTS DE PEDIDOS
# ============================================
@app.route('/pedido', methods=['POST'])
def crear_pedido():
    datos = request.get_json()
    
    if not datos or 'producto_id' not in datos:
        return jsonify({"error": "Debes enviar producto_id"}), 400
    
    # Verifica que el producto existe
    producto = db.obtener_producto(datos['producto_id'])
    if not producto:
        return jsonify({"error": "Producto no existe"}), 404
    
    # Construye el pedido
    pedido = {
        "id": f"PED-{int(time.time())}",
        "producto_id": datos['producto_id'],
        "cantidad": datos.get('cantidad', 1),
        "estado": "pendiente"
    }
    
    # 1. Guarda en PostgreSQL
    db.insertar_pedido(
        pedido['id'],
        pedido['producto_id'],
        pedido['cantidad'],
        pedido['estado']
    )
    
    # 2. Guarda en caché por 5 minutos
    cache.set(f"pedido:{pedido['id']}", pedido, expira_en=300)
    
    # 3. Envía a RabbitMQ para procesamiento
    mensajeria.enviar_mensaje('pedidos', pedido)
    
    return jsonify({
        "mensaje": "Pedido creado exitosamente",
        "pedido": pedido
    }), 201

@app.route('/pedido/<pedido_id>')
def get_pedido(pedido_id):
    # Primero busca en caché
    pedido = cache.get(f"pedido:{pedido_id}")
    
    if pedido:
        pedido['fuente'] = 'CACHE'
        return jsonify(pedido)
    
    # Si no está en caché, busca en DB
    pedido = db.obtener_pedido(pedido_id)
    
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    
    pedido['created_at'] = str(pedido['created_at'])
    pedido['fuente'] = 'BASE DE DATOS'
    
    return jsonify(pedido)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)