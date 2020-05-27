'''
Inserts sample records into mongodb. Gets mongo information from ../config.py.
'''

import os
import sys
import pymongo
import bson.objectid
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
        "_id": bson.objectid.ObjectId("5ec7cac93c9619864cc73e4a"),
        "current_user": {
            "fname": "Billy",
            "lname": "Tech1",
            "username": "tech1b",
            "email": "billy.tech1@jax.org"},
        "managerUserId": "pi1",
        "userId": "postdoc1",
        "projectName": "project 1",
        "classification": "class 1",
        "grant_id": "NA",
        "notes": "notes 1",
        "request_type": "faculty",
        "system_groups": ["jaxuser", "pi1", "postdoc1"],
        "submitter": {
            "fname": "post",
            "lname": "doc1",
            "username": "pdoc1",
            "email": "post.doc1@jax.org"},
        "archivedPath": "/archive/faculty/pi1-lab/postdoc1/2019-12-31/NPP1",
        "sourceFolderPath": "/tier2/pi1-lab/postdoc1/postdoc1_NPP",
        "archival_status": "completed",
        "submit_progress": [],
        "archivedSize": int(396700549),
        "dateArchived": "2020-01-01",
        "sourceSize": int(797725536),
        "user_metadata":{},
        "submission": {
            "job_id": "8638.ctarchive.jax.org",
            "when_ready_for_pbs": "2019-12-31 22:41:00 EDT-0400",
            "when_archival_queued": "2019-12-31 22:41:01 EDT-0400",
            "when_archival_started": "2019-12-31 22:44:08 EDT-0400",
            "when_archival_completed": "2020-01-01 03:01:59 EDT-0400" },
        "retrievals": [{
            "retrieval_status": "ready_for_pbs",
            "when_ready_for_pbs": "2020-01-02 07:34:38 EDT-0400",
            "when_retrieval_queued": None,
            "when_retrieval_started": None,
            "when_retrieval_completed": None }] 
    },
    {
        "_id": bson.objectid.ObjectId("5ec7cac93c9619864cc73e4b"),
        "current_user": {
            "fname": "Billy",
            "lname": "Tech2",
            "username": "tech2b",
            "email": "billy.tech2@jax.org"},
        "managerUserId": "pi2",
        "userId": "postdoc2",
        "projectName": "project 2",
        "classification": "class 2",
        "grant_id": "NA",
        "notes": "notes 2",
        "request_type": "faculty",
        "system_groups": ["pi2", "postdoc1"],
        "submitter": {
            "fname": "post",
            "lname": "doc2",
            "username": "pdoc2",
            "email": "post.doc2@jax.org"},
        "archivedPath": "/archive/faculty/pi2-lab/postdoc2/2019-01-31/NPP2",
        "sourceFolderPath": "/tier2/pi2-lab/postdoc2/postdoc2_NPP",
        "archival_status": "completed",
        "submit_progress": [],
        "archivedSize": int(396700550),
        "dateArchived": "2020-01-01",
        "sourceSize": int(797725547),
        "user_metadata":{},
        "submission": {
            "job_id": "8639.ctarchive.jax.org",
            "when_ready_for_pbs": "2019-01-31 22:41:00 EDT-0400",
            "when_archival_queued": "2019-01-31 22:41:01 EDT-0400",
            "when_archival_started": "2019-01-31 22:44:08 EDT-0400",
            "when_archival_completed": "2020-02-01 03:01:59 EDT-0400" },
        "retrievals": [{
            "retrieval_status": "ready_for_pbs",
            "when_ready_for_pbs": "2020-02-02 07:34:40 EDT-0400",
            "when_retrieval_queued": None,
            "when_retrieval_started": None,
            "when_retrieval_completed": None }]
    },
    {
        "_id": bson.objectid.ObjectId("5ec7cac93c9619864cc73e4c"),
        "current_user": {
            "fname": "Billy",
            "lname": "Tech3",
            "username": "tech3b",
            "email": "billy.tech3@jax.org"},
        "managerUserId": "pi3",
        "userId": "postdoc3",
        "projectName": "project 3",
        "classification": "class 3",
        "grant_id": "NA",
        "notes": "notes 3",
        "request_type": "faculty",
        "system_groups": ["jaxuser", "pi3", "postdoc3"],
        "submitter": {
            "fname": "post",
            "lname": "doc3",
            "username": "pdoc3",
            "email": "post.doc3@jax.org"},
        "archivedPath": "/archive/faculty/pi3-lab/postdoc3/2019-02-15/NPP3",
        "sourceFolderPath": "/tier2/pi3-lab/postdoc3/postdoc3_NPP",
        "archival_status": "completed",
        "submit_progress": [],
        "archivedSize": int(396700590),
        "dateArchived": "2020-01-15",
        "sourceSize": int(797725567),
        "user_metadata":{},
        "submission": {
            "job_id": "8640.ctarchive.jax.org",
            "when_ready_for_pbs": "2019-12-20 12:41:00 EDT-0400",
            "when_archival_queued": "2019-12-21 12:41:01 EDT-0400",
            "when_archival_started": "2019-12-22 12:44:08 EDT-0400",
            "when_archival_completed": "2020-01-01 13:01:59 EDT-0400" },
        "retrievals": [{
            "retrieval_status": "ready_for_pbs",
            "when_ready_for_pbs": "2020-01-02 08:34:48 EDT-0400",
            "when_retrieval_queued": None,
            "when_retrieval_started": None,
            "when_retrieval_completed": None}]
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

