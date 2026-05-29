#!/bin/bash
# Limpieza de ejecuciones anteriores
docker stop samplerunning 2>/dev/null
docker rm samplerunning 2>/dev/null

# Construcción de la imagen local basada en Python
docker build -t sample-app .

# Despliegue redirigiendo el tráfico del host (9999) al puerto interno de Flask (5050)
docker run -d -p 9999:5050 --name samplerunning sample-app
