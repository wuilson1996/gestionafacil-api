from lxml import etree
from datetime import datetime
from lxml import etree
from lxml import etree as ET
from datetime import datetime
import datetime as dt
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

    def __init__(self, emisor, receptor, comprobante, concepto, path_cert, type_document, period=None):
        #breakpoint
        self.path = "documents/"
        self.path_cert = path_cert
        self.path_serial = "test/"
        self.invoice_name = emisor["Rfc"]+comprobante["Serie"]+comprobante["Folio"]
        self.emisor = emisor
        self.receptor = receptor
        self.comprobante = comprobante
        self.concepto = concepto
        self.type_document = type_document
        self.period = period
        #archivo = self.creacionXML()
        #self.now = datetime.now().replace(microsecond=0).isoformat('T')
        #self.XSLT_STYLE = etree.parse("integrador/cfdi/v40/cadenaoriginal.xslt")
        #self.xml_string = open(self.path+self.invoice_name+'.xml', 'rb').read()
        #xml_etree = etree.fromstring(self.xml_string)
        #self.cadena_original = self.obtener_cadena_original(xml_etree)
        #self.sello = self.obtener_sello(self.cadena_original)  # Obtener el sello
        #self.agregar_sello_al_xml(xml_etree)  # Agregar el sello al XML

    def creacionXML(self):
        """relelnar atributos del XML"""
        certificado_file = self.path_cert#+self.emisor["Rfc"]+'.cer'
        with open(certificado_file, 'rb') as f:
            certificado_data = f.read()
            certificado_base64 = base64.b64encode(certificado_data).decode('utf-8').replace('\n', '').replace('\r', '')

        os.system('openssl x509 -inform DER -in '+ certificado_file + ' -noout -serial > "'+self.path_serial+self.emisor["Rfc"]+'.txt"')
        with open(self.path_serial+self.emisor["Rfc"]+'.txt', 'r') as serial_file:
            serial = serial_file.read()
            no_certificado = serial[::2][4:]
 
        ET.register_namespace('cfdi', "http://www.sat.gob.mx/cfd/4")
        ET.register_namespace('cartaporte30', 'http://www.sat.gob.mx/CartaPorte30')
        namespace = {'xmlns:cartaporte30': 'http://www.sat.gob.mx/CartaPorte30', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:schemaLocation':'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/CartaPorte30 http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd'}
        
        Comprobante = ET.Element("{http://www.sat.gob.mx/cfd/4}Comprobante", namespace,
            Version="4.0",
            Folio=self.comprobante["Folio"],
            Fecha=self.comprobante["Fecha"],
            SubTotal=self.comprobante["SubTotal"],
            #Sello="",
            NoCertificado=no_certificado,
            Certificado=certificado_base64,
            Total=self.comprobante["Total"],
            Moneda=self.comprobante["Moneda"],
            #TipoCambio="20.366",
            TipoDeComprobante=self.comprobante["TipoDeComprobante"],
            LugarExpedicion=self.comprobante["LugarExpedicion"],
            #CondicionesDePago="CONDICIONES",
            FormaPago=self.comprobante["FormaPago"],
            Serie=self.comprobante["Serie"],  
            MetodoPago=self.comprobante["MetodoPago"],
            Exportacion=self.comprobante["Exportacion"]
        )

        if self.type_document == 5:
            InformacionGlobal = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}InformacionGlobal ', 
                Año=self.period["year"],
                Meses=self.period["month"],
                Periodicidad=self.period["period"],
            )

        Emisor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', 
            Rfc=self.emisor["Rfc"],#"EKU9003173C9" ,
            Nombre=self.emisor["Nombre"],#"ESCUELA KEMPER URGATE",
            RegimenFiscal=self.emisor["RegimenFiscal"],#"601"
        )
        
        Receptor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor',
            Rfc=self.receptor["Rfc"],#"ICV060329BY0" ,
            Nombre=self.receptor["Nombre"],#"INMOBILIARIA CVA"  ,
            UsoCFDI=self.receptor["UsoCFDI"],#"G03",
            RegimenFiscalReceptor=self.receptor["RegimenFiscalReceptor"],#"601",
            DomicilioFiscalReceptor=self.receptor["DomicilioFiscalReceptor"],#"33826"
        )
        # Concepto de productos
        Conceptos=ET.SubElement(Comprobante, '''cfdi:Conceptos''')
        for c in self.concepto:
            Concepto = ET.SubElement(Conceptos, '''cfdi:Concepto''',
                Cantidad=c["Cantidad"],#"1.00",
                ClaveProdServ=c["ClaveProdServ"],#"78101802",
                ClaveUnidad=c["ClaveUnidad"],#"E48",
                Descripcion=c["Descripcion"],#"gastos generales",
                #Descuento=c["Descuento"],#"22500.00",
                Importe=c["Importe"],#"1000.00",
                #NoIdentificacion=c["NoIdentificacion"],#"0001",
                Unidad=c["Unidad"],#"Servicio",
                ValorUnitario=c["ValorUnitario"],#"1000.00",
                ObjetoImp=c["ObjetoImp"],#"02" 
            )
    
            #IMPUESTOS CONCEPTO
            #print(c["tax"]["Traslado"])
            Impuestos=ET.SubElement(Concepto, '''cfdi:Impuestos''')
            Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
            Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
                Base=c["tax"]["Traslado"]["Base"],#"1000.00",
                Importe=c["tax"]["Traslado"]["Importe"],#"160.00", 
                Impuesto=c["tax"]["Traslado"]["Impuesto"],#"002", 
                TasaOCuota=c["tax"]["Traslado"]["TasaOCuota"],#"0.160000", 
                TipoFactor=c["tax"]["Traslado"]["TipoFactor"],#"Tasa"
            )
        
            # Retenciones=ET.SubElement(Impuestos, '''cfdi:Retenciones''')
            # Retencion=ET.SubElement(Retenciones, '''cfdi:Retencion''',
            #     Base=c["tax"]["Retencion"]["Base"],#"1000.00", 
            #     Importe=c["tax"]["Retencion"]["Importe"],#"40.00",
            #     Impuesto=c["tax"]["Retencion"]["Impuesto"],#"002", 
            #     TasaOCuota=c["tax"]["Retencion"]["TasaOCuota"],#"0.040000", 
            #     TipoFactor=c["tax"]["Retencion"]["TipoFactor"],#"Tasa"
            #)

        #IMPUESTOS COMPROBANTE
        #print(self.comprobante["tax"]["TotalImpuestosTrasladados"])
        Impuestos=ET.SubElement(Comprobante, '''cfdi:Impuestos''',
            #TotalImpuestosRetenidos=self.comprobante["tax"]["TotalImpuestosRetenidos"],#"40.00",
            TotalImpuestosTrasladados=self.comprobante["tax"]["TotalImpuestosTrasladados"]#"160.00"
        )
        # Retenciones=ET.SubElement(Impuestos, '''cfdi:Retenciones''')
        # Retencion=ET.SubElement(Retenciones, '''cfdi:Retencion''',
        #     Importe=self.comprobante["tax"]["Retencion"]["Importe"],#"40.00", 
        #     Impuesto=self.comprobante["tax"]["Retencion"]["Impuesto"]#"002"
        #)
        #print(self.comprobante["tax"]["Traslado"])
        Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
        Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
            Importe=self.comprobante["tax"]["Traslado"]["Importe"],#"160.00",
            Base=self.comprobante["tax"]["Traslado"]["Base"],#"1000.00", 
            Impuesto=self.comprobante["tax"]["Traslado"]["Impuesto"],#"002", 
            TasaOCuota=self.comprobante["tax"]["Traslado"]["TasaOCuota"],#"0.160000", 
            TipoFactor=self.comprobante["tax"]["Traslado"]["TipoFactor"],#"Tasa"
        )
 

        xml_str = ET.tostring(Comprobante, encoding='utf-8', method='xml').decode('utf-8')
        with open(self.path+self.invoice_name+'.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            archivo.close()
        
        # Generate cadena original.
        self.now = datetime.now().replace(microsecond=0).isoformat('T')
        self.XSLT_STYLE = etree.parse("integrador/cfdi/v40/cadenaoriginal.xslt")
        self.xml_string = open(self.path+self.invoice_name+'.xml', 'rb').read()
        xml_etree = etree.fromstring(self.xml_string)
        self.cadena_original = self.obtener_cadena_original(xml_etree)

        return {
            "code": 200,
            "status": "OK",
            "message": "Success",
            "cadena_original": self.cadena_original,
            "no_cert": no_certificado
        }

    def createXMLPayment(self):
        """relelnar atributos del XML"""
        certificado_file = self.path_cert#+self.emisor["Rfc"]+'.cer'
        with open(certificado_file, 'rb') as f:
            certificado_data = f.read()
            certificado_base64 = base64.b64encode(certificado_data).decode('utf-8').replace('\n', '').replace('\r', '')

        os.system('openssl x509 -inform DER -in '+ certificado_file + ' -noout -serial > "'+self.path_serial+self.emisor["Rfc"]+'.txt"')
        with open(self.path_serial+self.emisor["Rfc"]+'.txt', 'r') as serial_file:
            serial = serial_file.read()
            no_certificado = serial[::2][4:]
 
        ET.register_namespace('cfdi', "http://www.sat.gob.mx/cfd/4")
        ET.register_namespace('pago20', 'http://www.sat.gob.mx/Pagos20')
        namespace = {
            'xmlns:pago20': 'http://www.sat.gob.mx/Pagos20', 
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 
            'xsi:schemaLocation':'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd http://www.sat.gob.mx/Pagos20 http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos20.xsd'
        }
        
        Comprobante = ET.Element("{http://www.sat.gob.mx/cfd/4}Comprobante", namespace,
            Version="4.0",
            Folio=self.comprobante["Folio"],
            Fecha=self.comprobante["Fecha"],
            SubTotal=self.comprobante["SubTotal"],
            #Sello="",
            NoCertificado=no_certificado,
            Certificado=certificado_base64,
            Total=self.comprobante["Total"],
            Moneda=self.comprobante["Moneda"],
            #TipoCambio="20.366",
            TipoDeComprobante=self.comprobante["TipoDeComprobante"],
            LugarExpedicion=self.comprobante["LugarExpedicion"],
            #CondicionesDePago="CONDICIONES",
            #FormaPago=self.comprobante["FormaPago"],
            Serie=self.comprobante["Serie"],  
            #MetodoPago=self.comprobante["MetodoPago"],
            Exportacion=self.comprobante["Exportacion"]
        )

        Emisor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', 
            Rfc=self.emisor["Rfc"],#"EKU9003173C9" ,
            Nombre=self.emisor["Nombre"],#"ESCUELA KEMPER URGATE",
            RegimenFiscal=self.emisor["RegimenFiscal"],#"601"
        )
        
        Receptor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor',
            Rfc=self.receptor["Rfc"],#"ICV060329BY0" ,
            Nombre=self.receptor["Nombre"],#"INMOBILIARIA CVA"  ,
            UsoCFDI=self.receptor["UsoCFDI"],#"G03",
            RegimenFiscalReceptor=self.receptor["RegimenFiscalReceptor"],#"601",
            DomicilioFiscalReceptor=self.receptor["DomicilioFiscalReceptor"],#"33826"
        )
        # Concepto de productos
        Conceptos=ET.SubElement(Comprobante, '''cfdi:Conceptos''')
        for c in self.concepto:
            Concepto = ET.SubElement(Conceptos, '''cfdi:Concepto''',
                Cantidad=c["Cantidad"],#"1.00",
                ClaveProdServ=c["ClaveProdServ"],#"78101802",
                ClaveUnidad=c["ClaveUnidad"],#"E48",
                Descripcion=c["Descripcion"],#"gastos generales",
                Importe=c["Importe"],#"1000.00",
                ValorUnitario=c["ValorUnitario"],#"0",
                ObjetoImp=c["ObjetoImp"],#"01" 
            )
    
        # Creación del elemento Complemento
        Complemento = ET.SubElement(Comprobante, 'cfdi:Complemento')

        # Creación del elemento Pagos dentro de Complemento
        Pagos = ET.SubElement(Complemento, 'pago20:Pagos', Version="2.0")

        # Creación del elemento Totales dentro de Pagos
        if "TotalTrasladosBaseIVA16" in list(self.comprobante["pagoTotals"].keys()):
            Totales = ET.SubElement(Pagos, 'pago20:Totales', 
                MontoTotalPagos=self.comprobante["pagoTotals"]["MontoTotalPagos"],
                #TotalRetencionesISR="12833.05",
                TotalTrasladosBaseIVA16=self.comprobante["pagoTotals"]["TotalTrasladosBaseIVA16"],
                TotalTrasladosImpuestoIVA16=self.comprobante["pagoTotals"]["TotalTrasladosImpuestoIVA16"]
            )
        elif "TotalTrasladosBaseIVA8" in list(self.comprobante["pagoTotals"].keys()):
            Totales = ET.SubElement(Pagos, 'pago20:Totales', 
                MontoTotalPagos=self.comprobante["pagoTotals"]["MontoTotalPagos"],
                #TotalRetencionesISR="12833.05",
                TotalTrasladosBaseIVA8=self.comprobante["pagoTotals"]["TotalTrasladosBaseIVA8"],
                TotalTrasladosImpuestoIVA8=self.comprobante["pagoTotals"]["TotalTrasladosImpuestoIVA8"]
            )
        elif "TotalTrasladosBaseIVA0" in list(self.comprobante["pagoTotals"].keys()):
            Totales = ET.SubElement(Pagos, 'pago20:Totales', 
                MontoTotalPagos=self.comprobante["pagoTotals"]["MontoTotalPagos"],
                #TotalRetencionesISR="12833.05",
                TotalTrasladosBaseIVA0=self.comprobante["pagoTotals"]["TotalTrasladosBaseIVA0"],
                TotalTrasladosImpuestoIVA0=self.comprobante["pagoTotals"]["TotalTrasladosImpuestoIVA0"]
            )

        # Creación del elemento Pago dentro de Pagos
        Pago = ET.SubElement(Pagos, 'pago20:Pago', 
            FechaPago=self.comprobante["pago"]["FechaPago"],#"2024-08-12T18:15:38",
            FormaDePagoP=self.comprobante["pago"]["FormaDePagoP"],#"02",
            MonedaP=self.comprobante["pago"]["MonedaP"],#"MXN",
            Monto=self.comprobante["pago"]["Monto"],#"116.00",
            TipoCambioP=self.comprobante["pago"]["TipoCambioP"],#"1"
        )

        # Creación del elemento DoctoRelacionado dentro de Pago
        DoctoRelacionado = ET.SubElement(Pago, 'pago20:DoctoRelacionado', 
            EquivalenciaDR=self.comprobante["DocRel"]["EquivalenciaDR"],#"1",
            Folio=self.comprobante["DocRel"]["Folio"],#"91",
            IdDocumento=self.comprobante["DocRel"]["IdDocumento"],#"D5FB4E3A-9E42-5381-A458-329C42F30458",
            ImpPagado=self.comprobante["DocRel"]["ImpPagado"],#"116.00",
            ImpSaldoAnt=self.comprobante["DocRel"]["ImpSaldoAnt"],#"116.00",
            ImpSaldoInsoluto=self.comprobante["DocRel"]["ImpSaldoInsoluto"],#"0.00",
            MonedaDR=self.comprobante["DocRel"]["MonedaDR"],#"MXN",
            NumParcialidad=self.comprobante["DocRel"]["NumParcialidad"],#"1",
            ObjetoImpDR=self.comprobante["DocRel"]["ObjetoImpDR"],#"02",
            Serie=self.comprobante["DocRel"]["Serie"],#"COA"
        )

        # Creación del elemento ImpuestosDR dentro de DoctoRelacionado
        ImpuestosDR = ET.SubElement(DoctoRelacionado, 'pago20:ImpuestosDR')

        # Creación de RetencionesDR dentro de ImpuestosDR
        # RetencionesDR = ET.SubElement(ImpuestosDR, 'pago20:RetencionesDR')

        # RetencionDR = ET.SubElement(RetencionesDR, 'pago20:RetencionDR', 
        #     BaseDR="6474.81",
        #     ImporteDR="647.48",
        #     ImpuestoDR="001",
        #     TasaOCuotaDR="0.100000",
        #     TipoFactorDR="Tasa"
        # )

        # Creación de TrasladosDR dentro de ImpuestosDR
        TrasladosDR = ET.SubElement(ImpuestosDR, 'pago20:TrasladosDR')

        TrasladoDR = ET.SubElement(TrasladosDR, 'pago20:TrasladoDR', 
            BaseDR=self.comprobante["DocRel"]["tax"]["Traslado"]["BaseDR"],
            ImporteDR=self.comprobante["DocRel"]["tax"]["Traslado"]["ImporteDR"],
            ImpuestoDR=self.comprobante["DocRel"]["tax"]["Traslado"]["ImpuestoDR"],
            TasaOCuotaDR=self.comprobante["DocRel"]["tax"]["Traslado"]["TasaOCuotaDR"],
            TipoFactorDR=self.comprobante["DocRel"]["tax"]["Traslado"]["TipoFactorDR"]
        )

        # Creación del elemento ImpuestosP dentro de Pago
        ImpuestosP = ET.SubElement(Pago, 'pago20:ImpuestosP')

        # Creación de RetencionesP dentro de ImpuestosP
        # RetencionesP = ET.SubElement(ImpuestosP, 'pago20:RetencionesP')

        # RetencionP = ET.SubElement(RetencionesP, 'pago20:RetencionP', 
        #     ImporteP="647.48",
        #     ImpuestoP="001"
        # )

        # Creación de TrasladosP dentro de ImpuestosP
        TrasladosP = ET.SubElement(ImpuestosP, 'pago20:TrasladosP')

        TrasladoP = ET.SubElement(TrasladosP, 'pago20:TrasladoP', 
            BaseP=self.comprobante["tax"]["Traslado"]["BaseP"],
            ImporteP=self.comprobante["tax"]["Traslado"]["ImporteP"],
            ImpuestoP=self.comprobante["tax"]["Traslado"]["ImpuestoP"],
            TasaOCuotaP=self.comprobante["tax"]["Traslado"]["TasaOCuotaP"],
            TipoFactorP=self.comprobante["tax"]["Traslado"]["TipoFactorP"]
        )

        xml_str = ET.tostring(Comprobante, encoding='utf-8', method='xml').decode('utf-8')
        with open(self.path+"Pago-"+self.invoice_name+'.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            archivo.close()
        
        # Generate cadena original.
        self.now = datetime.now().replace(microsecond=0).isoformat('T')
        self.XSLT_STYLE = etree.parse("integrador/cfdi/v40/cadenaoriginal.xslt")
        self.xml_string = open(self.path+"Pago-"+self.invoice_name+'.xml', 'rb').read()
        xml_etree = etree.fromstring(self.xml_string)
        self.cadena_original = self.obtener_cadena_original(xml_etree)

        return {
            "code": 200,
            "status": "OK",
            "message": "Success",
            "cadena_original": self.cadena_original,
            "no_cert": no_certificado
        }

    def createXMLCreditNote(self):
        """relelnar atributos del XML"""
        certificado_file = self.path_cert#+self.emisor["Rfc"]+'.cer'
        with open(certificado_file, 'rb') as f:
            certificado_data = f.read()
            certificado_base64 = base64.b64encode(certificado_data).decode('utf-8').replace('\n', '').replace('\r', '')

        os.system('openssl x509 -inform DER -in '+ certificado_file + ' -noout -serial > "'+self.path_serial+self.emisor["Rfc"]+'.txt"')
        with open(self.path_serial+self.emisor["Rfc"]+'.txt', 'r') as serial_file:
            serial = serial_file.read()
            no_certificado = serial[::2][4:]
 
        ET.register_namespace('cfdi', "http://www.sat.gob.mx/cfd/4")
        ET.register_namespace('xs', 'http://www.w3.org/2001/XMLSchema')
        namespace = {'xmlns:xs': 'http://www.w3.org/2001/XMLSchema', 'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance', 'xsi:schemaLocation':'http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd'}
        
        Comprobante = ET.Element("{http://www.sat.gob.mx/cfd/4}Comprobante", namespace,
            Version="4.0",
            Folio=self.comprobante["Folio"],
            Fecha=self.comprobante["Fecha"],
            SubTotal=self.comprobante["SubTotal"],
            #Sello="",
            NoCertificado=no_certificado,
            Certificado=certificado_base64,
            Total=self.comprobante["Total"],
            Moneda=self.comprobante["Moneda"],
            #TipoCambio="20.366",
            TipoDeComprobante=self.comprobante["TipoDeComprobante"],
            LugarExpedicion=self.comprobante["LugarExpedicion"],
            #CondicionesDePago="CONDICIONES",
            FormaPago=self.comprobante["FormaPago"],
            Serie=self.comprobante["Serie"],
            MetodoPago=self.comprobante["MetodoPago"],
            Exportacion=self.comprobante["Exportacion"]
        )

        # Creación del elemento DoctoRelacionado
        DoctoRelacionados = ET.SubElement(Comprobante, 'cfdi:CfdiRelacionados', 
            TipoRelacion="01"
        )
        for dc in self.comprobante["DocRel"]:
            DoctoRelacionado = ET.SubElement(DoctoRelacionados, 'cfdi:CfdiRelacionado ', 
                UUID=dc
            )

        Emisor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Emisor', 
            Rfc=self.emisor["Rfc"],#"EKU9003173C9" ,
            Nombre=self.emisor["Nombre"],#"ESCUELA KEMPER URGATE",
            RegimenFiscal=self.emisor["RegimenFiscal"],#"601"
        )
        
        Receptor = ET.SubElement(Comprobante, '{http://www.sat.gob.mx/cfd/4}Receptor',
            Rfc=self.receptor["Rfc"],#"ICV060329BY0" ,
            Nombre=self.receptor["Nombre"],#"INMOBILIARIA CVA"  ,
            UsoCFDI=self.receptor["UsoCFDI"],#"G03",
            RegimenFiscalReceptor=self.receptor["RegimenFiscalReceptor"],#"601",
            DomicilioFiscalReceptor=self.receptor["DomicilioFiscalReceptor"],#"33826"
        )
        # Concepto de productos
        Conceptos = ET.SubElement(Comprobante, '''cfdi:Conceptos''')
        for c in self.concepto:
            Concepto = ET.SubElement(Conceptos, '''cfdi:Concepto''',
                Cantidad=c["Cantidad"],#"1.00",
                ClaveProdServ=c["ClaveProdServ"],#"78101802",
                ClaveUnidad=c["ClaveUnidad"],#"E48",
                Descripcion=c["Descripcion"],#"gastos generales",
                Importe=c["Importe"],#"1000.00",
                ValorUnitario=c["ValorUnitario"],#"0",
                ObjetoImp=c["ObjetoImp"],#"01" 
            )
            #IMPUESTOS CONCEPTO
            Impuestos=ET.SubElement(Concepto, '''cfdi:Impuestos''')
            Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
            Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
                Base=c["tax"]["Traslado"]["Base"],#"1000.00",
                Importe=c["tax"]["Traslado"]["Importe"],#"160.00", 
                Impuesto=c["tax"]["Traslado"]["Impuesto"],#"002", 
                TasaOCuota=c["tax"]["Traslado"]["TasaOCuota"],#"0.160000", 
                TipoFactor=c["tax"]["Traslado"]["TipoFactor"],#"Tasa"
            )

        #IMPUESTOS COMPROBANTE
        #print(self.comprobante["tax"]["TotalImpuestosTrasladados"])
        Impuestos=ET.SubElement(Comprobante, '''cfdi:Impuestos''',
            #TotalImpuestosRetenidos=self.comprobante["tax"]["TotalImpuestosRetenidos"],#"40.00",
            TotalImpuestosTrasladados=self.comprobante["tax"]["TotalImpuestosTrasladados"]#"160.00"
        )
        # Retenciones=ET.SubElement(Impuestos, '''cfdi:Retenciones''')
        # Retencion=ET.SubElement(Retenciones, '''cfdi:Retencion''',
        #     Importe=self.comprobante["tax"]["Retencion"]["Importe"],#"40.00", 
        #     Impuesto=self.comprobante["tax"]["Retencion"]["Impuesto"]#"002"
        #)
        #print(self.comprobante["tax"]["Traslado"])
        Traslados=ET.SubElement(Impuestos, '''cfdi:Traslados''')
        Traslado=ET.SubElement(Traslados, '''cfdi:Traslado''',
            Importe=self.comprobante["tax"]["Traslado"]["Importe"],#"160.00",
            Base=self.comprobante["tax"]["Traslado"]["Base"],#"1000.00", 
            Impuesto=self.comprobante["tax"]["Traslado"]["Impuesto"],#"002", 
            TasaOCuota=self.comprobante["tax"]["Traslado"]["TasaOCuota"],#"0.160000", 
            TipoFactor=self.comprobante["tax"]["Traslado"]["TipoFactor"],#"Tasa"
        )

        xml_str = ET.tostring(Comprobante, encoding='utf-8', method='xml').decode('utf-8')
        with open(self.path+self.invoice_name+'.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            archivo.close()
        
        # Generate cadena original.
        self.now = datetime.now().replace(microsecond=0).isoformat('T')
        self.XSLT_STYLE = etree.parse("integrador/cfdi/v40/cadenaoriginal.xslt")
        self.xml_string = open(self.path+self.invoice_name+'.xml', 'rb').read()
        xml_etree = etree.fromstring(self.xml_string)
        self.cadena_original = self.obtener_cadena_original(xml_etree)

        return {
            "code": 200,
            "status": "OK",
            "message": "Success",
            "cadena_original": self.cadena_original,
            "no_cert": no_certificado
        }

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
        with open('CFDI40.xml', 'w', encoding='utf-8') as archivo:
            archivo.truncate(0)
            archivo.write(xml_str)
            print("XML SELLADO DE FORMA EXITOSA!!")


if __name__ == "__main__":
    emisor = {
        "Rfc": "XIQB891116QE4",
        "Nombre": "BERENICE XIMO QUEZADA",
        "RegimenFiscal": "601"
    }
    #print(_invoice_data)
    #print(_invoice_data["data"]["uso_cfdi"])
    receptor = {
        "Rfc": "ICV060329BY0",
        "Nombre": "INMOBILIARIA CVA",
        "UsoCFDI": "S01",
        "RegimenFiscalReceptor": "616",
        "DomicilioFiscalReceptor": "86400"
    }
    comprobante = {
        "Folio": "1",
        "Fecha": (datetime.now() - dt.timedelta(hours=1)).replace(microsecond=0).isoformat('T'),
        "SubTotal": "{:.2f}".format(1000),
        "Total": "{:.2f}".format(1160),
        "Moneda": "MXN",
        "TipoDeComprobante": "E",
        "LugarExpedicion": "26017",
        "FormaPago": "02",
        "MetodoPago": "PUE",
        "Serie": "PREDIAL",
        "Exportacion": "01",
        "tax": {
            "TotalImpuestosRetenidos": "40.00",
            "TotalImpuestosTrasladados": "{:.2f}".format(0),
            "Retencion": {
                "Importe": "40.00",
                "Impuesto": "002"
            },
            "Traslado": {
                "Importe": "{:.2f}".format(1000),
                "Base": "{:.2f}".format(160),
                "Impuesto": "002",
                "TasaOCuota": "0.160000",
                "TipoFactor": "Tasa"
            }
        }
    }
    concepto = [{
        "Cantidad": "1",
        "ClaveProdServ": "80131500",
        "ClaveUnidad": "CE",
        "Descripcion": "ARRENDAMIENTO DE JUAREZ PTE 108-A",
        "Importe": "1000",
        "ValorUnitario": "1000",
        "ObjetoImp": "02",
        "tax":{
            "Traslado": {
                "Base": "{:.2f}".format(1000),
                "Importe": "{:.2f}".format(160),
                "Impuesto": "002",
                "TasaOCuota": "0.160000",
                "TipoFactor": "Tasa"
            },
            "Retencion": {
                "Base": "1000.00",
                "Importe": "40.00",
                "Impuesto": "002",
                "TasaOCuota": "0.040000",
                "TipoFactor": "Tasa"
            }
        }
    }]
    instancia = crear_cadena40(
        emisor=emisor,
        receptor=receptor,
        comprobante=comprobante,
        concepto=concepto,
        path_cert="C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/cert/XIQB891116QE4.cer",
        type_document=0
    )
    #result = instancia.createXMLPayment()
    instancia.createXMLCreditNote()