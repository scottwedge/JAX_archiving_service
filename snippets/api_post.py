import requests
import sys

## should be from config module:

api_key = '123xyz'
protocol = 'https'
host = '127.0.0.1'
port = '5000'

## typically in this module: 

id1 = 'mpolo'
route = f'info/{id1}'
url = f"{protocol}://{host}:{port}/{route}"

## this sets 'flask.request.is_json' to 'True'; can then retrieve params on server 
##   as json using 'flask.request.json':
headers = {'Content-Type': 'application/json'}

## note this needs to be a string, not a dict(); note f-string double curly:
data = f'''{{ 
    "api_key": "{api_key}", 
    "my_key": "my_value" 
}}'''

print(f"data: {data}")

## the actual call; enclosing all parts that can fail in 'try' and using 'raise'
##   from w/i the 'try'; can check for different types of exceptions, but the
##   generic Exception handling below is adequate for most purposes:

try:
    response = requests.post(url, headers=headers, data=data, verify=False)
    if response.status_code != 200:
        raise Exception(f"Status code != 200; status_code: '{response.status_code}'")
    output = response.text.encode('utf-8')
except Exception as e:
    ## we will normally log to file and email, but here we just write to stdout:
    sys.stderr.write(f"post() returned exception of type '{type(e)}': {e}\n")
    sys.exit(3)

print(output)

