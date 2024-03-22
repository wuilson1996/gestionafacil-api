def zip_to_binary(file_path):
    with open(file_path, 'rb') as file:
        binary_data = file.read()
    return binary_data

# Ejemplo de uso:
archivo_zip = 'C:/Users/Desarrollo2/Pictures/convertidor/Motos/Nueva_carpeta/api_new_invoice/media/file_archive_5ee73cdb3b0c43a097d4c318b4b36eba.zip'
datos_binarios = zip_to_binary(archivo_zip)
print(datos_binarios)
def guardar_datos_binarios(datos_binarios, nombre_archivo):
    with open(nombre_archivo, 'wb') as archivo:
        archivo.write(datos_binarios)

# Guardar los datos binarios en un archivo ZIP
nombre_archivo_zip = 'archivo.zip'
guardar_datos_binarios(datos_binarios, nombre_archivo_zip)