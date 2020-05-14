import requests
import sys

## should be from config:

api_key = '123xyz'
protocol = 'https'
host = '127.0.0.1'
port = '5000'
id1 = 'mpolo'
route = f'info/{id1}'
params = f'api_key={api_key}&greet=hello'
## url = f"{protocol}://{host}:{port}/"
url = f"{protocol}://{host}:{port}/{route}?{params}"

try:
    response = requests.get(url, verify=False)
    response.raise_for_status()
except Exception as e:
    sys.stderr.write(f"get() returned exception of type {type(e)}: {e}\n")
    sys.exit(3)

print(response.text.encode('utf8'))

