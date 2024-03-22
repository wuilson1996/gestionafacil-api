import base64
import json

def convertir_a_base64(archivo_ruta):
    with open(archivo_ruta, "rb") as archivo:
        contenido_base64 = base64.b64encode(archivo.read()).decode("utf-8")
    return contenido_base64
archivo_ruta = "views.py"
print(convertir_a_base64(archivo_ruta))
