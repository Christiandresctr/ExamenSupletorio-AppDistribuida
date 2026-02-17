import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = 'miapp'
DB_USER = 'admin'
DB_PASS = 'admin123'

class Database:
    def __init__(self):
        self.host = DB_HOST
        self.database = DB_NAME
        self.user = DB_USER
        self.password = DB_PASS
    
    def conectar(self):
        """Crea una conexión a PostgreSQL"""
        return psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )
    
    def inicializar_tablas(self):
        """Crea las tablas si no existen"""
        conn = self.conectar()
        cur = conn.cursor()
        
        # Tabla de productos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de pedidos
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id VARCHAR(50) PRIMARY KEY,
                producto_id INTEGER REFERENCES productos(id),
                cantidad INTEGER NOT NULL,
                estado VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print(" [✓] Tablas creadas exitosamente")
    
    def insertar_producto(self, nombre, precio, stock):
        """Inserta un nuevo producto"""
        conn = self.conectar()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s) RETURNING id",
            (nombre, precio, stock)
        )
        
        producto_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return producto_id
    
    def obtener_producto(self, producto_id):
        """Obtiene un producto por ID"""
        conn = self.conectar()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT * FROM productos WHERE id = %s",
            (producto_id,)
        )
        
        producto = cur.fetchone()
        cur.close()
        conn.close()
        
        return dict(producto) if producto else None
    
    def listar_productos(self):
        """Lista todos los productos"""
        conn = self.conectar()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM productos ORDER BY id")
        productos = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return [dict(p) for p in productos]
    
    def insertar_pedido(self, pedido_id, producto_id, cantidad, estado):
        """Inserta un nuevo pedido"""
        conn = self.conectar()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO pedidos (id, producto_id, cantidad, estado) VALUES (%s, %s, %s, %s)",
            (pedido_id, producto_id, cantidad, estado)
        )
        
        conn.commit()
        cur.close()
        conn.close()
    
    def obtener_pedido(self, pedido_id):
        """Obtiene un pedido por ID"""
        conn = self.conectar()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(
            "SELECT * FROM pedidos WHERE id = %s",
            (pedido_id,)
        )
        
        pedido = cur.fetchone()
        cur.close()
        conn.close()
        
        return dict(pedido) if pedido else None
    
    def actualizar_estado_pedido(self, pedido_id, estado):
        """Actualiza el estado de un pedido"""
        conn = self.conectar()
        cur = conn.cursor()
        
        cur.execute(
            "UPDATE pedidos SET estado = %s WHERE id = %s",
            (estado, pedido_id)
        )
        
        conn.commit()
        cur.close()
        conn.close()

# Instancia global
db = Database()