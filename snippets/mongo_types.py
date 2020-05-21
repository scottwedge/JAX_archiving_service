'''
Reports types (only descending one level right now) of fields in records of
one mongodb collection. Gets mongodb info from ../config.py
'''

import os
import sys
import pymongo
import urllib.parse

## sleight of hand to import config from parent without making module:
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

mongo_host = config.mongo['host']
mongo_port = config.mongo['port']
mongo_user = config.mongo['user']
mongo_passwd = config.mongo['passwd']
mongo_user_db = config.mongo['authdb']       ## the authentication database for mongo_user
database = config.mongo['db']                ## the database where we will write records
collection = config.mongo['collection']      ## the collection where we will write records


## Set up client:
##   normally you can set up the client in one spot and pass around;
##   alternatively, you can combine several steps in a single try;
##   several exception types can be thrown, and you can separate out handling
##     of each type, but usually generic exception handling like below is ok:
try:
    user = urllib.parse.quote_plus(mongo_user)       ## percent-escape string
    passwd = urllib.parse.quote_plus(mongo_passwd)   ## percent-escape string
    uri = f"mongodb://{user}:{passwd}@{mongo_host}:{mongo_port}"
    client = pymongo.MongoClient(uri, authSource=mongo_user_db)
    client.admin.command('ismaster')      ## tests for client != None and good connection
except Exception as e:
    sys.stderr.write(f"ERROR: could not connect to '{mongo_host}:{mongo_port}': {e}\n")
    sys.exit(3)

## Connect to database and collection:
##   normally you can set up the collection object in one spot and pass around:
try:
    db = client[database]
    col = db[collection]
except Exception as e:
    sys.stderr.write(f"ERROR: could not select collection '{database}.{collection}': {e}\n")
    sys.exit(4)

try:
    curs = col.find({})
    for rec in curs:
        for key in rec:
            print(f"type({key}): {type(rec[key])}")
            if isinstance(rec[key], dict):
                for key2 in rec[key]:
                    print(f"    type({key2}): {type(rec[key][key2])}")
            if isinstance(rec[key], list):
                for val in rec[key]:
                    print(f"    type of list element: {type(val)}")
        input("press <ENTER> to continue:")
        print()
except Exception as e:
    sys.stderr.write(f"ERROR: find() failed: {e}\n")
    sys.exit(5)

sys.exit(0)


