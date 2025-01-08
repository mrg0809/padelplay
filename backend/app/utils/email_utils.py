import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException

def send_email(recipient_email: str, subject: str, body: str):
    """
    Envía un correo electrónico utilizando un servidor SMTP.

    Args:
        recipient_email (str): Dirección de correo electrónico del destinatario.
        subject (str): Asunto del correo.
        body (str): Contenido del correo.

    Raises:
        HTTPException: Si ocurre algún error al enviar el correo.
    """
    try:
        # Configuración del correo
        sender_email = "info@padelplay.mx"
        sender_password = "PadelPla@y2025"
        smtp_server = "smtp.zoho.com"
        smtp_port = 587

        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Conexión al servidor SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()

        print(f"Correo enviado exitosamente a {recipient_email}")

    except Exception as e:
        print(f"Error al enviar el correo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se pudo enviar el correo a {recipient_email}.")
    

def send_match_invitation_email(recipient_email, data):
    subject = f"{data.player_name} Te han invitado a un partido: "
    body = f"""
    Hola,

    Has sido invitado a participar en el club "{data.club_name}" a un partido
    el dia {data.match_date} a las {data.match_time}
    Para unirte, regístrate en nuestra plataforma a través del siguiente enlace:

    [ENLACE A TU SITIO DE REGISTRO]

    ¡Esperamos verte pronto!

    Saludos,
    El equipo de PadelPlay.
    """
    send_email(recipient_email, subject, body)


def send_tournament_invitation_email(recipient_email):
    subject = f"Te han invitado a un torneo: {recipient_email}"
    body = f"""
    Hola,

    Has sido invitado a participar en el torneo "{recipient_email}".
    Para unirte, regístrate en nuestra plataforma a través del siguiente enlace:

    [ENLACE A TU SITIO DE REGISTRO]

    ¡Esperamos verte pronto!

    Saludos,
    El equipo de PadelPlay.
    """
    send_email(recipient_email, subject, body)
