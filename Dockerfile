# Imagen base de python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el codigo de la aplicacion
COPY . .

#Exponer el puerto
EXPOSE 5000

#Comando para ejecutar la app
CMD [ "python", "app/app.py" ]
