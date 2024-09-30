import xmlschema
import xmltodict
import json

# Ruta al archivo XSD
xsd_file = "C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/test/datos.xsd"

# Carga el archivo XSD
schema = xmlschema.XMLSchema(xsd_file)

print(schema)

# Imprime la información del esquema XSD
#print("Información del esquema XSD:")
#print("-----------------------------")
#print("Elementos tope:", schema.root_elements)
#print("Tipos definidos:", schema.types)
# Recorre cada tipo definido

#print("Elementos definidos:", schema.elements)
#print("Atributos definidos:", schema.attributes)

# Convierte el XSD a un diccionario
#xsd_dict = xmltodict.parse(str(schema))

# Convierte el diccionario a JSON
#json_data = json.dumps(xsd_dict, indent=4)

# Guarda el JSON en un archivo o imprímelo
#with open("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/test/datos.json", "w") as json_file:
#    json_file.write(json_data)

#print("Archivo JSON generado exitosamente.")

#print("Tipos definidos en el esquema XSD:")
#print("-----------------------------------")
#for type_name, type_obj in schema.types.items():
#    print("Nombre:", type_name)
#    print("Tipo:", type_obj)
#    print("--------------------------")

print("Enumerations en el esquema XSD:")
print("-----------------------------------")
data_dict = {}
for type_name, type_obj in schema.types.items():
    data_dict[type_name] = []
    if "c_CodigoPostal" == type_name:
        print("Tipo:", type_name)
        if hasattr(type_obj, 'enumeration'):
            print("Enumerations: "+str(len(type_obj.enumeration)))
            for enum in type_obj.enumeration:
                #print("-", enum)
                data_dict[type_name].append(enum)
        else:
            print("No tiene enumerations.")
        print("--------------------------")

#print(data_dict)

# Convierte el diccionario a JSON
#json_data = json.dumps(data_dict, indent=4)

# Guarda el JSON en un archivo o imprímelo
#with open("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/test/datos.json", "w") as json_file:
#    json_file.write(json_data)