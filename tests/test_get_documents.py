import requests
import sys
import os
import urllib.parse

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
find = '{"projectName": "Project 3"}'
limit = '1'
last = '5ec7cac93c9619864cc73e4a'
protocol = 'https'
host = '127.0.0.1'
port = '5000'


def build_url(api_key=None, find=None, limit=None, last=None, protocol=protocol, port=port):

    route = f'get_documents'

    param_list = []
    if api_key: param_list.append(f"api_key={api_key}")
    if find: param_list.append(f"find={urllib.parse.quote_plus(find)}")
    if limit: param_list.append(f"limit={limit}")
    if last: param_list.append(f"last={last}")

    if len(param_list) == 0: params = ''
    elif len(param_list) == 1: params = param_list[0]
    else: params = '&'.join(param_list)
    
    url = f"{protocol}://{host}:{port}/{route}"
    if params: url = f"{url}?{params}"

    return url


def get_response_value(url):

    try:
        response = requests.get(url, verify=False)    ## verify=False: for ssh w/o certificate
        if response.status_code != 200:
            raise Exception(f"Status code != 200; status_code: '{response.status_code}'")
        response.encoding = 'utf-8'
        output = response.text 
    except Exception as e:
        sys.stderr.write(f"get() returned exception of type '{type(e)}': {e}\n")
        return None

    return output


if __name__ == '__main__':

    url = build_url(api_key=api_key, find=find, limit=limit, last=last, protocol=protocol, port=port)

    print(f"testing url '{url}'")
    value = get_response_value(url)

    print(f"Returned value: '{value}'")

    sys.exit(0)

