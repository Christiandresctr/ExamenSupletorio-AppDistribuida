import redis
import json
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')

class Cache:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST, 
            port=6379, 
            decode_responses=True
        )

    def get(self, clave):
        """Obtiene un valor del cache"""
        valor = self.client.get(clave)
        if valor:
            return json.loads(valor)
        return None
    
    def set(self, clave, valor, expira_en=60):
        """Guarda un valor en el cache con una expiración"""
        self.client.setex(
            clave, 
            expira_en, 
            json.dumps(valor)
        )

        def delete(self, clave):
            """Elimina un valor del cache"""
            return self.client.delete(clave)
        
        def existe(self, clave):
            """Verifica si una clave existe en el cache"""
            return bool(self.client.exists(clave))
        
# Instancia Global
cache = Cache()

