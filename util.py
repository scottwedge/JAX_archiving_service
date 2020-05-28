# unconditional global imports:
import sys
import datetime
import pytz
import inspect
import smtplib
import subprocess
from bson.objectid import ObjectId
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# unconditional local imports:
import config
from logger import LOGGER


def get_timestamp(format=config.time["format_sec"], zone=config.time["zone"]):
    """
    Returns a timestamp (str) with the current time.
    Argument(s):
      format: time format str
      zone: time zone str
    Value: str containing the current datetime
    """

    zone = pytz.timezone(zone)
    ts = zone.localize(datetime.datetime.now())
    return ts.strftime(format)


def send_email(recipients, body, subject="Test Email", to="frank zappulla"):
    msg = MIMEMultipart()
    # Who recipient(s) will see the email is from
    msg["From"] = "JAX Archiver <noreply-archiver@jax.org>"
    # Who the recipient(s) visually see the email is addressed to
    msg["To"] = to
    # Text in subject line
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    msg_txt = msg.as_string()
    try:
        with smtplib.SMTP("smtp.jax.org", 25) as svr:
            # 1st arg overwritten by msg["From"] above
            # 2nd arg is list of recipients and who actually receives the email
            # 3rd arg body of email
            # result will return an empty dict when server does not refuse any
            # recipient. Returns dict of refused emails otherwise
            result = svr.sendmail("return-email@jax.org", recipients, msg_txt)
            if result:
                err_msg = f"ERROR: The following recipients were refused, "
                +"{result}"
                LOGGER.error(err_msg)
                sys.stderr.write(err_msg)
    except Exception as e:
        LOGGER.error(f"error sending email: {e}")
        pass


def gen_msg(msg, error=True):

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    frame = inspect.currentframe()
    filename = inspect.getframeinfo(frame).filename.split("/")[-1]
    lineno = frame.f_back.f_lineno
    prefix = f"[{ts}, {filename}:{lineno}, "
    prefix += "ERROR]" if error else "INFO]"
    return f"{prefix} {msg}"


def log_email(msg, error=False):

    if error:
        sys.stderr.write(f"{msg}\n")
        # send_email(
        #     config.err_email_list,
        #     body,
        #     subject="Archiver Error",
        #     to="Data-Services@jax.org",
        # )
        LOGGER.error(msg)
    else:
        LOGGER.info(msg)
    print(msg)
    return


def get_api_user(args_dict):

    if not isinstance(args_dict, dict):
        raise Exception(gen_msg("args_dict is not a dict."))

    if "api_key" not in args_dict:
        raise Exception(gen_msg("no api key present; unauthorized request."))
    api_key = args_dict.get("api_key")

    user_info = config.api_keys.get(api_key)
    if not user_info:
        raise Exception(gen_msg("invalid api_key"))
    else:
        # log the authenticated key and delete from args
        log_email(f"api_key: '{api_key}' authenticated.")
        del args_dict["api_key"]

    try:
        groups_string = subprocess.getoutput(f"id -Gn {user_info['userid']}")
        groups_list = groups_string.split()
    except Exception as e:
        raise Exception(gen_msg(f"could not get groups: {e}"))

    user_info["groups_list"] = groups_list
    return user_info


def process_key(key, mydict):
    symbols = ["$", "."]
    replaced = False
    for symbol in symbols:
        if symbol in key:
            log_email(f"Illegal char found, removing {symbol} from {key}")
            new_key = key.replace(symbol, "")
            replaced = True
    if replaced:
        mydict[new_key] = mydict[key]
        del mydict[key]
    return mydict


def scrub_dict_keys(dictionary):
    for k, v in dictionary.items():
        process_key(k, dictionary)
        if isinstance(v, dict):
            scrub_dict_keys(v)
    return dictionary


def add_current_user(user: dict, obj_id: str, collection):
    query = {"_id": ObjectId(obj_id)}
    new_val = {"$set": {"current_user": user}}
    result = collection.update_one(query, new_val)
    assert result.acknowledged
    return result.modified_count
