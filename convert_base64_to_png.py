import base64

def imagen_a_base64(nombre_archivo):
    with open(nombre_archivo, "rb") as imagen:
        imagen_base64 = base64.b64encode(imagen.read()).decode('utf-8')
    return imagen_base64

def save_base64_as_png(base64_string, nombre_archivo):
    try:
        # Decodificar la cadena base64
        imagen_decodificada = base64.b64decode(base64_string)

        # Escribir la imagen decodificada en un archivo
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(imagen_decodificada)
        
        print("Imagen guardada correctamente como", nombre_archivo)
    except Exception as e:
        print("Error al guardar la imagen:", e)

# # Ejemplo de uso
# nombre_archivo_guardado = "imagen_guardada.png"

# # Convertir la imagen a base64
# nombre_archivo_imagen = r"C:\Users\Desarrollo2\Desktop\124563021_1.jpeg"
# imagen_base64 = imagen_a_base64(nombre_archivo_imagen)
# print(imagen_base64)

# # Guardar la imagen base64 como archivo PNG
# guardar_base64_como_png(imagen_base64, nombre_archivo_guardado)
