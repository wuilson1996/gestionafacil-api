from zeep import Client
import logging
import base64
from lxml import etree
from zeep.plugins import HistoryPlugin
from integrador.generate_xml import *
from .models import *
from .make_pdf import *
from .get_attribute import *
from django.conf import settings
from setting.models import *

class FinkokService:
    def __init__(self, rfc=None) -> None:
        # Username y Password de Finkok
        self.username = settings.API_USERNAME
        self.password = settings.API_PASSWORD
        self.invoice_path = "documents/"
        self.timbre_path = "media/timbres/"
        self.rfc = rfc
        self.url = settings.URL_API_SOAT
        self.path_test = "test/"
        self.url_file = settings.URL_FILE
        self.PATH_ACUSES2_CANCELACION = "documents"

    def register_client(self, path_cer, path_key, pwd):
        result = {
            "code": 400,
            "message": "",
            "status": False
        }
        type_user = 'O'
        coupon = ''
        added = ''
        try:
            # Read the x509 certificate file on PEM format and encode it on base64
            file = open(path_cer, "rb")
            cer = (file.read())
            
            file = open(path_key, "rb")
            key = (file.read())
            
            history = HistoryPlugin()
            client = Client(wsdl = self.url+"/registration.wsdl", plugins = [history])
            
            response = client.service.add(self.username,self.password,self.rfc, type_user, '', '',cer, key, pwd)

            result["message"] = response["message"]
            result["status"] = response["success"]
            result["code"] = 200
        except Exception as e:
            result["message"] = str(e)
            result["status"] = "Fail"

        return result

    def update_register_client(self, status):
        result = {
            "code": 400,
            "message": "",
            "status": False
        }
        try:
            #status = 'S' # (Valores permitidos 'A' : 'Activate', 'S' : 'suspend')
            
            # Consumir el método edit del web services de registration
            history = HistoryPlugin() 
            client = Client(wsdl = self.url+"/registration.wsdl", plugins = [history])
            
            response = client.service.edit(self.username, self.password, self.rfc, status)
        
            result["code"] = 200
            result["status"] = response["success"]
            result["message"] = response["message"]
        except Exception as e:
            result["message"] = str(e)
        
        return result

    def get_register_client(self):
        result = {
            "code": 400,
            "message": "",
            "status": False,
            "users": {"ResellerUser":[]}
        }
        try:
            # Consumir el método get del web services de registration
            history = HistoryPlugin() 
            client = Client(wsdl = self.url+"/registration.wsdl", plugins = [history])
            
            response = client.service.get(self.username,self.password,self.rfc)

            for u in response["users"]["ResellerUser"]:
                result["users"]["ResellerUser"].append({
                    'status': u["status"],
                    'counter': u["counter"],
                    'taxpayer_id': u["taxpayer_id"],
                    'credit': u["credit"]
                })
            result["code"] = 200
            result["message"] = response["message"]
            result["status"] = "Success"
        except Exception as e:
            result["message"] = str(e)
            result["status"] = "Fail"
        return result
    
    def assign_register_client(self, credit):
        result = {
            "code": 400,
            "message": "",
            "status": False,
        }
        try:
            # Consumir el método assign del web services de registration
            history = HistoryPlugin()
            client = Client(wsdl = self.url+"/registration.wsdl", plugins = [history])
            
            response = client.service.assign(self.username, self.password, self.rfc, credit)
            print(response)

            result["code"] = 200
            result["message"] = response["message"]
            result["status"] = True

        except Exception as e:
            result["message"] = str(e)
            result["status"] = "Fail"
        return result

    def __assign_register_client(self):
        result = {
            "code": 400,
            "message": "",
            "status": False,
        }
        try:
            
            result["code"] = 200
            #result["message"] = response["message"]
            result["status"] = True
        except Exception as e:
            result["message"] = str(e)
            result["status"] = "Fail"
        return result
    
    def stamp(self):
        #Read the xml file and turn in in bytes
        file = open(self.invoice_path+"stamp.xml")
        lines = "".join(file.readlines())
        xml = lines.encode("UTF-8")
        
        history = HistoryPlugin()
        client = Client(wsdl = self.url+"/stamp.wsdl", plugins = [history])
        contenido = client.service.stamp(xml, self.username, self.password)
        xml = contenido.xml
        print(contenido)
    
    def agregar_saltos_de_linea(self, texto, longitud_maxima):
        resultado = ''
        cont = 0

        for letter in texto:
            if cont + len(letter) > longitud_maxima:
                resultado += '\n'
                cont = 0
            resultado += letter
            cont += len(letter) + 1  # Sumar 1 por el espacio agregado

        return resultado

    def sing_stamp(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        #if  _invoice.state != "Comprobante timbrado satisfactoriamente":
        file_name = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)
        # Read the xml file and encode it to bytes
        history = HistoryPlugin()
        #file = open(self.invoice_path+file_name+".xml")
        #lines = "".join(file.readlines())
        #xml = lines.encode("UTF-8")
        with open(self.invoice_path+file_name+".xml", "rb") as file:
            xml = file.read()
        # Consuming the stamp service
        client = Client(wsdl = self.url+"/stamp.wsdl", plugins = [history])
        response = client.service.sign_stamp(xml, self.username, self.password)
        xml = response.xml
        #print(response)

        insident = []
        if response["Incidencias"] != None:
            for i in response["Incidencias"]["Incidencia"]:
                insident.append({
                    'IdIncidencia': i["IdIncidencia"],
                    'RfcEmisor': i["RfcEmisor"],
                    'Uuid': i["Uuid"],
                    'CodigoError': i["CodigoError"],
                    'WorkProcessId': i["WorkProcessId"],
                    'MensajeIncidencia': i["MensajeIncidencia"],
                    'ExtraInfo': i["ExtraInfo"],
                    'NoCertificadoPac': i["NoCertificadoPac"],
                    'FechaRegistro': i["FechaRegistro"]
                })
        else:
            _name_file = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)+".xml"
            _file_name_save = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)
            self.generate_xml_by_str(response["xml"], _name_file)
            
            _invoice.UUID = response["UUID"]
            _invoice.cufe = response["SatSeal"]

            _invoice.state = "Timbrada" if  response["CodEstatus"] == "Comprobante timbrado satisfactoriamente" else "No timbrada"
            _invoice.state_invoice = "Por cobrar" if  response["CodEstatus"] == "Comprobante timbrado satisfactoriamente" else "Borrador"

            _invoice.no_cert_sat = response["NoCertificadoSAT"]
            _invoice.date_cert = response["Fecha"]
            xml_by_dict = get_att(self.timbre_path+_name_file)
            sello_cfdi = xml_by_dict["cfdi:Comprobante"]["cfdi:Complemento"]["ns2:TimbreFiscalDigital"]["@SelloCFD"]
            #print(sello_cfdi)
            _invoice.sello_cfdi = sello_cfdi
            _invoice.save()

            _invoice_data = _invoice.get_invoice(data)
            
            _invoice_data["data"]["path_dir"] = self.timbre_path
            _invoice_data["data"]["sello_cfdi"] = self.agregar_saltos_de_linea(_invoice.sello_cfdi, 140)
            _invoice_data["data"]["cadena_original"] = self.agregar_saltos_de_linea(_invoice.cadena_original, 140)
            #print(_invoice_data["data"])
            _invoice_data["data"]["SatSeal"] = self.agregar_saltos_de_linea(_invoice_data["data"]["SatSeal"], 240)
            
            try:
                Create_PDF_Invoice(_invoice_data["data"], "pdf_invoice", _file_name_save)
                _invoice.status_file = "Success"
                _invoice.pdf = self.url_file+self.timbre_path+str(_name_file).replace("xml", "pdf")
                _invoice.save()
            except Exception as epdf:
                _invoice.status_file = str(epdf)
                _invoice.save()
            
        return {
            'xml': response["xml"],
            'UUID': response["UUID"],
            'faultstring': response["faultstring"],
            'Fecha': response["Fecha"],
            'CodEstatus': response["CodEstatus"],
            'faultcode': response["faultcode"],
            'SatSeal': response["SatSeal"],
            'Incidencias': {
                'Incidencia': insident
            },
            'NoCertificadoSAT': response["NoCertificadoSAT"]
        }
    
    def sing_stamp_payment(self, data):
        payment_invoice = PaymentInvoice.objects.filter(pk = data["pk"]).first()
        file_name = "Pago-"+payment_invoice.invoice.branch.company.documentI+str("P")+str(payment_invoice.number)
        # Read the xml file and encode it to bytes
        history = HistoryPlugin()
        file = open(self.invoice_path+file_name+".xml")
        lines = "".join(file.readlines())
        xml = lines.encode("UTF-8")
        
        # Consuming the stamp service
        client = Client(wsdl = self.url+"/stamp.wsdl", plugins = [history])
        response = client.service.sign_stamp(xml, self.username, self.password)
        xml = response.xml
        #print(response)

        insident = []
        if response["Incidencias"] != None:
            for i in response["Incidencias"]["Incidencia"]:
                insident.append({
                    'IdIncidencia': i["IdIncidencia"],
                    'RfcEmisor': i["RfcEmisor"],
                    'Uuid': i["Uuid"],
                    'CodigoError': i["CodigoError"],
                    'WorkProcessId': i["WorkProcessId"],
                    'MensajeIncidencia': i["MensajeIncidencia"],
                    'ExtraInfo': i["ExtraInfo"],
                    'NoCertificadoPac': i["NoCertificadoPac"],
                    'FechaRegistro': i["FechaRegistro"]
                })
        else:
            _name_file = file_name+".xml"
            _file_name_save = file_name
            self.generate_xml_by_str(response["xml"], _name_file)
            
            payment_invoice.UUID = response["UUID"]
            payment_invoice.cufe = response["SatSeal"]

            payment_invoice.state = "Timbrada" if  response["CodEstatus"] == "Comprobante timbrado satisfactoriamente" else "No timbrada"

            payment_invoice.no_cert_sat = response["NoCertificadoSAT"]
            payment_invoice.date_cert = response["Fecha"]
            xml_by_dict = get_att(self.timbre_path+_name_file)
            #print(xml_by_dict["cfdi:Comprobante"])
            sello_cfdi = xml_by_dict["cfdi:Comprobante"]["cfdi:Complemento"]["ns3:TimbreFiscalDigital"]["@SelloCFD"]
            #print(sello_cfdi)
            payment_invoice.sello_cfdi = sello_cfdi
            payment_invoice.save()

            _invoice_data = payment_invoice.get_payment(data)
            
            _invoice_data["data"]["path_dir"] = self.timbre_path
            _invoice_data["data"]["sello_cfdi"] = self.agregar_saltos_de_linea(payment_invoice.sello_cfdi, 250)
            _invoice_data["data"]["cadena_original"] = self.agregar_saltos_de_linea(payment_invoice.cadena_original, 320)
            #print(_invoice_data["data"])
            _invoice_data["data"]["SatSeal"] = self.agregar_saltos_de_linea(sello_cfdi, 250)
            
            try:
                #print(_invoice_data)
                Create_PDF_Payment(_invoice_data["data"], "pdf_payment", _file_name_save)
                payment_invoice.status_file = "Success"
                payment_invoice.pdf = self.url_file+self.timbre_path+str(_name_file).replace("xml", "pdf")
                payment_invoice.save()
            except Exception as epdf:
                print("Error create pdf: "+str(epdf))
                payment_invoice.status_file = str(epdf)
                payment_invoice.save()
            
        return {
            'xml': response["xml"],
            'UUID': response["UUID"],
            'faultstring': response["faultstring"],
            'Fecha': response["Fecha"],
            'CodEstatus': response["CodEstatus"],
            'faultcode': response["faultcode"],
            'SatSeal': response["SatSeal"],
            'Incidencias': {
                'Incidencia': insident
            },
            'NoCertificadoSAT': response["NoCertificadoSAT"]
        }

    def sing_stamp_credit_note(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        #if  _invoice.state != "Comprobante timbrado satisfactoriamente":
        file_name = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)
        # Read the xml file and encode it to bytes
        history = HistoryPlugin()
        #file = open(self.invoice_path+file_name+".xml")
        #lines = "".join(file.readlines())
        #xml = lines.encode("UTF-8")
        with open(self.invoice_path+file_name+".xml", "rb") as file:
            xml = file.read()
        # Consuming the stamp service
        client = Client(wsdl = self.url+"/stamp.wsdl", plugins = [history])
        response = client.service.sign_stamp(xml, self.username, self.password)
        xml = response.xml
        #print(response)

        insident = []
        if response["Incidencias"] != None:
            for i in response["Incidencias"]["Incidencia"]:
                insident.append({
                    'IdIncidencia': i["IdIncidencia"],
                    'RfcEmisor': i["RfcEmisor"],
                    'Uuid': i["Uuid"],
                    'CodigoError': i["CodigoError"],
                    'WorkProcessId': i["WorkProcessId"],
                    'MensajeIncidencia': i["MensajeIncidencia"],
                    'ExtraInfo': i["ExtraInfo"],
                    'NoCertificadoPac': i["NoCertificadoPac"],
                    'FechaRegistro': i["FechaRegistro"]
                })
        else:
            _name_file = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)+".xml"
            _file_name_save = _invoice.branch.company.documentI+str(_invoice.prefix)+str(_invoice.number)
            self.generate_xml_by_str(response["xml"], _name_file)
            
            _invoice.UUID = response["UUID"]
            _invoice.cufe = response["SatSeal"]

            _invoice.state = "Timbrada" if  response["CodEstatus"] == "Comprobante timbrado satisfactoriamente" else "No timbrada"
            _invoice.state_invoice = "Por cobrar" if  response["CodEstatus"] == "Comprobante timbrado satisfactoriamente" else "Borrador"

            _invoice.no_cert_sat = response["NoCertificadoSAT"]
            _invoice.date_cert = response["Fecha"]
            xml_by_dict = get_att(self.timbre_path+_name_file)
            #print(xml_by_dict["cfdi:Comprobante"])
            sello_cfdi = xml_by_dict["cfdi:Comprobante"]["cfdi:Complemento"]["ns2:TimbreFiscalDigital"]["@SelloCFD"]
            #print(sello_cfdi)
            _invoice.sello_cfdi = sello_cfdi
            _invoice.save()

            _invoice_data = _invoice.get_invoice(data)
            
            _invoice_data["data"]["path_dir"] = self.timbre_path
            _invoice_data["data"]["sello_cfdi"] = self.agregar_saltos_de_linea(_invoice.sello_cfdi, 180)
            _invoice_data["data"]["cadena_original"] = self.agregar_saltos_de_linea(_invoice.cadena_original, 240)
            #print(_invoice_data["data"])
            _invoice_data["data"]["SatSeal"] = self.agregar_saltos_de_linea(_invoice_data["data"]["SatSeal"], 180)
            
            try:
                Create_PDF_Invoice(_invoice_data["data"], "pdf_nc", _file_name_save)
                _invoice.status_file = "Success"
                _invoice.pdf = self.url_file+self.timbre_path+str(_name_file).replace("xml", "pdf")
                _invoice.save()
            except Exception as epdf:
                _invoice.status_file = str(epdf)
                _invoice.save()
            
        return {
            'xml': response["xml"],
            'UUID': response["UUID"],
            'faultstring': response["faultstring"],
            'Fecha': response["Fecha"],
            'CodEstatus': response["CodEstatus"],
            'faultcode': response["faultcode"],
            'SatSeal': response["SatSeal"],
            'Incidencias': {
                'Incidencia': insident
            },
            'NoCertificadoSAT': response["NoCertificadoSAT"]
        }

    def calcula_tax(self, value, tax_porcent):
        # Calculate the factor to remove the tax
        tax_factor = 1 + (tax_porcent / 100)
        # Calculate the amount before tax
        return value - (value / tax_factor)

    def generate_payment_xml(self, data):
        payment_invoice = PaymentInvoice.objects.filter(pk = data["pk"]).first()
        totals = 0
        parcialidad = 1
        for pinv in PaymentInvoice.objects.filter(invoice=payment_invoice.invoice):
            if pinv.state == "Timbrada":
                totals += pinv.amount
                parcialidad += 1
        emisor = {
            "Rfc": payment_invoice.invoice.branch.company.documentI,
            "Nombre": payment_invoice.invoice.branch.company.name,
            "RegimenFiscal": payment_invoice.invoice.branch.company.type_regime.code
        }
        #print(_invoice_data)
        #print(_invoice_data["data"]["uso_cfdi"])
        receptor = {
            "Rfc": payment_invoice.invoice.customer.identification_number,
            "Nombre": payment_invoice.invoice.customer.name,
            "UsoCFDI": "CP01",
            "RegimenFiscalReceptor": payment_invoice.invoice.customer.type_regime.code,
            "DomicilioFiscalReceptor": payment_invoice.invoice.customer.address.split(",")[0]
        }
        tax_porcent2 = 0
        for d in Details_Invoice.objects.filter(invoice = payment_invoice.invoice):
            tax_porcent2 = int(d.tax_value)
            break
        TipoDeComprobante = "P"
        #tax_porcent2 = 16
        tax = self.calcula_tax(payment_invoice.amount, tax_porcent2)
        #print(tax, payment_invoice.amount, payment_invoice.amount - tax, tax_porcent2)
        if tax_porcent2 == 16:
            totalsPayment = {
                "MontoTotalPagos": "{:.2f}".format(payment_invoice.amount),
                "TotalRetencionesISR": "",
                "TotalTrasladosBaseIVA16": "{:.2f}".format(payment_invoice.amount - tax),
                "TotalTrasladosImpuestoIVA16": "{:.2f}".format(tax)
            }
        elif tax_porcent2 == 8:
            totalsPayment = {
                "MontoTotalPagos": "{:.2f}".format(payment_invoice.amount),
                "TotalRetencionesISR": "",
                "TotalTrasladosBaseIVA8": "{:.2f}".format(payment_invoice.amount - tax),
                "TotalTrasladosImpuestoIVA8": "{:.2f}".format(tax)
            }
        elif tax_porcent2 == 0:
            totalsPayment = {
                "MontoTotalPagos": "{:.2f}".format(payment_invoice.amount),
                "TotalRetencionesISR": "",
                "TotalTrasladosBaseIVA0": "{:.2f}".format(payment_invoice.amount - tax),
                "TotalTrasladosImpuestoIVA0": "{:.2f}".format(tax)
            }
        comprobante = {
            "Folio": str(payment_invoice.number),
            "Fecha": (datetime.now() - dt.timedelta(hours=1)).replace(microsecond=0).isoformat('T'),
            "SubTotal": "0",
            "Total": "0",
            "Moneda": "XXX",
            "TipoDeComprobante": TipoDeComprobante,
            "LugarExpedicion": payment_invoice.invoice.branch.company.address.split(",")[0],
            "Serie": "P",
            "Exportacion": "01",
            "tax": {
                "TotalImpuestosRetenidos": "40.00",
                "TotalImpuestosTrasladados": "{:.2f}".format(0),
                "Retencion": {
                    "ImporteP": "11.60",
                    "ImpuestoP": "001",
                },
                "Traslado": {
                    "BaseP": "{:.2f}".format(payment_invoice.amount - tax),
                    "ImporteP": "{:.2f}".format(tax),
                    "ImpuestoP": "002",
                    "TasaOCuotaP": "0."+str(tax_porcent2 if tax_porcent2 > 0 else "00")+"0000",
                    "TipoFactorP": "Tasa"
                }
            },
            "pagoTotals":totalsPayment,
            "pago":{
                "FechaPago": str("2024-08-13T15:24:00"),
                "FormaDePagoP": str(payment_invoice.payment_form._id),
                "MonedaP": "MXN",
                "Monto": "{:.2f}".format(payment_invoice.amount),
                "TipoCambioP": "1"
            },
            "DocRel":{
                "EquivalenciaDR": "1",
                "Folio": str(payment_invoice.invoice.number),
                "IdDocumento": payment_invoice.invoice.UUID,
                "ImpPagado": "{:.2f}".format(payment_invoice.amount),
                "ImpSaldoAnt": "{:.2f}".format(payment_invoice.invoice.total - totals),
                "ImpSaldoInsoluto": "{:.2f}".format((payment_invoice.invoice.total - payment_invoice.amount) - totals),
                "MonedaDR": "MXN",
                "NumParcialidad": str(parcialidad),
                "ObjetoImpDR": "02",
                "Serie": payment_invoice.invoice.prefix,
                "tax": {
                    "Retencion": {
                        "BaseDR": "116.00",
                        "ImporteDR": "11.60",
                        "ImpuestoDR": "001",
                        "TasaOCuotaDR": "0.100000",
                        "TipoFactorDR": "Tasa",
                    },
                    "Traslado": {
                        "BaseDR": "{:.2f}".format(payment_invoice.amount - tax),
                        "ImporteDR": "{:.2f}".format(tax),
                        "ImpuestoDR": "002",
                        "TasaOCuotaDR": "0."+str(tax_porcent2 if tax_porcent2 > 0 else "00")+"0000",
                        "TipoFactorDR": "Tasa"
                    }
                }
            }
        }
        #print(comprobante)
        
        concepto = [{
            "Cantidad": "1",
            "ClaveProdServ": "84111506",
            "ClaveUnidad": "ACT",
            "Descripcion": "Pago",
            "Importe": "0",
            "ValorUnitario": "0",
            "ObjetoImp": "01"
        }]
        instancia = crear_cadena40(
            emisor=emisor,
            receptor=receptor,
            comprobante=comprobante,
            concepto=concepto,
            path_cert=str(payment_invoice.invoice.branch.company.cer_file),
            type_document=0
        )
        result = instancia.createXMLPayment()
        payment_invoice.no_cert_dig = result["no_cert"]
        payment_invoice.cadena_original = result["cadena_original"]
        payment_invoice.imp_saldo_ant = float("{:.2f}".format(payment_invoice.invoice.total - totals))
        payment_invoice.imp_saldo_insoluto = float("{:.2f}".format((payment_invoice.invoice.total - payment_invoice.amount) - totals))
        payment_invoice.parcialidad = parcialidad
        payment_invoice.save()

        result = {
            "status": "OK",
            "code": 200,
            "Message": "Success"
        }
        return result

    def generate_xml(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        if  _invoice.state != "Comprobante timbrado satisfactoriamente":
            #print(_invoice)
            #print(_invoice.get_invoice(data))
            _invoice_data = _invoice.get_invoice(data)
            tax_porcent = 0
            tax = 0
            total = 0
            sub_total = 0
            #cant = 0
            concepto = []
            #print(_invoice_data)
            for p in _invoice_data["data"]["details"]:
                if _invoice.type_document == 1:
                    tax += p["tax"] * p["quantity"]
                    total += p["price"] * p["quantity"]
                    sub_total += p["cost"] * p["quantity"]
                    #cant += p["quantity"]
                    tax_porcent = p["tax_value"]
                    concepto.append({
                        "Cantidad": str(p["quantity"]),
                        "ClaveProdServ": p["code"],
                        "ClaveUnidad": p["clave_uni"],
                        "Descripcion": p["name"],
                        "Descuento": "0",#"22500.00",
                        "Importe": "{:.2f}".format(p["cost"] * p["quantity"]),
                        #"NoIdentificacion":"0001",
                        "Unidad": "No aplica",
                        "ValorUnitario": "{:.2f}".format(p["cost"]),
                        "ObjetoImp": "02",
                        "tax":{
                            "Traslado": {
                                "Base": "{:.2f}".format(p["cost"] * p["quantity"]),
                                "Importe": "{:.2f}".format(p["tax"] * p["quantity"]),
                                "Impuesto": "002",
                                "TasaOCuota": "0."+str(p["tax_value"] if p["tax_value"] > 0 else "00")+"0000",
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
                    })
                else:
                    tax2 = 0
                    total2 = 0
                    sub_total2 = 0
                    tax_porcent2 = 0
                    payment_form = {}
                    for j in p["details"]:
                        tax2 += j["tax"] * j["quantity"]
                        total2 += j["price"] * j["quantity"]
                        sub_total2 += j["cost"] * j["quantity"]
                        #cant2 += 1
                        tax_porcent2 = j["tax_value"]
                        
                    
                    tax_porcent2 = 16
                    concepto.append({
                        "Cantidad": str(1),
                        "ClaveProdServ": p["code"],
                        "ClaveUnidad": p["clave_uni"],
                        "Descripcion": p["name"],
                        "Descuento": "0",#"22500.00",
                        "Importe": "{:.2f}".format(sub_total2),
                        #"NoIdentificacion":"0001",
                        "Unidad": "No aplica",
                        "ValorUnitario": "{:.2f}".format(sub_total2),
                        "ObjetoImp": "02",
                        "tax":{
                            "Traslado": {
                                "Base": "{:.2f}".format(sub_total2),
                                "Importe": "{:.2f}".format(tax2),
                                "Impuesto": "002",
                                "TasaOCuota": "0."+str(tax_porcent2 if tax_porcent2 > 0 else "00")+"0000",
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
                    })
                    tax += tax2
                    total += total2
                    sub_total += sub_total2
                    #cant += 1
                    tax_porcent = tax_porcent2
                    #print(p["total"], total2, total)
                    #print(tax_porcent)

            #print(concepto)
            #print(total, sub_total, tax)
            emisor = {
                "Rfc": _invoice.branch.company.documentI,
                "Nombre": _invoice.branch.company.name,
                "RegimenFiscal": _invoice.branch.company.type_regime.code
            }
            #print(_invoice_data)
            #print(_invoice_data["data"]["uso_cfdi"])
            receptor = {
                "Rfc": _invoice.customer.identification_number,
                "Nombre": _invoice.customer.name,
                "UsoCFDI": _invoice_data["data"]["uso_cfdi"]["code"],
                "RegimenFiscalReceptor": _invoice.customer.type_regime.code,
                "DomicilioFiscalReceptor": _invoice.customer.address.split(",")[0]
            }
            #print(_invoice_data["data"]["customer"]["payment_form"])
            TipoDeComprobante = "I" # ingresos e ingresos de traslado.
            #print(receptor)
            comprobante = {
                "Folio": str(_invoice.number),
                "Fecha": (datetime.now() - dt.timedelta(hours=1)).replace(microsecond=0).isoformat('T'),
                "SubTotal": "{:.2f}".format(sub_total),
                "Total": "{:.2f}".format(total),
                "Moneda": "MXN",
                "TipoDeComprobante": TipoDeComprobante,
                "LugarExpedicion": _invoice.branch.company.address.split(",")[0],
                "FormaPago": _invoice_data["data"]["payment_form_data"]["_id"],
                "Serie": str(_invoice.prefix),
                "MetodoPago": _invoice_data["data"]["payment_method_data"]["code"],
                "Exportacion": "01",
                "tax": {
                    "TotalImpuestosRetenidos": "40.00",
                    "TotalImpuestosTrasladados": "{:.2f}".format(tax),
                    "Retencion": {
                        "Importe": "40.00",
                        "Impuesto": "002"
                    },
                    "Traslado": {
                        "Importe": "{:.2f}".format(tax),
                        "Base": "{:.2f}".format(sub_total),
                        "Impuesto": "002",
                        "TasaOCuota": "0."+str(tax_porcent if tax_porcent > 0 else "00")+"0000",
                        "TipoFactor": "Tasa"
                    }
                }
            }
            _period = None
            if _invoice.type_document == 5:
                _period = {
                    "year": "2024",
                    "month": "08",
                    "period": "01"
                }
            #print(_period)
            #print("------------------------------------------------")
            #print(emisor)
            #print(receptor)
            #print(comprobante)
            #print(concepto)
            #print("-------------------------------------------------")

            instancia = crear_cadena40(
                emisor=emisor, 
                receptor=receptor, 
                comprobante=comprobante, 
                concepto=concepto, 
                path_cert=str(_invoice.branch.company.cer_file), 
                type_document=_invoice.type_document, 
                period=_period
            )
            result = instancia.creacionXML()
            _invoice.no_cert_dig = result["no_cert"]
            _invoice.cadena_original = result["cadena_original"]
            _invoice.save()
            
            result = {
               "status": "OK",
               "code": 200,
               "Message": "Success"
            }
        else:
            result = {
                "status": "Fail",
                "code": 400,
                "Message": _invoice.state
            }
        return result

    def generate_xml_nc(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        if  _invoice.state != "Comprobante timbrado satisfactoriamente":
            #print(_invoice)
            #print(_invoice.get_invoice(data))
            _invoice_data = _invoice.get_invoice(data)
            tax_porcent = 0
            tax = 0
            total = 0
            sub_total = 0
            #cant = 0
            concepto = []
            #print(_invoice_data)
            for p in _invoice_data["data"]["details"]:
                tax += p["tax"] * p["quantity"]
                total += p["price"] * p["quantity"]
                sub_total += p["cost"] * p["quantity"]
                #cant += p["quantity"]
                tax_porcent = p["tax_value"]
                #print(p)
                concepto.append({
                    "Cantidad": str(p["quantity"]),
                    "ClaveProdServ": p["code"],
                    "ClaveUnidad": p["clave_uni"],
                    "Descripcion": p["name"],
                    "Descuento": "0",#"22500.00",
                    "Importe": "{:.2f}".format(p["cost"] * p["quantity"]),
                    #"NoIdentificacion":"0001",
                    "Unidad": "No aplica",
                    "ValorUnitario": "{:.2f}".format(p["cost"]),
                    "ObjetoImp": "02",
                    "tax":{
                        "Traslado": {
                            "Base": "{:.2f}".format(p["cost"] * p["quantity"]),
                            "Importe": "{:.2f}".format(p["tax"] * p["quantity"]),
                            "Impuesto": "002",
                            "TasaOCuota": "0."+str(p["tax_value"] if p["tax_value"] > 0 else "00")+"0000",
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
                })
 

            #print(concepto)
            #print(total, sub_total, tax)
            emisor = {
                "Rfc": _invoice.branch.company.documentI,
                "Nombre": _invoice.branch.company.name,
                "RegimenFiscal": _invoice.branch.company.type_regime.code
            }
            #print(_invoice_data)
            #print(_invoice_data["data"]["uso_cfdi"])
            receptor = {
                "Rfc": _invoice.customer.identification_number,
                "Nombre": _invoice.customer.name,
                "UsoCFDI": _invoice_data["data"]["uso_cfdi"]["code"],
                "RegimenFiscalReceptor": _invoice.customer.type_regime.code,
                "DomicilioFiscalReceptor": _invoice.customer.address.split(",")[0]
            }
            #print(_invoice_data["data"]["customer"]["payment_form"])
            TipoDeComprobante = "E" # ingresos e ingresos de traslado.
            #print(receptor)
            comprobante = {
                "Folio": str(_invoice.number),
                "Fecha": (datetime.now() - dt.timedelta(hours=1)).replace(microsecond=0).isoformat('T'),
                "SubTotal": "{:.2f}".format(sub_total),
                "Total": "{:.2f}".format(total),
                "Moneda": "MXN",
                "TipoDeComprobante": TipoDeComprobante,
                "LugarExpedicion": _invoice.branch.company.address.split(",")[0],
                "FormaPago": _invoice_data["data"]["payment_form_data"]["_id"],
                "Serie": str(_invoice.prefix),
                "MetodoPago": _invoice_data["data"]["payment_method_data"]["code"],
                "Exportacion": "01",
                "tax": {
                    "TotalImpuestosRetenidos": "40.00",
                    "TotalImpuestosTrasladados": "{:.2f}".format(tax),
                    "Retencion": {
                        "Importe": "40.00",
                        "Impuesto": "002"
                    },
                    "Traslado": {
                        "Importe": "{:.2f}".format(tax),
                        "Base": "{:.2f}".format(sub_total),
                        "Impuesto": "002",
                        "TasaOCuota": "0."+str(tax_porcent if tax_porcent > 0 else "00")+"0000",
                        "TipoFactor": "Tasa"
                    }
                }
            }
            comprobante["DocRel"] = []
            for dc in CreditNote.objects.filter(nc_to_invoice = NcToInvoice.objects.filter(invoice = _invoice).first()):
                comprobante["DocRel"].append(dc.invoice.UUID)
            #print(comprobante["DocRel"])
            instancia = crear_cadena40(
                emisor=emisor, 
                receptor=receptor, 
                comprobante=comprobante, 
                concepto=concepto, 
                path_cert=str(_invoice.branch.company.cer_file), 
                type_document=_invoice.type_document, 
                period=None
            )
            result = instancia.createXMLCreditNote()
            _invoice.no_cert_dig = result["no_cert"]
            _invoice.cadena_original = result["cadena_original"]
            _invoice.save()
            
            result = {
               "status": "OK",
               "code": 200,
               "Message": "Success"
            }
        else:
            result = {
                "status": "Fail",
                "code": 400,
                "Message": _invoice.state
            }
        return result

    def sign_cancel(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        serial = _invoice.no_cert_dig
        uuid = _invoice.UUID
        rfc = _invoice.branch.company.documentI
        folio_sustitucion = ''
        motivo = data["motivo"]
        _invoice.reason_cancel = MotivoCancel.objects.filter(code = motivo).first()
        _invoice.save()
        
        if not os.path.exists(self.PATH_ACUSES2_CANCELACION):
            os.makedirs(self.PATH_ACUSES2_CANCELACION)
        
        history = HistoryPlugin()
        cliente = Client(wsdl=self.url+"/cancel.wsdl", plugins=[history])
        
        uuids_factory = cliente.get_type('ns0:UUID')
        uuids_obj = uuids_factory(uuid, folio_sustitucion, motivo)
        #print(uuids_obj)
        uuids_array_factory = cliente.get_type('ns0:UUIDArray')
        uuids_array_obj = uuids_array_factory([uuids_obj])
        
        response = cliente.service.sign_cancel(
            uuids_array_obj,
            self.username,
            self.password,
            rfc,
            serial,
            store_pending=False
        )
        
        if response['Acuse'] is not None:
            if 'Folios' in response and 'Folio' in response['Folios']:
                for folio in response['Folios']['Folio']:

                    _invoice.state = response['Folios']['Folio'][0]["EstatusCancelacion"]
                    _invoice.save()

                    ruta = '{}/{}.xml'.format(self.PATH_ACUSES2_CANCELACION, uuid)
                    #print(ruta)
                    with open(ruta, 'w+') as acuse_file:
                        acuse_file.write(response['Acuse'])
        
        #print(response)

        try:
            r = self.get_sat_status(data)
            _invoice.state = r["sat"]["Estado"]
            _invoice.state_invoice = r["sat"]["Estado"]
            _invoice.save()
            print(r)
        except Exception as e:
            print("Error in get status: "+str(e))
        result = {
                "status": "OK",
                "code": 200,
                "Message": "",
                "data":{
                    'Folios': {
                        'Folio': [
                            {
                                'UUID': response['Folios']['Folio'][0]["UUID"],
                                'EstatusUUID': response['Folios']['Folio'][0]["EstatusUUID"],
                                'EstatusCancelacion': response['Folios']['Folio'][0]["EstatusCancelacion"]
                            }
                        ]
                    },
                    'Acuse': response['Acuse'],
                    'Fecha': response['Fecha'],
                    'RfcEmisor': response['RfcEmisor'],
                    'CodEstatus': response['CodEstatus']
                }
            }
        return result
    
    def get_sat_status(self, data):
        _invoice = Invoice.objects.filter(pk = data["pk_invoice"]).first()
        taxpayer_id=_invoice.branch.company.documentI#'EKU9003173C9'# El rfc emisor de las facturas a consultar Tipo String 
        rtaxpayer_id=_invoice.customer.identification_number#'ZACA6812246G1' #El rfc receptorde los CFDI a consultar Tipo String
        uuid=_invoice.UUID#'F4EF7B8E-476D-4CD5-AAA7-8934A04574C2' # El UUID del CFDI a consultar  Tipo Sring
        total=_invoice.total#'466.51' # El valor del aributo total del CFDI
        
        history = HistoryPlugin()
        client = Client(wsdl = self.url+"/cancel.wsdl", plugins = [history])#location=url
        
        contenido =  client.service.get_sat_status(self.username, self.password, taxpayer_id, rtaxpayer_id, uuid, total)
        #print(contenido)
        return {
            'error': contenido["error"],
            'sat': {
                'DetallesValidacionEFOS': contenido["sat"]["DetallesValidacionEFOS"],
                'EsCancelable': contenido["sat"]["EsCancelable"],
                'ValidacionEFOS': contenido["sat"]["ValidacionEFOS"],
                'CodigoEstatus': contenido["sat"]["CodigoEstatus"],
                'Estado': contenido["sat"]["Estado"],
                'EstatusCancelacion': contenido["sat"]["EstatusCancelacion"]
            }
        }

    def generate_xml_by_json(self, data):
        emisor = {
            "Rfc":"EKU9003173C9",
            "Nombre":"ESCUELA KEMPER URGATE",
            "RegimenFiscal":"601"
        }
        receptor = {
            "Rfc":"ICV060329BY0",
            "Nombre":"INMOBILIARIA CVA",
            "UsoCFDI":"G03",
            "RegimenFiscalReceptor":"601",
            "DomicilioFiscalReceptor":"33826"
        }
        comprobante = {
            "Folio":"1",
            "Fecha":(datetime.now() - dt.timedelta(hours=1)).replace(microsecond=0).isoformat('T'),
            "SubTotal":"1000.00",
            "Total":"1120.00",
            "Moneda":"MXN",
            "TipoDeComprobante":"I",
            "LugarExpedicion":"58000",
            "FormaPago":"99",
            "Serie":"A",
            "MetodoPago":"PPD",
            "Exportacion":"01"
        }
        instancia = crear_cadena40(emisor=data["emisor"], receptor=data["receptor"], comprobante=data["comprobante"])
        response = instancia.creacionXML()
        return response

    def generate_xml_by_str(self, xml_string, name_file):
        # Analizar la cadena XML
        root = ET.fromstring(xml_string)

        # Escribir la estructura XML en un archivo
        tree = ET.ElementTree(root)
        tree.write(self.timbre_path+name_file)

if __name__ == "__main__":
    finkok = FinkokService("EKU9003173C9")
    #finkok.assign_register_client(10)
    #data = finkok.update_register_client("A")
    #data = finkok.get_register_client()
    #print(data)
    #finkok.register_client()
    data = finkok.sing_stamp()
    print(data)
    #finkok.stamp()