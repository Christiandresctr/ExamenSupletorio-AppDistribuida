# Examen Supletorio - Programación

## Autor
Christian Maisincho

## Descripción
API RESTful con arquitectura de microservicios que integra:
- Cache en memoria (Redis)
- Sistema de mensajería (RabbitMQ)
- Base de datos relacional (PostgreSQL)
- Procesamiento asíncrono con workers
- Despliegue automatizado con Terraform en AWS

## Tecnologías
- **Lenguaje**: Python 3.11
- **Framework**: Flask
- **Containerización**: Docker + Docker Compose
- **Caché**: Redis
- **Mensajería**: RabbitMQ
- **Base de datos**: PostgreSQL
- **IaC**: Terraform
- **Cloud**: AWS (EC2, VPC, Security Groups)

## Arquitectura
```
Cliente → Flask API → Redis (caché)
                   ↓
                   PostgreSQL (persistencia)
                   ↓
                   RabbitMQ (cola) → Worker (procesamiento)
```

## Instalación Local
```bash
# Clonar repositorio
git clone https://github.com/TU-USUARIO/examen-supletorio.git
cd examen-supletorio

# Levantar servicios
docker-compose up -d

# Verificar
curl http://localhost:5000/
```

## Despliegue en AWS
```bash
cd terraform
terraform init
terraform plan
terraform apply

# Obtener IP pública del output
# Conectarse por SSH y ejecutar docker-compose
```

## Endpoints

### Productos
- `POST /producto` - Crear producto
- `GET /producto/<id>` - Obtener producto (con caché)
- `GET /productos` - Listar todos

### Pedidos
- `POST /pedido` - Crear pedido (guarda en DB y envía a cola)
- `GET /pedido/<id>` - Consultar estado

## Flujo de un Pedido

1. Cliente crea pedido vía API
2. API guarda en PostgreSQL
3. API guarda en Redis (caché 5 min)
4. API envía mensaje a RabbitMQ
5. Worker procesa mensaje de forma asíncrona
6. Worker actualiza estado en DB y caché

## Limpieza
```bash
# Destruir infraestructura AWS
terraform destroy
```

## Estructura del Proyecto
```
examen-supletorio/
├── app/
│   ├── app.py           # API principal
│   ├── cache.py         # Lógica Redis
│   ├── mensajeria.py    # Lógica RabbitMQ
│   ├── database.py      # Lógica PostgreSQL
│   ├── worker.py        # Consumidor de mensajes
│   ├── Dockerfile
│   └── requirements.txt
├── terraform/
│   └── main.tf          # Infraestructura como código
├── docker-compose.yml
└── README.md
```