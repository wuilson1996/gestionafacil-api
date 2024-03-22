from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.safestring import mark_safe
import env, json, requests, pandas as pd, os

class AuthenticationUser:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Create_Employee(self,data):
		response = requests.request("POST", env.CREATE_EMPLOYEE, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Query_Permissions(self):
		change = True
		response = requests.request("GET", env.QUERY_PERMISSIONS, headers= self.headers, data=json.dumps({"pk_employee":self.request.session['pk_employee']}))
		values = json.loads(response.text)
		if values != self.request.session['permission']:
			change = False
		self.request.session['permission'] = values
		menu = mark_safe(env.HTML_MENU.replace('    ', '').replace('\t', ''))
		self.request.session['html'] = menu
		print(self.request.session['permission'])
		return json.dumps({'change':change,'html':menu})

	def Login(self):
		values = None
		try:
			payload = json.dumps(self.request.GET)
			response = requests.request("POST", env.LOGIN, headers=self.headers, data=payload)
			values = json.loads(response.text)
			self.request.session['pk_employee'] = values['pk_employee']
			self.request.session['name_employee'] = values['name']
			self.request.session['pk_branch'] = values['pk_branch']
			self.request.session['name_branch'] = values['name_branch']
			self.request.session['logo'] = values['logo']
			self.request.session['permission'] = values['permission']
			self.request.session['size_permission'] = len(values['permission'])
			self.request.session['html'] = ""
		except Exception as e:
			print(e)
		return json.dumps({'result': values['result'], 'message': values['message']})


	def Get_List_User(self):
		response = requests.request("GET", env.GET_LIST_EMPLOYEE, headers= self.headers, data=json.dumps({'pk_employee': self.request.session['pk_employee']}))
		return json.loads(response.text)

	def LogOut(self):
		response = requests.request("PUT", env.LOGOUT, headers= self.headers, data=json.dumps({'pk_employee': self.request.session['pk_employee']}))
		return json.loads(response.text)

	def Get_Employee(self,pk):
		response = requests.request("GET", env.GET_EMPLOYEE, headers= self.headers, data=json.dumps({'pk_employee': pk}))
		return json.loads(response.text)
	def Update_User(self, data):
		response = requests.request("PUT", env.UPDATE_USER, headers=self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Delelete_User(self,data):
		response = requests.request("DELETE", env.DELETE_USER, headers = self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Get_List_Email(self):
		response = requests.request("GET", env.GET_LIST_EMAIL, headers = self.headers, data=json.dumps({'pk_employee': self.request.session['pk_employee'], "pk_branch":self.request.session['pk_branch']}))
		return json.loads(response.text)

	def Get_All_Payroll_Employee(self, pk):
		response = requests.request("GET", env.GET_ALL_PAYROLL_EMPLOYEE, headers = self.headers, data=json.dumps({'pk_employee': pk}))
		return json.loads(response.text)

class Supplier:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def List_Supplier(self):
		payload = json.dumps({"pk_employee":self.request.session['pk_employee']})
		response = requests.request("GET", env.LIST_SUPPLIER, headers= self.headers, data=payload)
		return json.loads(response.text)

	def Create_Supplier(self):
		data = self.request.GET.copy()
		for i in data.keys():
			if data[i] == "":
				data[i] = None
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("POST", env.CREATE_SUPPLIER, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

	def Delete_Supplier(self):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("POST", env.DELETE_SUPPLIER, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

	def Get_Supplier(self, pk):
		response = requests.request("GET", env.GET_SUPPLIER, headers= self.headers, data=json.dumps({'pk_supplier':pk}))
		return json.loads(response.text)

	def Update_Supplier(self, data):
		response = requests.request("PUT", env.UPDATE_SUPPLIER, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

class Inventory:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Save_Transfer(self,data):
		response = requests.request("POST", env.SAVE_TRANSFER, headers= self.headers, data= json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Get_List_Products(self):
		response = requests.request("GET", env.GET_LIST_PRODUCTS, headers= self.headers, data=json.dumps({'pk_employee':self.request.session['pk_employee']}))
		return json.loads(response.text)

	def List_Branch(self):
		response = requests.request("GET", env.LIST_BRANCH, headers= self.headers, data=json.dumps({'pk_branch':self.request.session['pk_branch']}))
		return json.loads(response.text)

	def Return_Products(self):
		response = requests.request('POST',env.RETURN_PRODUCTS, headers= self.headers, data = json.dumps({'pk_user':self.request.session['pk_employee']}))

	def Return_Product_UNIQUE(self):
		response = requests.request('PUT',env.RETURN_PRODUCT_UNIQUE, headers= self.headers, data = json.dumps(self.request.GET))


	def Product_Reserved(self):
		data = self.request.GET
		payload = json.dumps({
		  "pk_user": self.request.session['pk_employee'],
		  "pk_product": data['pk_product'],
		  "quantity": data['quantity']
		})
		response = requests.request("POST", env.PRODUCT_RESERVED_USER, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

	def Create_Product(self, excel = 0):
		data = self.request.GET.copy()
		for i in data.keys():
			if data[i] == "":
				return json.dumps({'result':False, 'message':"No puede dejar ningun campo vacio"})
		data['pk_employee'] = self.request.session['pk_employee']
		data['excel'] = excel
		response = requests.request("POST", env.CREATE_PRODUCT, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Get_Category(self):
		response = requests.request("GET", env.GET_CATEGORY, headers= self.headers, data={})
		return json.loads(response.text)

	def Get_List_SubCategory(self):
		response = requests.request("POST", env.GET_SUBCATEGORY, headers= self.headers, data=json.dumps(self.request.GET))
		return json.dumps(json.loads(response.text))

	def Delete_Product(self):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		response = requests.request("DELETE", env.DELETE_PRODUCT, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Get_Product(self,code):
		payload = json.dumps({
		  "pk_employee": self.request.session['pk_employee'],
		  "code": code
		})
		response = requests.request("GET", env.GET_PRODUCT, headers= self.headers, data=payload)
		return json.loads(response.text)

	def Update_Product(self,data):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("PUT", env.UPDATE_PRODUCT, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

	def Get_List_Products_Supplier(self):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("GET", env.GET_LIST_PRODUCTS_SUPPLIER, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

class Shopping:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Verified_Invoice(self):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("GET", env.VERIFIED_INVOICE, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

	def Save_Shopping(self, data):
		data['pk_employee'] = self.request.session['pk_employee']
		payload = json.dumps(data)
		response = requests.request("POST", env.CREATE_SHOPPING, headers= self.headers, data=payload)
		return json.dumps(json.loads(response.text))

class Invoice:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Get_List_Invoice(self,type_invoice):
		payload = json.dumps({
			'pk_employee':self.request.session['pk_employee'],
			'type_document': int(type_invoice)
		})
		response = requests.request("GET", env.GET_LIST_INVOICE, headers= self.headers, data=payload)
		return json.loads(response.text)

	def Annulled_Invoice(self):
		data = self.request.GET.copy()
		data['pk_employee'] = self.request.session['pk_employee']
		response = requests.request("POST", env.ANNULLED_INVOICE, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Send_Invoice_DIAN(self):
		response = requests.request("POST", env.SEND_INVOICE_DIAN, headers = self.headers, data = json.dumps( {'pk_invoice':self.request.GET['pk_invoice'], 'type_document': self.request.session['type_document'] } ) )
		data = json.loads(response.text)
		return json.dumps(data['data'])


	def Get_Invoice(self, pk):
		response = requests.request("GET", env.GET_INVOICE, headers= self.headers, data=json.dumps({'pk_invoice':pk}))
		return json.loads(response.text)

	def Get_Selling_By_Invoice(self, type_document):
		response = requests.request("GET", env.GET_SELLING_BY_INVOICE, headers= self.headers, data=json.dumps({'pk_branch':self.request.session['pk_branch'], 'type_document':type_document}))
		return json.loads(response.text)

	def Get_Selling_By_Date(self, date):
		data = {
			'pk_branch':self.request.session['pk_branch'],
			'date_start':date['date_start']
		}
		response = requests.request("GET", env.GET_SELLING_BY_DATE, headers= self.headers, data=json.dumps(data))
		totals_prices = []
		for date, total in json.loads(response.text).items():
		    totals_prices.append({'date':total})
		return json.dumps(totals_prices)

	def Create_Invoice(self, data):
		response = requests.request("POST", env.CREATE_INVOICE, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Annulled_Invoice_By_Product(self):
		response = requests.request("POST", env.ANNULLED_INVOICE_BY_PRODUCT, headers= self.headers, data=json.dumps(self.request.GET))
		return json.dumps(json.loads(response.text))

	def Create_Pass_Invoice(self):
		response = requests.request("POST", env.CREATE_PASS_INVOICE, headers=self.headers, data= json.dumps(self.request.GET))
		return json.dumps(json.loads(response.text))

class Setting:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Get_Data(self, url):
		response = requests.request("GET", url, headers= self.headers, data={})
		return json.loads(response.text)

	def Get_Resolution(self,data):
		response = requests.request("GET", env.GET_RESOLUTION, headers= self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Get_Resolution_List(self):
		response = requests.request("GET", env.GET_RESOLUTION_LIST, headers= self.headers, data=json.dumps({'pk_branch':self.request.session['pk_branch']}))
		return json.loads(response.text)

	def Get_Branch(self):
		response = requests.request("GET", env.GET_BRANCH, headers= self.headers, data=json.dumps({'pk_branch':self.request.session['pk_branch']}))
		data = json.loads(response.text)
		self.request.session['logo'] = data['fields']['logo']
		return data

	def Update_Branch(self):
		data = self.request.GET.copy()
		data['pk_branch'] = self.request.session['pk_branch']
		response = requests.request("PUT", env.UPDATE_BRANCH, headers= self.headers, data = json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Update_Logo(self):
		response = requests.request("PUT", env.UPDATE_LOGO, headers= self.headers, data = json.dumps({'pk_branch': self.request.session['pk_branch'], 'logo': self.request.POST['img_base64']}))
		data = json.loads(response.text)
		self.request.session['logo'] = data['url_logo']
		return json.dumps(data)

	def Update_Resolution_DIAN(self, data):
		response = requests.request("PUT", env.UPDATE_RESOLUTION_DIAN, headers= self.headers, data=json.dumps({
																												  "pk_branch": self.request.session['pk_branch'],
																												  "type_document_id": data['type_document'],
																												  "resolution": data['resolution']
																												}))
		return json.dumps(json.loads(response.text))

class Customer:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Get_List_Customer(self):
		response = requests.request("GET", env.GET_LIST_CUSTOMER, headers=self.headers, data=json.dumps({"pk_employee": self.request.session['pk_employee']}))
		return json.loads(response.text)

	def Get_Customer(self,pk):
		response = requests.request("GET", env.GET_CUSTOMER, headers=self.headers, data=json.dumps({"pk_customer": pk}))
		return json.loads(response.text)

	def Update_Customer(self,data):
		response = requests.request("PUT", env.UPDATE_CUSTOMER, headers=self.headers, data=json.dumps(data))
		print(json.loads(response.text))
		return json.dumps(json.loads(response.text))

	def Create_Customer(self, data):
		response = requests.request("POST", env.CREATE_CUSTOMER, headers=self.headers, data=json.dumps(data))
		return json.dumps(json.loads(response.text))

	def Delete_Client(self):
		response = requests.request("DELETE", env.DELETE_CLIENT, headers=self.headers, data=json.dumps({"pk_customer": self.request.GET['pk_customer']}))
		return json.dumps(json.loads(response.text))

class Email:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Get_List_Emals(self):
		response = requests.request("GET", env.GET_LIST_EMAILS, headers=self.headers, data=json.dumps({"pk_employee": self.request.session['pk_employee']}))
		return json.loads(response.text)['data']

	def Get_List_Email_Sender(self):
		response = requests.request("GET", env.GET_LIST_EMAIL_SENDER, headers=self.headers, data=json.dumps({"pk_employee": self.request.session['pk_employee']}))
		return json.loads(response.text)['data']

	def Create_Email(self,data):
		response = requests.request("POST", env.CREATE_EMAIL, headers=self.headers, data=json.dumps(data))
		print(json.loads(response.text))
		return json.loads(response.text)

	def Get_Email(self,pk):
		response = requests.request("GET", env.GET_EMAIL, headers=self.headers, data=json.dumps({"pk_email": pk}))
		return json.loads(response.text)

	def Mark_As_Read(self,data):
		response = requests.request("PUT", env.MARK_AS_READ, headers=self.headers, data=json.dumps(data))
		return json.loads(response.text)

class Report:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Report_Invoices(self, type_document):
		response = requests.request("GET", env.REPORT_INVOICES, headers=self.headers, data=json.dumps({"pk_employee": self.request.session['pk_employee'], 'type_document':type_document}))
		return json.loads(response.text)

	def Get_List_Best_Selling_Product(self, data):
		payload = json.dumps({
		  "pk_branch": 46,
		  "start_date": "2023-01-30",
		  "end_date": "2024-01-30"
		})
		response = requests.request("GET", env.GET_LIST_BEST_SELLING_PRODUCT, headers= self.headers, data=payload)
		return json.loads(response.text)['data']

	def Get_All_List_Best_Selling_Product(self):
		response = requests.request("GET", env.GET_ALL_LIST_BEST_SELLING_PRODUCT, headers=self.headers, data=json.dumps({"pk_branch": self.request.session['pk_branch']}))
		return json.loads(response.text)['data']

	def Close_The_Box_All(self):
		print(self.request.GET)
		response = requests.request("GET", env.CLOSE_THE_BOX_ALL, headers=self.headers, data=json.dumps({ 
																											"pk_employee": self.request.session['pk_employee'], 
																											'date_start':self.request.GET['date_start'], 
																											'date_end':self.request.GET['date_end']
																										}))
		return json.loads(response.text)

	def Report_Invoice_Annulled(self, type_document):
		response = requests.request("GET", env.REPORT_INVOICE_ANNULLED, headers=self.headers, data=json.dumps({"pk_employee": self.request.session['pk_employee'], 'type_document':type_document}))
		return json.loads(response.text)


	def History_Inventory(self):
		result =False
		message = None
		name_file = None
		try:
			payload = json.dumps({
				'pk_employee': self.request.session['pk_employee'],
				'date_start': self.request.GET['date_start'],
				'date_end': self.request.GET['date_end']
				})
			response = requests.request("GET", env.HISTORY_INVENTORY, headers = self.headers, data = payload)
			relevant_data = []
			for i in json.loads(response.text)['data']:
				product_info = i['product']
				modified_values = i['modified_values']
				relevant_data.append({
					"Codigo":product_info['code'],
					"Producto":product_info['name'],
					"Fecha":i['timestamp'],
					"Cant. Ant":modified_values['quantity'],
					"precio_1. Ant":modified_values['price_1'],
					"precio_2. Ant":modified_values['price_2'],
					"precio_3. Ant":modified_values['price_3'],
					"Cant. Act":product_info['quantity'],
					"precio_1. Act":product_info['price_1'],
					"precio_2. Act":product_info['price_2'],
					"precio_3. Act":product_info['price_3'],
					"Empleado":f"{i['employee'][0]['fields']['first_name']} {i['employee'][0]['fields']['surname']}",
					"Usuario":f"{i['employee'][0]['fields']['user_name']}",
					"Accion":i['action'],
				})
			df = pd.DataFrame(relevant_data)
			path_dir =  f"{env.URL_FILES}{self.request.session['pk_branch']}"
			if not os.path.exists(path_dir):
				os.makedirs(path_dir)
			name_file = f'{path_dir}/datos_modificados.xlsx'
			partes = name_file.partition("invoice_new_evansoft")
			name_file = f"{env.URL_APPLICATION}{partes[2]}"
			print(name_file)
			df.to_excel(name_file, index=False)
			result = True
			message = "Success"
		except Exception as e:
			message = str(e)
		return json.dumps({'path_file':f'{name_file}', 'result':result, 'message':message})


class Payroll:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Basic_Payroll(self):
		data = json.dumps({
			'pk_employee': self.request.GET['pk_employee'],
			"worked_days": self.request.GET['worked_days'],
			"worked_time": 780,
			})

		response = requests.request("POST", env.BASIC_PAYROLL, headers = self.headers, data = data)
		return json.dumps(json.loads(response.text))

	def Delete_Payroll(self):
		response = requests.request("DELETE", env.DELETE_PAYROLL, headers=self.headers, data=json.dumps(self.request.GET))
		return json.dumps(json.loads(response.text))



class Wallet:
	def __init__(self,request):
		self.headers = {'Content-Type': 'application/json'}
		self.request = request

	def Get_Pass_Invoice(self):
		response = requests.request("GET", env.GET_PASS_INVOICE, headers = self.headers, data=json.dumps({'pk_branch': self.request.session['pk_branch']}))
		return json.loads(response.text)

	def Get_All_History_Pass_Invoice(self):
		response = requests.request("GET", env.GET_ALL_HISTORY_PASS_INVOICE, headers = self.headers, data=json.dumps({'pk_branch': self.request.session['pk_branch']}))
		return json.loads(response.text)

	def Get_All_History_Pass_Customer(self,identification_number):
		response = requests.request("GET", env.GET_ALL_HISTORY_PASS_CUSTOMER, headers = self.headers, data=json.dumps({'pk_branch': self.request.session['pk_branch'],'identification_number':identification_number}))
		return json.loads(response.text)


