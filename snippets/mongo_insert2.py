'''
Inserts sample records into mongodb. Gets mongo information from ../config.py.
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

## test data:

docs = [
    {
        "managerUserId": "pi1",
        "userId": "postdoc1",
        "projectName": "Project 1",
        "classification": "Secret",
        "grant_id": "NA",
        "notes": "Notes 1",
        "request_type": "faculty",
        "system_groups": ["jaxuser", "postdoc1", "pi1"],
        "submitter": {
            "fname": "post",
            "lname": "doc1",
            "username": "pdoc",
            "group": "science-lab1",
            "email": "post.doc@jax.org"
        },
        "archivedPath": "/archive/faculty/pi-lab/postdoc/2019-12-31/NPP1",
        "sourceFolderPath": "/tier2/pi-lab/postdoc/postdoc_NPP1",
        "ready_for_submit": False,
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": None,
        "when_archival_completed": None,
        "failed_multiple": None,
        "archival_status": "queued",
        "user_metadata": {"key1": "val1", "key2": "val2"}
    },
    {
        "managerUserId": "pi2",
        "userId": "postdoc2",
        "projectName": "Project 2",
        "classification": "Top Secret",
        "grant_id": "acbd",
        "notes": "Notes 2",
        "request_type": "faculty",
        "system_groups": ["postdoc2", "pi2"],
        "submitter": {
            "fname": "post",
            "lname": "doc2",
            "username": "pdoc2",
            "group": "science-lab2",
            "email": "post.doc2@jax.org"
        },
        "archivedPath": "/archive/faculty/pi2-lab/postdoc2/2019-1-31/NPP2",
        "sourceFolderPath": "/tier2/pi2-lab/postdoc2/postdoc2_NPP2",
        "ready_for_submit": False,
        "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
        "when_archival_started": None,
        "when_archival_completed": None,
        "failed_multiple": None,
        "archival_status": "queued",
        "user_metadata": {"key3": "val3"}
    },
    {
        "managerUserId": "pi3",
        "userId": "postdoc3",
        "projectName": "Project 3",
        "classification": "NA",
        "grant_id": "NA",
        "notes": "Notes 3",
        "request_type": "faculty",
        "system_groups": ["pi3"],
        "submitter": {
            "fname": "post",
            "lname": "doc3",
            "username": "pdoc3",
            "group": "science-lab3",
            "email": "post.doc3@jax.org"
        },
        "archivedPath": "/archive/faculty/pi3-lab/postdoc3/2019-02-01/NPP3",
        "sourceFolderPath": "/tier2/pi3-lab/postdoc3/postdoc3_NPP3",
        "ready_for_submit": False,
        "when_archival_queued": "2019-02-01 21:01:01 EDT-0400",
        "when_archival_started": None,
        "when_archival_completed": None,
        "failed_multiple": None,
        "archival_status": "queued",
        "user_metadata": {}
    },
]

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

## The actual insertion; you can also insert a single record as a dictionary (instead
##   of as a list of dictionaries), by calling 'insert_one', then get single _id w/
##   result.inserted_id (instead of inserted_ids):
try: 
    result = col.insert_many(docs)
    if not result.acknowledged:
        raise Exception(f"ERROR: insertion not acknowledged.")
except Exception as e:
    sys.stderr.write(f"ERROR: could not write records to '{database}.{collection}': {e}\n")
    sys.exit(5)

print(f"successfully inserted data; autogenerated _ids: '{result.inserted_ids}'\n")
sys.exit(0)

