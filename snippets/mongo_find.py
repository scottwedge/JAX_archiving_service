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
    sys.stderr.write(f"ERROR: could not connect to '{mongo_host}:{mongo_port}': {e}")
    sys.exit(3)

## Connect to database and collection:
##   normally you can set up the collection object in one spot and pass around:
try:
    db = client[database]
    col = db[collection]
except Exception as e:
    sys.stderr.write(f"ERROR: could not select collection '{database}.{collection}': {e}")
    sys.exit(4)

## The actual insertion; you can also insert a single record as a dictionary (instead
##   of as a list of dictionaries), by calling 'insert_one':
try: 
    curs = col.find({"i like": True})
    ## if the result set is reasonably small, you can get them all back as a list with:
    ##   results = list(curs)
    ## but here we will pretend the list is potentially huge, so need to process 1-by-1:
    ##   keep inside try, as each iteration requires a server connection (which may fail):
    for rec in curs:
        print("next record: ", rec)
except Exception as e:
    sys.stderr.write(f"ERROR: find() failed: {e}")
    sys.exit(5)

sys.exit(0)

