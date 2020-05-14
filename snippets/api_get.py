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
params = f'api_key={api_key}&greet=hello'
url = f"{protocol}://{host}:{port}/{route}?{params}"

## the actual call; enclosing all parts that can fail in 'try' and using 'raise'
##   from w/i the 'try'; can check for different types of exceptions, but the
##   generic Exception handling below is adequate for most purposes:

try:
    response = requests.get(url, verify=False)
    if response.status_code != 200:
        raise Exception(f"Status code != 200; status_code: '{response.status_code}'")
    output = response.text.encode('utf8')
except Exception as e:
    ## we will normally log to file and email, but here we just write to stdout:
    sys.stderr.write(f"get() returned exception of type '{type(e)}': {e}\n")
    sys.exit(3)

print(output)

