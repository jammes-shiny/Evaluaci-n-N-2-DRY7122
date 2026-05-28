#!/usr/bin/env python3
import os
import requests
import urllib.parse
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key de forma segura
key = os.getenv("GRAPHHOPPER_API_KEY")

if not key:
    print("Error: No se encontró la API Key en el archivo .env")
    exit(1)

# URLs de la API de GraphHopper
geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"

while True:
    print("\n" + "="*40)
    origen = input("Ingrese la Ciudad de Origen (o presione 'q' para salir): ")
    if origen.strip().lower() == 'q':
        print("Saliendo del programa...")
        break
        
    destino = input("Ingrese la Ciudad de Destino (o presione 'q' para salir): ")
    if destino.strip().lower() == 'q':
        print("Saliendo del programa...")
        break

    # Solicitar el rendimiento del vehículo
    while True:
        rendimiento_input = input("Ingrese el rendimiento del auto en km/l [Por defecto 12]: ").strip()
        
        # Si presiona Enter sin escribir nada, se asigna el valor por defecto
        if rendimiento_input == "":
            rendimiento_km_por_litro = 12.0
            break
        
        # Validar si es un número (int o float) válido y positivo
        try:
            rendimiento_km_por_litro = float(rendimiento_input)
            if rendimiento_km_por_litro <= 0:
                print("Error: El rendimiento debe ser un número mayor que 0.")
                continue
            break  # Salir del bucle de validación si el número es correcto
        except ValueError:
            print("Error: Ingrese un número válido (ej: 12 o 14.5).")

    # 1. Obtener coordenadas del Origen
    url_origen = geocode_url + urllib.parse.urlencode({"q": origen, "limit": "1", "key": key})
    res_origen = requests.get(url_origen)
    datos_origen = res_origen.json()

    # 2. Obtener coordenadas del Destino
    url_destino = geocode_url + urllib.parse.urlencode({"q": destino, "limit": "1", "key": key})
    res_destino = requests.get(url_destino)
    datos_destino = res_destino.json()

    # Corrección en el parseo del JSON
    try:
        if not datos_origen["hits"] or not datos_destino["hits"]:
            print("Error: No se encontraron resultados para una de las ciudades. Intente de nuevo.")
            continue
            
        lat_origen = datos_origen["hits"][0]["point"]["lat"]
        lng_origen = datos_origen["hits"][0]["point"]["lng"]
        
        lat_destino = datos_destino["hits"][0]["point"]["lat"]
        lng_destino = datos_destino["hits"][0]["point"]["lng"]
        
    except (KeyError, IndexError, TypeError):
        print("Error al procesar las coordenadas de las ciudades. Intente de nuevo.")
        continue

    # 3. Consultar la Ruta (Se corrigió la indentación para mantenerlo dentro del bloque 'while')
    parametros_ruta = {
        "point": [f"{lat_origen},{lng_origen}", f"{lat_destino},{lng_destino}"],
        "vehicle": "car",
        "locale": "es", 
        "instructions": True,   
        "calc_points": True,    
        "key": key
    }
    res_ruta = requests.get(route_url, params=parametros_ruta)
    datos_ruta = res_ruta.json()

    if "paths" in datos_ruta and len(datos_ruta["paths"]) > 0:
        path = datos_ruta["paths"][0]
        
        # Medir la distancia en kilómetros
        distancia_km = path["distance"] / 1000.0
        
        # Mostrar la duración del viaje
        tiempo_ms = path["time"]
        segundos_totales = tiempo_ms // 1000
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        
        # Calcular combustible usando la variable dinámica ingresada por el usuario
        litros_requeridos = distancia_km / rendimiento_km_por_litro

        # Resultados
        print("\n--- RESUMEN DEL VIAJE ---")
        print(f"Ruta: {origen.capitalize()} a {destino.capitalize()}")
        print(f"Distancia: {distancia_km:.2f} km")
        print(f"Duración: {horas:02d}:{minutos:02d}:{segundos:02d}")
        print(f"Rendimiento considerado: {rendimiento_km_por_litro:.1f} km/l")
        print(f"Combustible requerido: {litros_requeridos:.2f} litros")
        
        # Narrativa del viaje
        print("\n--- NARRATIVA DEL VIAJE ---")
        if "instructions" in path and path["instructions"]:
            for instruccion in path["instructions"]:
                dist_instruccion = instruccion["distance"] / 1000.0
                print(f"- {instruccion['text']} ({dist_instruccion:.2f} km)")
        else:
            print("No hay instrucciones detalladas disponibles para esta ruta.")
            
    else:
        print("No se pudo calcular una ruta entre esas ciudades.")