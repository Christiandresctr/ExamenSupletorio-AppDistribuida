import json
import time
import sys
import os

# Esto permite que el worker encuentre a mensajeria.py sin importar desde dónde se lance
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mensajeria import mensajeria
from cache import cache

def procesar_pedido(ch, method, properties, body):
    """
    Se ejecuta automáticamente cada vez que llega un mensaje
    ch       : canal de RabbitMQ
    method   : información de entrega
    properties: propiedades del mensaje
    body     : contenido del mensaje en bytes
    """
    # Convierte bytes a diccionario
    pedido = json.loads(body.decode())
    
    print(f"\n [>] Procesando pedido: {pedido}")
    
    # Simula trabajo real (enviar email, actualizar inventario, etc)
    time.sleep(2)

    pedido['estado'] = 'completado'
    cache.set(f"pedido:{pedido['id']}", pedido, expira_en=300)
    
    print(f" [✓] Pedido {pedido.get('id')} completado!")
    
    # MUY IMPORTANTE: Confirma que el mensaje fue procesado
    # Sin esto, RabbitMQ reencola el mensaje si el worker falla
    ch.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == '__main__':
    print(" [*] Worker iniciado, esperando pedidos...")
    mensajeria.recibir_mensajes('pedidos', procesar_pedido)