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
job_id = 'xy121yx'
source_size = 1000000
archived_size = 800000
protocol = 'https'
host = '127.0.0.1'
port = '5000'

def build_url(api_key=None, job_id=None, source_size=None, archived_size=None, protocol=protocol, port=port):

    route = f'archive_success'

    param_list = []
    if api_key: param_list.append(f"api_key={api_key}")
    if job_id: param_list.append(f"job_id={job_id}")
    if source_size: param_list.append(f"sourceSize={source_size}")
    if archived_size: param_list.append(f"archivedSize={archived_size}")

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

    url = build_url(api_key=api_key, job_id=job_id, source_size=source_size, 
                    archived_size=archived_size, protocol=protocol, port=port)

    print(f"testing url '{url}'")
    value = get_response_value(url)

    print(f"Returned value: '{value}'")

    sys.exit(0)

