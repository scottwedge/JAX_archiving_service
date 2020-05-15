## unconditional global imports:
import sys
import urllib.parse

## unconditional local imports:
import config

## imports conditional on config:
if config.testing['email_on']: 
    import pymongo
else: 
    import mocks.pymongo_mock

def log_email(msg, error=True):

    if error: 
        sys.stderr.write(f"{msg}\n")
        ## add emailing here
    else:
        print(msg)
    return None

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

