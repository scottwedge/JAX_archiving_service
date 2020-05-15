import sys
import pymongo
import urllib.parse

## normally in config or secrets modules:

mongo_host = '127.0.0.1'
mongo_port = '27017'
mongo_user = 'test_user'
mongo_passwd = 'resu_tset'
mongo_user_db = 'test_db'           ## the authentication database for mongo_user
database = 'test_db'                ## the database we will search
collection = 'test_collection'      ## the collection we will search

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

## The actual update; you can also update multiple records in single call w/ update_many():
condition = {'i like': False}
try: 
    cursor = col.find(condition, {'_id': 1})
    count = cursor.count() 
    if count != 1:
        raise Exception(f"ERROR: {count} records match condition {condition}.\n")
    id1 = cursor[0]['_id']      ## '_id' field from 1st record (dict); type(id1): ObjectId
    result = col.update_one(
        {'_id': id1},                                             ## match condition
        {'$set': {'i like': True, 'priceline_spokesman': True},   ## one old field, one new
         '$unset': {'other works': ''}})                          ## delete a field
    if not result.acknowledged:
        raise Exception(f"ERROR: update not acknowledged.")
except Exception as e:
    sys.stderr.write(f"ERROR: find() failed: {e}\n")
    sys.exit(5)

print(f"successfully changed record w/ _id: {id1}")
sys.exit(0)

