from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from inspect import currentframe
from inspect import getframeinfo
from logger import LOGGER
import inspect
import smtplib
import sys


def send_email(recipients, body, subject="Test Email", to="frank zappulla"):
    msg = MIMEMultipart()
    # Who recipient(s) will see the email is from
    msg["From"] = "JAX Archiver <noreply-archiver@jax.org>"
    # Who the recipient(s) visually see the email is addressed to
    msg["To"] = to
    # Text in subject line
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    msg_text = msg.as_string()
    try:
        with smtplib.SMTP("smtp.jax.org", 25) as server:
            # 1st arg overwritten by msg["From"] above
            # 2nd arg is list of recipients and who actually receives the email
            # 3rd arg body of email
            # result will return an empty dict when server does not refuse any
            # recipient. Returns dict of refused emails otherwise
            result = server.sendmail("return-email@jax.org", recipients, msg_text)
            if result:
                err_msg = f"ERROR: The following recipients were refused, {result}"
                LOGGER.error(err_msg)
                sys.stderr.write(err_msg)
    except Exception as e:
        LOGGER.error(f"error sending email: {e}")
        pass


def log_email(msg, error=False):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = getframeinfo(currentframe()).filename
    lineno = inspect.currentframe().f_back.f_lineno
    log_prefix = f"[{ts}, {filename}:{lineno}, "
    log_prefix += "ERROR]" if error else "INFO]"
    log_msg = f"{log_prefix} {msg}"
    if error:
        sys.stderr.write(f"{log_msg}\n")
        # send_email(
        #     config.err_email_list,
        #     body,
        #     subject="Archiver Error",
        #     to="Data-Services@jax.org",
        # )
        LOGGER.error(log_msg)
    else:
        LOGGER.info(log_msg)
    print(log_msg)
    return
