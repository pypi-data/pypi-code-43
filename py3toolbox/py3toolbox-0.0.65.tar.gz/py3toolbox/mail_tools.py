import os
import sys
import re
import smtplib
import email  
import ssl

from email import encoders
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email.mime.image import MIMEImage
from email import encoders 

def send_gmail (sender_account, sender_password, smtp,smtp_port,senders,receivers,subject,body,attachments):
  msg               = MIMEMultipart()
  msg["From"]       = senders
  msg["To"]         = receivers
  msg["Subject"]    = subject
  
  msg.attach(MIMEText(body, 'plain'))

  for filename in attachments:
    with open(filename, 'rb') as fp:
      part = MIMEBase("application", "octet-stream")
      part.set_payload(fp.read())
    encoders.encode_base64(part)
    attachment_name = os.path.basename(filename)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={attachment_name}",
    )
    msg.attach(part)

  text = msg.as_string()


  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(smtp, smtp_port, context=context) as server:
    server.login(sender_account, sender_password)
    server.sendmail(senders, receivers, text)



if __name__ == "__main__":
  send_gmail('xxxxxx@gmail.com',
            'xxxxxx',
            'smtp.gmail.com', 
            465, 
            'xxxxx@gmail.com',
            'xxxxx@test.com',
            'System Monitor ' ,
            'blablabla',
            ["R:/car.jpg", "R:/car.rar", "R:/1.cat"]
            )
    