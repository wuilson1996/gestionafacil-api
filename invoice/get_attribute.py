import xmlschema
import xmltodict
def get_att(xsd_file):
    # Parsear el XML desde el archivo
    with open(xsd_file, "r", encoding="utf-8") as xml_file:
        xml_str = xml_file.read()
    
    xml_dict = xmltodict.parse(xml_str.replace("&#241;", "ñ"))

    return xml_dict

if __name__ == "__main__":
    data = get_att("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/media/timbres/XIQB891116QE4TS87.xml")
    print(data)