from flask import Flask, jsonify, request
import time
import os
from cache import cache

app = Flask(__name__)

#Simulamos una consulta "consulta costosa" que tarda 3 segundos.
def consulta_costosa(producto_id):
    time.sleep(3)  # Simula una consulta lenta
    return {
        "id": producto_id, 
        "nombre": f"Producto {producto_id}", 
        "precio": 99.99,
        "stock": 100
    }

@app.route('/')
def home():
    return jsonify({
        "mensaje": "Api con Cache usando Redis",
        "endpoints": [
            "/producto/<id> -> Con cache",
            "/sin-cache/<id> -> Sin cache",
            "/cache/limpiar -> Limpiar cache"
        ]
    })

@app.route('/producto/<int:producto_id>')
def get_producto_con_cache(producto_id):
    clave = f"producto:{producto_id}"

    # 1. Buscar en cache primero
    resultado = cache.get(clave)
    
    if resultado:
        # Cache Hit - repuesta instantanea
        resultado['fuente'] = 'CACHE'
        return jsonify(resultado)
    
    # 2. No esta en cache - consulta "costosa"
    resultado = consulta_costosa(producto_id)

    # 3. Guardar en cache por 30 segundos
    cache.set(clave, resultado, expira_en=30)

    resultado['fuente'] = 'BASE DE DATOS'
    return jsonify(resultado)

@app.route('/sin-cache/<int:producto_id>')
def get_producto_sin_cache(producto_id):
    # Siempre consulta, nunca usa cache
    resultado = consulta_costosa(producto_id)
    resultado['fuente'] = 'BASE DE DATOS (sin cache)'
    return jsonify(resultado)

@app.route('/cache/limpiar', methods=['GET','DELETE'])
def limpiar_cache():
    cache.delete('producto:1')
    cache.delete('producto:2')
    return jsonify({"mensaje": "Cache limpiado para productos 1 y 2"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)