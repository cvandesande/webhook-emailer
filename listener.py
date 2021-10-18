"""Modules for E-mail, Web & logging"""
import smtplib
import logging
from flask import Flask,request
from waitress import serve

# Logging with timestamps
logging.basicConfig(
    format='%(asctime)s %(levelname)-4s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Flask(__name__)

@app.route("/healthcheck")
def healthcheck():
    """Kubernetes healthcheck"""
    return {"pong": True}, 200

@app.route('/notify', methods=['POST'])
def notify():
    """Log and store webhook payload json as dict"""
    cf_ip = request.environ.get('HTTP_CF_CONNECTING_IP')
    if not cf_ip:
        logging.info("Notification received from: %s", request.remote_addr)
    else:
        logging.info("Notification received from: %s", cf_ip)
    payload    = request.get_json()
    recipient  = payload['event-data']['recipient']
    severity   = payload['event-data']['severity']
    sender     = payload['event-data']['envelope']['sender']
    status_msg = payload['event-data']['delivery-status']['message']
    subject    = payload['event-data']['message']['headers']['subject']
    logging.debug("Payload: %s", payload)
    sendmsg(sender, recipient, subject, severity, status_msg)
    return {"success": True}, 200

def sendmsg(mail_sender, mail_recipient, mail_subj, mail_severity, mail_status):
    """Build and send event e-mail"""
    # E-mail settings
    mail_server = "mail.example.com"
    mail_port = 25
    mail_from = "postmaster@example.com"
    mail_header = 'To:' \
      + mail_sender \
      + '\n' \
      + 'From:' \
      + mail_from \
      + '\n' \
      + 'Subject:' \
      + mail_severity \
      + ' error' \
      + '\n'''
    if mail_severity == 'permanent':
        mail_msg = mail_header \
        + 'Delivery failed to: ' \
        + mail_recipient \
        + '\n' \
        + 'Subject: ' \
        + mail_subj \
        + '\n' \
        + 'The receiving server reported: ' \
        + '\n' \
        + mail_status \
        + '\n' \
        + 'This is a permanent failure, please check the email ' \
        + 'address or contact postmaster@opendmz.com.'
    elif mail_severity == 'temporary':
        mail_msg = mail_header \
        + 'Delayed delivery to: ' \
        + mail_recipient \
        + '\n' \
        + 'Subject: ' \
        + mail_subj \
        + '\n' \
        + 'The receiving server reported: ' \
        + '\n' \
        + mail_status \
        + '\n' \
        + 'As this is a temporary error, we will keep trying to ' \
        + 'deliver your message.'
    else:
        logging.error("Unexpected severity in payload")
    smtp = smtplib.SMTP(mail_server, mail_port)
    #smtp.set_debug:level(1)
    smtp.sendmail(mail_from, mail_sender, mail_msg)
    smtp.quit()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)
