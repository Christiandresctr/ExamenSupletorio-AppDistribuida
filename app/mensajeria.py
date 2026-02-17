import pika
import json
import os
import time

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class Mensajeria:
    def __init__(self):
        self.host = RABBITMQ_HOST
    
    def _conectar(self):
        """
        Intenta conectarse a RabbitMQ varias veces
        porque puede tardar en iniciar
        """
        intentos = 0
        while intentos < 5:
            try:
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.host,
                        credentials=pika.PlainCredentials('admin', 'admin123')
                    )
                )
                return connection
            except Exception:
                intentos += 1
                print(f"Intento {intentos}/5 de conexión a RabbitMQ...")
                time.sleep(2)
        raise Exception("No se pudo conectar a RabbitMQ")
    
    def enviar_mensaje(self, cola, mensaje):
        """
        Envía un mensaje a una cola
        cola: nombre de la cola (ej: 'pedidos')
        mensaje: diccionario con los datos
        """
        connection = self._conectar()
        channel = connection.channel()
        
        # Declara la cola, la crea si no existe
        channel.queue_declare(queue=cola, durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key=cola,
            body=json.dumps(mensaje),
            properties=pika.BasicProperties(
                delivery_mode=2  # Mensaje persistente
            )
        )
        
        print(f" [x] Enviado a cola '{cola}': {mensaje}")
        connection.close()
    
    def recibir_mensajes(self, cola, callback):
        """
        Escucha una cola y procesa mensajes con callback
        """
        connection = self._conectar()
        channel = connection.channel()
        
        channel.queue_declare(queue=cola, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=cola,
            on_message_callback=callback
        )
        
        print(f" [*] Escuchando cola '{cola}'...")
        channel.start_consuming()

# Instancia global
mensajeria = Mensajeria()