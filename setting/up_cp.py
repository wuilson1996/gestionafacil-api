import xmlschema
import xmltodict
import json
import pandas as pd
from .models import *

def up_cp():
    # Ruta al archivo XSD
    xsd_file = "C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/test/datos.xsd"

    # Carga el archivo XSD
    schema = xmlschema.XMLSchema(xsd_file)

    print(schema)

    print("Enumerations en el esquema XSD:")
    print("-----------------------------------")
    data_dict = {}
    for type_name, type_obj in schema.types.items():
        data_dict[type_name] = []
        if "c_ClaveProdServ" == type_name:
            print("Tipo:", type_name)
            if hasattr(type_obj, 'enumeration'):
                print("Enumerations: "+str(len(type_obj.enumeration)))
                for enum in type_obj.enumeration:
                    print("-", enum)
                    #data_dict[type_name].append(enum)
                    o = ClaveProdServ.objects.filter(code=enum).first()
                    if not o:
                        ClaveProdServ.objects.create(code=enum)
                    #else:
                    #    cp.code = enum
                    #    cp.save()
            else:
                print("No tiene enumerations.")
            print("--------------------------")

def up_cp_excel():
    archivo = 'codigo_postal_mx.xls'

    sheet_names = [
        'Aguascalientes', 
        'Baja_California',
        'Baja_California_Sur',
        'Campeche',
        'Coahuila_de_Zaragoza',
        'Colima',
        'Chiapas',
        'Chihuahua',
        'Distrito_Federal',
        'Durango',
        'Guanajuato',
        'Guerrero',
        'Hidalgo',
        'Jalisco',
        'México',
        'Michoacán_de_Ocampo',
        'Morelos',
        'Nayarit',
        'Nuevo_León',
        'Oaxaca',
        'Puebla',
        'Querétaro',
        'Quintana_Roo',
        'San_Luis_Potosí',
        'Sinaloa',
        'Sonora',
        'Tabasco',
        'Tamaulipas',
        'Tlaxcala',
        'Veracruz_de_Ignacio_de_la_Llave',
        'Yucatán',
        'Zacatecas'
    ]
    for s in sheet_names:
        df = pd.read_excel(archivo, sheet_name=s)
        _state_text = s.replace("_", " ")
        if _state_text == "Distrito Federal":
            _state_text = "Ciudad de México"
        #print(_state_text)
        _state = State.objects.filter(name = _state_text).first()
        if not _state:
            _state = State.objects.create(name = _state_text)
        for i in range(len(df)):
            _m = Municipalities.objects.filter(name = df.iloc[i]['D_mnpio']).first()
            if not _m:
                _m = Municipalities.objects.create(name = df.iloc[i]['D_mnpio'], state = _state)
            #if (df.iloc[i]['d_estado'] == _state_text) == False:
            print(df.iloc[i]['d_codigo']," | ", df.iloc[i]['d_estado'] ," | ", (df.iloc[i]['d_estado'] == _state_text)," | ", df.iloc[i]['D_mnpio'] ," | ", df.iloc[i]['d_asenta'])

            code_postal = PostalCode.objects.filter(code = df.iloc[i]['d_codigo']).first()
            if not code_postal:
                code_postal = PostalCode.objects.create(
                    code = df.iloc[i]['d_codigo'],
                    municipality = _m
                )
            
            colonia = Colonia.objects.filter(name = df.iloc[i]['d_asenta'], postal_code = code_postal).first()
            if not colonia:
                colonia = Colonia.objects.create(
                    name = df.iloc[i]['d_asenta'],
                    postal_code = code_postal
                )

def up_code_prod():
    with open("clave_prod.json") as file:
        data = json.loads(file)
    
        print(data)

def download_prod_service():
    url = "https://raw.githubusercontent.com/bambucode/catalogos_sat_JSON/master/c_ClaveProdServ.json"
    data = []
    with requests.get(url) as r:
        data = json.loads(r.content)
        #with open("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/c_ClaveProdServ.json", "wb") as f:
        #    f.write(r.content)

    for d in data:
        #print(d)
        ClaveProdServ.objects.create(
            code = d["id"],
            name = d["descripcion"],
            palabrasSimilares = d["palabrasSimilares"],
            estimuloFranjaFronteriza = d["estimuloFranjaFronteriza"],
            fechaFinVigencia = d["fechaFinVigencia"],
            fechaInicioVigencia = d["fechaInicioVigencia"],
            complementoQueDebeIncluir = d["complementoQueDebeIncluir"],
            incluirIEPSTrasladado = d["incluirIEPSTrasladado"],
            incluirIVATrasladado = d["incluirIVATrasladado"],
        )