import poplib
import imaplib
import smtplib
import email
import pickle
import time

SLEEP = 10
SLEEP_LONG = 120
SUBJECT = 'Confirm your email address'
HIER_EMAIL = 'Accounts <accounts@honorable-diligent-serval.anvil.app>'
MY_EMAIL = "jessime.kirk@gmail.com"
PASSWORD = "what is the problem"
BODY_BASE = ('Thanks for trying out Hier!\n\n'
             'Click the link below to confirm your email address:\n\n'
             '{}\n\n'
             'Cheers,\n'
             'Jessime and Kimiko\n\n'
             'P.S. If you have any questions, '
             'feel free to respond to this email.'
)
ALREADY_EMAILED_PATH = 'already_emailed.pkl'

def send_mail(confirmation_link, new_user_email):
    body = BODY_BASE.format(confirmation_link)
    content = 'Subject: %s\n\n%s' % (SUBJECT, body)
    mail = smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    mail.login(MY_EMAIL, PASSWORD)
    mail.sendmail(MY_EMAIL, new_user_email, content)
    mail.close()


def is_confirmation_email(msg):
    good_sender = msg['From'] == HIER_EMAIL
    good_subject = msg['Subject'] == SUBJECT
    return good_sender and good_subject


def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    else:
        body = msg.get_payload(decode=True)
    return body


def parse_body(body):
    body_lines = body.decode('utf-8').splitlines()
    new_user_email = body_lines[0].split('\'')[1]
    confirmation_link = body_lines[6]
    return confirmation_link, new_user_email

def forward_email(message_server, already_emailed):
    stat, count = message_server.select('Inbox')
    stat, content = message_server.fetch(count[0], '(RFC822)')
    mail = content[0][1]
    msg = email.message_from_string(mail.decode('utf-8'))
    if is_confirmation_email(msg):
        body = get_email_body(msg)
        confirmation_link, new_user_email = parse_body(body)
        never_mailed = not new_user_email in already_emailed
        if never_mailed:
            send_mail(confirmation_link, new_user_email)
            return new_user_email


def main():
    message_server = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    message_server.login(MY_EMAIL, PASSWORD)
    already_emailed = pickle.load(open(ALREADY_EMAILED_PATH, 'rb'))
    while True:
        try:
            new_user_email = forward_email(message_server, already_emailed)
            if new_user_email is not None:
                print(f'Forwarded to {new_user_email}')
                already_emailed.add(new_user_email)
                print(already_emailed)
            time.sleep(SLEEP)
            now = time.strftime("%Y-%m-%d %I:%M:%S")
            print(f'Alive at: {now}')
        except KeyboardInterrupt:
            pickle.dump(already_emailed, open(ALREADY_EMAILED_PATH, 'wb'))
            print('Stopping.')
            break
    message_server.close()
    message_server.logout()

if __name__ == '__main__':
    while True:
        try:
            print('Starting up.')
            main()
        except KeyboardInterrupt:
            break
        except:
            print('Crashed. Taking a break then trying again.')
            time.sleep(SLEEP_LONG)
