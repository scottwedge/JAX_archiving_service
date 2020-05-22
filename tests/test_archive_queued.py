import requests
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import config

mongo_host = config.mongo['host']
mongo_port = config.mongo['port']
mongo_user = config.mongo['user']
mongo_passwd = config.mongo['passwd']
mongo_user_db = config.mongo['authdb']       ## the authentication database for mongo_user
database = config.mongo['db']                ## the database where we will write records
collection = config.mongo['collection']    

api_key = '123abc'
obj_id = '5ec7cac93c9619864cc73e4d'
job_id = 'xy121yx'
protocol = 'https'
host = '127.0.0.1'
port = '5000'

## typically in this module: 

route = f'archive_queued'
params = f'api_key={api_key}&obj_id={obj_id}&job_id={job_id}'
url = f"{protocol}://{host}:{port}/{route}?{params}"
print(f"testing call: '{url}'")

## the actual call; enclosing all parts that can fail in 'try' and using 'raise'
##   from w/i the 'try'; can check for different types of exceptions, but the
##   generic Exception handling below is adequate for most purposes:

try:
    response = requests.get(url, verify=False)    ## verify=False: for ssh w/o certificate
    if response.status_code != 200:
        raise Exception(f"Status code != 200; status_code: '{response.status_code}'")
    response.encoding = 'utf-8'
    output = response.text 
except Exception as e:
    sys.stderr.write(f"get() returned exception of type '{type(e)}': {e}\n")
    sys.exit(3)

print(f"{output}")
sys.exit(0)

