## unconditional global imports:
import sys
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from inspect import currentframe
from inspect import getframeinfo
from logger import LOGGER
import inspect
import smtplib
import sys

## unconditional local imports:
import config

## imports conditional on config:
if config.testing['email_on']: 
    import pymongo
else: 
    import mocks.pymongo_mock
    

def get_mongo_client():

    try:
        user = urllib.parse.quote_plus(config.mongo.get('user'))       ## percent-escape string
        passwd = urllib.parse.quote_plus(config.mongo.get('passwd'))   ## percent-escape string
        host = config.mongo.get('host')
        port = config.mongo.get('port')
        uri = f"mongodb://{user}:{passwd}@{host}:{port}"
        client_obj = pymongo.MongoClient(uri, authSource=config.mongo.get('authdb'))
        client_obj.admin.command('ismaster')      ## tests for client != None and good connection
    except Exception as e:
        log_email(f"ERROR: could not connect to '{host}:{port}': {e}")
        return None

    return client_obj

def get_mongo_collection(client_obj=None, database_name=config.mongo.get('db'), collection_name=config.mongo.get('collection')):

    if not isinstance(client_obj, pymongo.mongo_client.MongoClient):
        client_obj = get_mongo_client()
        if not client_obj:
            log_email(f"ERROR: get_mongo_client() failed.")
            return None

    try: 
        db_obj = client_obj[database_name]
        collection_obj = db_obj[collection_name]
    except Exception as e:
        log_email(f"ERROR: could not connect to collection '{database_name}.{collection_name}': {e}")
        return None

    return collection_obj
  

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

