from flask import Flask, jsonify, request
import time
import os
from cache import cache
from mensajeria import mensajeria

app = Flask(__name__)

# ============================================
# SIMULACIÓN DE BASE DE DATOS
# ============================================
def consulta_costosa(producto_id):
    time.sleep(3)
    return {
        "id": producto_id,
        "nombre": f"Producto {producto_id}",
        "precio": 99.99,
        "stock": 100
    }

# ============================================
# INICIO
# ============================================
@app.route('/')
def home():
    return jsonify({
        "mensaje": "API con Cache y Mensajeria",
        "servicios": {
            "cache": "Redis ✓",
            "mensajeria": "RabbitMQ ✓"
        },
        "endpoints": {
            "GET  /producto/<id>": "Obtiene producto con cache",
            "GET  /sin-cache/<id>": "Obtiene producto sin cache",
            "GET  /cache/limpiar": "Limpia el cache",
            "POST /pedido": "Crea pedido y envia a cola RabbitMQ",
            "GET  /pedido/<id>": "Consulta estado del pedido"
        }
    })

# ============================================
# ENDPOINTS DE PRODUCTOS (con cache)
# ============================================
@app.route('/producto/<int:producto_id>')
def get_producto_con_cache(producto_id):
    clave = f"producto:{producto_id}"

    resultado = cache.get(clave)

    if resultado:
        resultado['fuente'] = 'CACHE'
        return jsonify(resultado)

    resultado = consulta_costosa(producto_id)
    cache.set(clave, resultado, expira_en=30)

    resultado['fuente'] = 'BASE DE DATOS'
    return jsonify(resultado)

@app.route('/sin-cache/<int:producto_id>')
def get_producto_sin_cache(producto_id):
    resultado = consulta_costosa(producto_id)
    resultado['fuente'] = 'BASE DE DATOS (sin cache)'
    return jsonify(resultado)

@app.route('/cache/limpiar', methods=['GET', 'DELETE'])
def limpiar_cache():
    cache.delete('producto:1')
    cache.delete('producto:2')
    return jsonify({"mensaje": "Cache limpiado para productos 1 y 2"})

# ============================================
# ENDPOINTS DE PEDIDOS (con RabbitMQ)
# ============================================
@app.route('/pedido', methods=['POST'])
def crear_pedido():
    datos = request.get_json()

    # Validación básica
    if not datos or 'producto_id' not in datos:
        return jsonify({
            "error": "Debes enviar producto_id"
        }), 400

    # Construye el pedido
    pedido = {
        "id": f"PED-{int(time.time())}",
        "producto_id": datos['producto_id'],
        "cantidad": datos.get('cantidad', 1),
        "estado": "pendiente"
    }

    # 1. Guarda en cache por 5 minutos
    cache.set(f"pedido:{pedido['id']}", pedido, expira_en=300)

    # 2. Envía a RabbitMQ para procesamiento en background
    mensajeria.enviar_mensaje('pedidos', pedido)

    return jsonify({
        "mensaje": "Pedido creado y enviado a procesar",
        "pedido": pedido
    }), 201

@app.route('/pedido/<pedido_id>')
def get_pedido(pedido_id):
    pedido = cache.get(f"pedido:{pedido_id}")

    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404

    return jsonify(pedido)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)