from lxml import etree
from datetime import datetime
from lxml import etree
from lxml import etree as ET
from datetime import datetime
import os
import hashlib
import base64
import uuid
import base64
import hashlib
import xml.etree.ElementTree as ET
import sys
import importlib
#from M2Crypto.RSA import load_key_string
importlib.reload(sys)

class crear_cadena40(object):

    def __init__(self, invoice_name):
        #breakpoint
        self.path = "C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/documents/"
        self.invoice_name = invoice_name
        archivo = self.creacionXML()
        self.now = datetime.now().replace(microsecond=0).isoformat('T')
        self.XSLT_STYLE = etree.parse("C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/integrador/cfdi/v40/cadenaoriginal.xslt")
        self.xml_string = open(self.path+self.invoice_name+'.xml', 'rb').read()
        xml_etree = etree.fromstring(self.xml_string)
        self.cadena_original = self.obtener_cadena_original(xml_etree)
        #self.sello = self.obtener_sello(self.cadena_original)  # Obtener el sello
        #self.agregar_sello_al_xml(xml_etree)  # Agregar el sello al XML

    def creacionXML(self):
        """relelnar atributos del XML"""
        certificado_file = 'C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/cert/EKU9003173C9.cer'
        with open(certificado_file, 'rb') as f:
            certificado_data = f.read()
            certificado_base64 = base64.b64encode(certificado_data).decode('utf-8').replace('\n', '').replace('\r', '')

        os.system('openssl x509 -inform DER -in '+ certificado_file + ' -noout -serial > "numero.txt"')
        with open('numero.txt', 'r') as serial_file:
            serial = serial_file.read()
            no_certificado = serial[::2][4:]
 
        ET.register_namespace('cfdi', "http://www.sat.gob.mx/cfd/4")
        ET.register_namespace('cartaporte30', 'http://www.sat.gob.mx/CartaPorte30')
        namespace = {'xmlns:cartaporte30': 'http://www.sat.gob.mx/CartaPorte30', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:schemaLocation':'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte30 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd'}
        
        Comprobante = ET.Element("{http://www.sat.gob.mx/cfd/4}Comprobante", namespace,
            Version="4.0",
            Folio="167ABC",
            Fecha=datetime.now().replace(microsecond=0).isoformat('T'),
            SubTotal="1000.00",
            #Sello="",
            NoCertificado="30001000000500003416",#no_certificado,
            Certificado=certificado_base64,
            Total="1120.00" ,
            Moneda="USD",
            TipoCambio="20.366",
            TipoDeComprobante="I" ,
            LugarExpedicion="58000",
            CondicionesDePago="CONDICIONES",
            FormaPago="99",
            Serie="A",  
            MetodoPago="PPD",
            Exportacion="01"
        )

        Emisor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', 
            Rfc="EKU9003173C9" ,
            Nombre="ESCUELA KEMPER URGATE",
            RegimenFiscal="601"
        )

        Receptor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor',
            Rfc="ICV060329BY0" ,
            Nombre="INMOBILIARIA CVA"  ,
            UsoCFDI="G03",
            RegimenFiscalReceptor="601",
            DomicilioFiscalReceptor="33826"
        )
        Conceptos=ET.SubElement(Comprobante, '''cfdi:Conceptos''')
        
        Concepto = ET.SubElement(Conceptos, '''cfdi:Concepto''',
            Cantidad="1.00",
            ClaveProdServ="78101802",
            ClaveUnidad="E48",
            Descripcion="servicios de transporte",
            #Descuento="22500.00",
            Importe="1000.00",
            #NoIdentificacion="0001",
            Unidad="Servicio",
            ValorUnitario="1000.00",
            ObjetoImp="02" )
 
        #IMPUESTOS CONCEPTO
        Impuestos=ET.SubElement(Concepto, '''cfdi:Impuestos''')
        Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
        Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
            Base="1000.00",
            Importe="160.00", 
            Impuesto="002", 
            TasaOCuota="0.160000", 
            TipoFactor="Tasa")
        
        Retenciones=ET.SubElement(Impuestos, '''cfdi:Retenciones''')
        Retencion=ET.SubElement(Retenciones, '''cfdi:Retencion''',
            Base="1000.00", 
            Importe="40.00",
            Impuesto="002", 
            TasaOCuota="0.040000", 
            TipoFactor="Tasa")

        #IMPUESTOS COMPROBANTE

        Impuestos=ET.SubElement(Comprobante, '''cfdi:Impuestos''',
            TotalImpuestosRetenidos="40.00",
            TotalImpuestosTrasladados="160.00")
        Retenciones=ET.SubElement(Impuestos, '''cfdi:Retenciones''')
        Retencion=ET.SubElement(Retenciones, '''cfdi:Retencion''',
            Importe="40.00", 
            Impuesto="002")
        Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
        Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
            Importe="160.00",
            Base="1000.00", 
            Impuesto="002", 
            TasaOCuota="0.160000", 
            TipoFactor="Tasa")
 
 
        #COMPLEMENTO CARTA PORTE
        uuid_v4 = uuid.uuid4()
        custom_uuid_str = f"CCC{uuid_v4.hex[3:8].upper()}-{uuid_v4.hex[8:12].upper()}-{uuid_v4.hex[12:16].upper()}-{uuid_v4.hex[16:20].upper()}-{uuid_v4.hex[20:32].upper()}"
        Complemento=ET.SubElement(Comprobante, '''cfdi:Complemento''' )
        Cartaporte=ET.SubElement(Complemento, '''cartaporte30:CartaPorte''',
    
        Version="3.0",
        IdCCP = custom_uuid_str,
        TranspInternac="No",
        #EntradaSalidaMerc= "",
        TotalDistRec="100.00",
        #PaisOrigenDestino="",
        #ViaEntradaSalida="",

 
         )
 
        ubicaciones=ET.SubElement(Cartaporte, '''cartaporte30:Ubicaciones''')
        ubicacion1=ET.SubElement(ubicaciones, '''cartaporte30:Ubicacion''',
        TipoUbicacion="Origen",
        #IDUbicacion="",
        RFCRemitenteDestinatario="EKU9003173C9",
        #NombreRemitenteDestinatario="",
        #NumRegIdTrib="",
        #ResidenciaFiscal="",
        #NumEstacion="",
        #NombreEstacion="",
        #NavegacionTrafico="",
        FechaHoraSalidaLlegada="2022-09-22T12:00:00",
        #TipoEstacion="",
        #DistaciaRecorrida="",
 
 
        )
 
        Domicilio= ET.SubElement(ubicacion1, '''cartaporte30:Domicilio ''',
        Calle="Calle",
        NumeroExterior="2",
        #NumeroInterior="",
        Colonia="0162",
        Localidad="20",
        #Referencia="",
        Municipio="106",
        Estado="MEX",
        Pais="MEX",
        CodigoPostal="50009"
        )
 
 
 
        ubicacion2=ET.SubElement(ubicaciones, '''cartaporte30:Ubicacion''',
        TipoUbicacion="Destino",
        #IDUbicacion="",
        RFCRemitenteDestinatario="IVD920810GU2",
        #NombreRemitenteDestinatario="",
        #NumRegIdTrib="",
        #ResidenciaFiscal="",
        #NumEstacion="",
        #NombreEstacion="",
        #NavegacionTrafico="",
        FechaHoraSalidaLlegada="2022-09-26T12:00:00",
        #TipoEstacion="",
        DistanciaRecorrida="100",
 
 
        )
        Domicilio2= ET.SubElement(ubicacion2, '''cartaporte30:Domicilio ''',
        Calle="Calle",
        NumeroExterior="34",
        #NumeroInterior="",
        Colonia="0196",
        Localidad="06",
        #Referencia="",
        Municipio="053",
        Estado="MIC",
        Pais="MEX",
        CodigoPostal="58160"
        )

        Mercancias=ET.SubElement(Cartaporte, '''cartaporte30:Mercancias''',
        PesoBrutoTotal="18000.00",
        UnidadPeso="KGM",
        #PesoNetoTotal="",
        NumTotalMercancias="1",
        #CargoPorTasacion=""
        )
        Mercancia=ET.SubElement(Mercancias, '''cartaporte30:Mercancia''',
        BienesTransp="11131504",
        #ClaveSTCC="",
        Descripcion="Cueros",
        Cantidad="18",
        ClaveUnidad="H87",
        #Unidad="",
        #Dimensiones="",
        #MaterialPeligroso="",
        #CveMaterialPeligroso="",
        #Embalaje="",
        #DescripEmbalaje="",
        PesoEnKg="18000.00",
        ValorMercancia="9850.00",
        Moneda="MXN",
        #FraccionArancelaria="",
        #UIIDComercioExt=""
 
        )

        AutoTransporte=ET.SubElement(Mercancias, '''cartaporte30:Autotransporte''',
        PermSCT="TPAF03",
        NumPermisoSCT="PER123456987"
        )
 
        IdentificacionVehicular=ET.SubElement(AutoTransporte, '''cartaporte30:IdentificacionVehicular''',
        ConfigVehicular="VL",
        PlacaVM="ABC3215",
        AnioModeloVM="2008",
        PesoBrutoVehicular="0.01"
        )
 
 
        Seguros=ET.SubElement(AutoTransporte, '''cartaporte30:Seguros''',
        AseguraRespCivil="AAA-34B",
        PolizaRespCivil="ACD-H23",
 
        )
        Remolques=ET.SubElement(AutoTransporte, '''cartaporte30:Remolques''')
 
        Remolque=ET.SubElement(Remolques, '''cartaporte30:Remolque''',
        SubTipoRem="CTR005",
        Placa="YYY1234"
        )
 
 
        FiguraTransporte=ET.SubElement(Cartaporte, '''cartaporte30:FiguraTransporte''')
        TiposFigura=ET.SubElement(FiguraTransporte, '''cartaporte30:TiposFigura''',
        TipoFigura="01",
        RFCFigura="XIQB891116QE4",
        NumLicencia="123456",
        NombreFigura="Nombre",
        #NumRegidTribFigura="",
        #ResidenciaFiscalFigura=""
        )

        xml_str = ET.tostring(Comprobante, encoding='utf-8', method='xml').decode('utf-8')
        with open(self.path+self.invoice_name+'.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            archivo.close()

    def obtener_cadena_original(self, xml_etree):
        
        result = etree.XSLT(self.XSLT_STYLE)
        result = result(xml_etree)
        original_string = str(result)

        original_string = original_string.replace('<?xml version="1.0" encoding="UTF-8"?>\n', '')
        original_string = original_string.replace("\n", "")
        original_string = original_string.replace("&quot;", '"')
        original_string = original_string.replace("&lt;", "<")
        original_string = original_string.replace("&gt;", ">")
        original_string = original_string.replace("&amp;", "&")
        original_string = original_string.strip()
        print(original_string)
        self.original_string_result = original_string
        return self.original_string_result

    def obtener_sello(self, cadena_original):
        """Generar sello del XML"""
        key_file_path = '/home/ljimenez/Documents/TimbradoScript/Timbrado-Python3/certificados/EKU9003173C9/EKU9003173C9.pem'
    
    # Verificar si el archivo de clave privada existe
        if os.path.exists(key_file_path):
            key_file = open(key_file_path).read()
            key_pem = bytes(key_file, encoding='utf8')
            rsa = load_key_string(key_pem)
            assert len(rsa) in (1024, 2048)
            assert rsa.e == b'\000\000\000\003\001\000\001'
            
            cadena_original_encode = cadena_original.encode('utf-8')
            md5_digest = hashlib.sha256(cadena_original_encode).digest()
            rsa_signature = rsa.sign(md5_digest, 'sha256')
            signature = base64.b64encode(rsa_signature)
            return signature
        else:
            raise FileNotFoundError(f"Archivo de clave privada no encontrado en la ruta: {key_file_path}")


    def agregar_sello_al_xml(self, xml_etree):
        """insertar sello al XML"""
        comprobante = xml_etree
        if comprobante is None:
            print("Error: No se encontró el elemento Comprobante en el XML.")
            return
        # Agregar el sello al elemento Comprobante
        comprobante.set("Sello", self.sello.decode('utf-8'))  # Utilizar self.sello
        #print(etree.tostring(comprobante))

        xml_str = ET.tostring(comprobante, encoding='utf-8', method='xml').decode('utf-8')
        with open('CartaPorte30.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            print("XML SELLADO DE FORMA EXITOSA!!")

if __name__ == "__main__":
    instancia = crear_cadena40("invoice1")