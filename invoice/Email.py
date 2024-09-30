from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
import smtplib
import email.message
from email import encoders

def send(Email_send, Password, Email_receiver, Affair, Text, Text_html, path, name_file, name_file2, host, port):

	msg = MIMEMultipart()

	#mensaje=texto			#mensaje de el correo

	#password = Passw						#contraseña
	msg['From'] = Email_send				#correo para el logeo
	msg['To'] = Email_receiver				#correoa quien se envia
	msg['Subject'] = Affair					#asunto de el envio de correo
	#msg.add_header('Content-Type', 'text/html')
	#msg.set_payload(Text_html)
	msg.attach(MIMEText(Text, 'plain'))	#carga de texto
	# attach image to message body
	#try:
	#	file = open(name_file, "rb")
	#	msg.attach(MIMEImage(file.read()))
	#except:
	#	pass
	# Abrimos el archivo que vamos a adjuntar
	status_flie1 = True
	status_flie2 = True
	try:
		print(path+name_file)
		archivo_adjunto = open(path+name_file, 'rb')
		adjunto_MIME = MIMEBase('application', 'octet-stream')
		adjunto_MIME.set_payload((archivo_adjunto).read())
		encoders.encode_base64(adjunto_MIME)
		adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % name_file)
		msg.attach(adjunto_MIME)
	except Exception as e:
		#print("Error exception file1: "+str(e))
		status_flie1 = False
	try:
		archivo_adjunto = open(path+name_file2, 'rb')
		adjunto_MIME = MIMEBase('application', 'octet-stream')
		adjunto_MIME.set_payload((archivo_adjunto).read())
		encoders.encode_base64(adjunto_MIME)
		adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % name_file2)
		msg.attach(adjunto_MIME)
	except Exception as e2:
		#print("Error exception file2: "+str(e2))
		status_flie2 = False
	
	if status_flie1 or status_flie2:
		server=smtplib.SMTP('smtp.gmail.com: 587')
		server.starttls()
		server.login(msg['From'],Password)
		server.sendmail(msg['From'],msg['To'],msg.as_string())
		server.quit()
		print("correo fue enviado con exito a %s:" % (msg['To']))

def send_notification(Email_send, Password, Email_receiver, Affair, Text, Text_html):
  pass

if __name__ == "__main__":
	send("streaming2053@gmail.com", "ulznhmzddcafttra", "wilson121yer@gmail.com", "prueba","prueba","", "C:/Users/WuilsonPc/Desktop/progra/gestionafacil/api/media/timbres", "IIA040805DZ4SETP990000539.pdf", "IIA040805DZ4SETP990000539.xml")
	