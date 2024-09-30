from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import smtplib
import email.message

def send(Email_send, Password, Email_receiver, Affair, Text, Text_html, name_file, host, port):

	msg = email.message.Message()

	#mensaje=texto			#mensaje de el correo

	#password = Passw						#contraseña
	msg['From'] = Email_send				#correo para el logeo
	msg['To'] = Email_receiver				#correoa quien se envia
	msg['Subject'] = Affair					#asunto de el envio de correo
	msg.add_header('Content-Type', 'text/html')
	msg.set_payload(Text_html)
	#msg.attach(MIMEText(Text, 'plain'))	#carga de texto
	# attach image to message body
	try:
		file = open(name_file, "rb")
		msg.attach(MIMEImage(file.read()))
	except:
		pass
	server=smtplib.SMTP(host+': '+str(port))
	server.starttls()
	server.login(msg['From'],Password)
	server.sendmail(msg['From'],msg['To'],msg.as_string())
	server.quit()
	print("correo fue enviado con exito a %s:" % (msg['To']))

if __name__ == "__main__":
	send("streaming2053@gmail.com", "ulznhmzddcafttra", "wilson121yer@gmail.com", "prueba", "", "prueba", "", "smtp.gmail.com", "587")
	