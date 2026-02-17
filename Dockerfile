# Imagen base de python
FROM python:3.11-slim

# Instalamos netcat (necesario para el script de espera)
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el codigo de la aplicacion
COPY . .

# Damos permisos al script
RUN chmod +x app/wait-for-it.sh

#Exponer el puerto
EXPOSE 5000

#Comando para ejecutar la app
CMD [ "python", "app/app.py" ]
