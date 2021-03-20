import os
import smtplib
import pathlib
import confply.log as log
import email.mime.text as mime_text
import email.mime.multipart as mime_multipart
import email.mime.application as mime_application

attachments = []
sender = None
recipients = []
login = None
host = "smtp.gmail.com"


def send_report(report):
    html_file = os.path.dirname(__file__)
    html_file = os.path.join(html_file, "mail.html")
    message = mime_multipart.MIMEMultipart('html')
    message["Subject"] = (pathlib.Path(report["vcs_root"]).name +
                          ": " + report["config_path"])
    message["From"] = sender
    message["To"] = recipients

    with open(html_file) as mail_file:
        message_str = mail_file.read()

        for key, val in report.items():
            message_str = message_str.replace("{"+key+"}", str(val))

        message_mime = mime_text.MIMEText(message_str, 'html')
        message.attach(message_mime)
        for f in attachments:
            if f is None or (not os.path.exists(f)):
                log.error("failed to send attachment: "+str(f))
                continue
            with open(f, "rb") as fil:
                part = mime_application.MIMEApplication(
                    fil.read(),
                    Name=os.path.basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = (
                'attachment; filename="%s"'
                % os.path.basename(f)
            )
            message.attach(part)

    if login:
        try:
            server = smtplib.SMTP_SSL(host)
            server.ehlo()
            server.login(*login)
            server.send_message(message)
            server.quit()
        except:
            log.error("failed to send mail")
