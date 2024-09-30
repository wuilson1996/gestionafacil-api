#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import base64
import xml.etree.ElementTree as ET
from datetime import datetime
#from M2Crypto.RSA import load_key_string

class CrearCadena33:
    def creacionXML(self):
        certificado_file = 'C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/cert/CSD_Sucursal_1_IIA040805DZ4_20230518_062510.cer'
        with open(certificado_file, 'rb') as f:
            certificado_pem = base64.b64encode(f.read()).decode('utf-8')

        serial = os.popen('openssl x509 -inform DER -in '+ certificado_file + ' -noout -serial').read()
        no_certificado = serial[::2][4:]

        ET.register_namespace('cfdi', "http://www.sat.gob.mx/cfd/4")
        ET.register_namespace('cartaporte20', "http://www.sat.gob.mx/CartaPorte20")
        namespace = {'xmlns:cartaporte20': 'http://www.sat.gob.mx/CartaPorte20',
                     'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                     'xsi:schemaLocation': 'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte20 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xsd'}

        Comprobante = ET.Element("{http://www.sat.gob.mx/cfd/4}Comprobante", namespace,
                                  Version="4.0",
                                  Folio="167ABC",
                                  Fecha=datetime.now().replace(microsecond=0).isoformat('T'),
                                  SubTotal="1000.00",
                                  Sello="",
                                  NoCertificado=no_certificado,
                                  Certificado=certificado_pem,
                                  Total="1120.00",
                                  Moneda="USD",
                                  TipoCambio="20.366",
                                  TipoDeComprobante="I",
                                  LugarExpedicion="58000",
                                  CondicionesDePago="CONDICIONES",
                                  FormaPago="99",
                                  Serie="A",
                                  MetodoPago="PPD",
                                  Exportacion="01"
                                  )

        Emisor = ET.SubElement(Comprobante, 'cfdi:Emisor',
                               Rfc="EKU9003173C9",
                               Nombre="ESCUELA KEMPER URGATE",
                               RegimenFiscal="601")
        Receptor = ET.SubElement(Comprobante, 'cfdi:Receptor',
                                 Rfc="ICV060329BY0",
                                 Nombre="INMOBILIARIA",
                                 UsoCFDI="G03",
                                 RegimenFiscalReceptor="601",
                                 DomicilioFiscalReceptor="33826"
                                 )
        Conceptos = ET.SubElement(Comprobante, 'cfdi:Conceptos')
        Concepto = ET.SubElement(Conceptos, 'cfdi:Concepto',
                                 Cantidad="1.00",
                                 ClaveProdServ="78101802",
                                 ClaveUnidad="E48",
                                 Descripcion="servicios de transporte",
                                 Importe="1000.00",
                                 Unidad="Servicio",
                                 ValorUnitario="1000.00",
                                 ObjetoImp="02")

        Impuestos = ET.SubElement(Concepto, 'cfdi:Impuestos')
        Traslados = ET.SubElement(Impuestos, 'cfdi:Traslados')
        Traslado = ET.SubElement(Traslados, 'cfdi:Traslado',
                                  Base="1000.00",
                                  Importe="160.00",
                                  Impuesto="002",
                                  TasaOCuota="0.160000",
                                  TipoFactor="Tasa")
        Retenciones = ET.SubElement(Impuestos, 'cfdi:Retenciones')
        Retencion = ET.SubElement(Retenciones, 'cfdi:Retencion',
                                  Base="1000.00",
                                  Importe="40.00",
                                  Impuesto="002",
                                  TasaOCuota="0.040000",
                                  TipoFactor="Tasa")

        Impuestos = ET.SubElement(Comprobante, 'cfdi:Impuestos',
                                  TotalImpuestosRetenidos="40.00",
                                  TotalImpuestosTrasladados="160.00")
        Retenciones = ET.SubElement(Impuestos, 'cfdi:Retenciones')
        Retencion = ET.SubElement(Retenciones, 'cfdi:Retencion',
                                  Importe="40.00",
                                  Impuesto="002")
        Traslados = ET.SubElement(Impuestos, 'cfdi:Traslados')
        Traslado = ET.SubElement(Traslados, 'cfdi:Traslado',
                                 Importe="160.00",
                                 Base="1000.00",
                                 Impuesto="002",
                                 TasaOCuota="0.160000",
                                 TipoFactor="Tasa")

        Complemento = ET.SubElement(Comprobante, 'cfdi:Complemento')
        Cartaporte = ET.SubElement(Complemento, 'cartaporte20:CartaPorte',
                                   Version="2.0",
                                   TranspInternac="No",
                                   TotalDistRec="100.00"
                                   )

        ubicaciones = ET.SubElement(Cartaporte, 'cartaporte20:Ubicaciones')
        ubicacion1 = ET.SubElement(ubicaciones, 'cartaporte20:Ubicacion',
                                   TipoUbicacion="Origen",
                                   FechaHoraSalidaLlegada="2022-09-22T12:00:00"
                                   )

        Domicilio = ET.SubElement(ubicacion1, 'cartaporte20:Domicilio',
                                  Calle="Calle",
                                  NumeroExterior="2",
                                  Colonia="0162",
                                  Localidad="20",
                                  Municipio="106",
                                  Estado="MEX",
                                  Pais="MEX",
                                  CodigoPostal="50009"
                                  )

        ubicacion2 = ET.SubElement(ubicaciones, 'cartaporte20:Ubicacion',
                                   TipoUbicacion="Destino",
                                   FechaHoraSalidaLlegada="2022-09-26T12:00:00",
                                   DistanciaRecorrida="100"
                                   )
        Domicilio2 = ET.SubElement(ubicacion2, 'cartaporte20:Domicilio',
                                   Calle="Calle",
                                   NumeroExterior="34",
                                   Colonia="0196",
                                   Localidad="06",
                                   Municipio="053",
                                   Estado="MIC",
                                   Pais="MEX",
                                   CodigoPostal="58160"
                                   )

        Mercancias = ET.SubElement(Cartaporte, 'cartaporte20:Mercancias',
                                   PesoBrutoTotal="18000.00",
                                   UnidadPeso="KGM",
                                   NumTotalMercancias="1"
                                   )
        Mercancia = ET.SubElement(Mercancias, 'cartaporte20:Mercancia',
                                  BienesTransp="11131504",
                                  Descripcion="Cueros",
                                  Cantidad="18",
                                  ClaveUnidad="H87",
                                  PesoEnKg="18000.00",
                                  ValorMercancia="9850.00",
                                  Moneda="MXN"
                                  )

        AutoTransporte = ET.SubElement(Mercancias, 'cartaporte20:Autotransporte',
                                       PermSCT="TPAF03",
                                       NumPermisoSCT="PER123456987"
                                       )

        IdentificacionVehicular = ET.SubElement(AutoTransporte, 'cartaporte20:IdentificacionVehicular',
                                                ConfigVehicular="VL",
                                                PlacaVM="ABC3215",
                                                AnioModeloVM="2008"
                                                )

        Seguros = ET.SubElement(AutoTransporte, 'cartaporte20:Seguros',
                                AseguraRespCivil="AAA-34B",
                                PolizaRespCivil="ACD-H23"
                                )
        Remolques = ET.SubElement(AutoTransporte, 'cartaporte20:Remolques')
        Remolque = ET.SubElement(Remolques, 'cartaporte20:Remolque',
                                 SubTipoRem="CTR005",
                                 Placa="YYY1234"
                                 )

        FiguraTransporte = ET.SubElement(Cartaporte, 'cartaporte20:FiguraTransporte')
        TiposFigura = ET.SubElement(FiguraTransporte, 'cartaporte20:TiposFigura',
                                    TipoFigura="01",
                                    RFCFigura="XIQB891116QE4",
                                    NumLicencia="123456"
                                    )

        tree = ET.ElementTree(Comprobante)
        tree.write('cartaporte.xml', encoding='utf-8', xml_declaration=True)

    def __init__(self):
        self.now = datetime.now().replace(microsecond=0).isoformat('T')

        self.xml_string = open('C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/test/cartaporte.xml').read()

        xml_etree = ET.ElementTree(ET.fromstring(self.xml_string))
        self.xml_string = self.xml_string.replace('xsi', 'xmlns:xsi')
        self.xml_string = self.xml_string.replace('schemaLocation', 'xsi:schemaLocation')

        cadena_original = self.cadena_original(self.xml_string)
        sello = self.sello33(cadena_original)
        xml_etree.getroot().set('Sello', sello)
        xml_etree.write('cartaporte_signed.xml', encoding='UTF-8', xml_declaration=True)

    def cadena_original(self, xml_string):
        original_string = ET.tostring(ET.fromstring(xml_string), encoding='utf-8').decode('utf-8')
        return original_string

    def sello33(self, cadena_original):
        os.system('openssl pkcs8 -inform DER -in llave.key -passin pass:12345678a -out llavePem.pem')
        with open('llavePem.pem', 'rb') as f:
            key_pem = f.read()

        rsa = load_key_string(key_pem)
        assert len(rsa) in (1024, 2048)
        assert rsa.e == b'\x00\x00\x00\x03\x01\x00\x01'

        md5_digest = hashlib.sha256(cadena_original.encode('utf-8')).digest()
        rsa_signature = rsa.sign(md5_digest, 'sha256')
        signature = base64.b64encode(rsa_signature)
        return signature.decode('utf-8')

if __name__ == "__main__":
    crear_cadena = CrearCadena33()
    crear_cadena.creacionXML()
