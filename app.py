import flask
import flask_session
import markupsafe

## to be moved into config:

config_session_key = 'abc123'
config_session_type = 'filesystem'

## launch and configure flask session:

app = flask.Flask(__name__.split('.')[0])
app.config['SECRET_KEY'] = config_session_key       ## random/secret key used to sign session info
app.config['SESSION_TYPE'] = config_session_type    ## mode for storing server-side session properties
flask_session.Session(app)                          ## make session server-side; set/get properties thru flask.session

#############################################################################################################
## ROUTES:

@app.route("/archive", methods=['POST'])
def archive_url():
    url = "/archive"
    if flask.request.is_json:           ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:                               ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"

@app.route("/retrieve", methods=['POST'])
def retrieve_url():
    url = "/retrieve"
    if flask.request.is_json:           ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:                               ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"

@app.route("/archive_failed", methods=['GET'])
def archive_failed_url():
    url = "/archive_failed"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

@app.route("/archive_processing", methods=['GET'])
def archive_processing_url():
    url = "/archive_processing"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

@app.route("/archive_success", methods=['GET'])
def archive_success_url():
    url = "/archive_success"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

@app.route("/retrieve_failed", methods=['GET'])
def retrieve_failed_url():
    url = "/retrieve_failed"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

@app.route("/retrieve_processing", methods=['GET'])
def retrieve_processing_url():
    url = "/retrieve_processing"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

@app.route("/retrieve_success", methods=['GET'])
def retrieve_success_url():
    url = "/retrieve_success"
    return f"ERROR: reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"

## for now, just for testing/demo flask:
@app.route("/", methods=['GET', 'POST'])
def root_url():
    url = "/"
    if flask.request.method == 'GET':   ## submitted parameters as part of URI
        return f"ERROR: GET reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"
    elif flask.request.is_json:         ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:                               ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"

## for now, just for testing/demo flask:
@app.route("/info/<id1>", methods=['GET', 'POST'])
def info_url(id1):
    url = f"/info/{id1}"
    if flask.request.method == 'GET':   ## submitted parameters as part of URI
        return f"ERROR: GET reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"
    elif flask.request.is_json:         ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:                               ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"

###########################################################################################
## MAIN: 

if __name__.split('.')[0] == '__main__': 
    ## execute main as 'try' block in order to gracefully handle and report any uncaught exceptions:
    try:
        ## listen to localhost only; ssl w/o certificates; auto refresh http server after code changes:
        app.run(host='127.0.0.1', ssl_context='adhoc', debug=True)  
    except Exception as e:
        ## we will normally log to file and email, but here temporarily we just write to stdout:
        sys.stderr.write(f"ERROR: uncaught exception of type '{type(e)}': {e}")
        sys.exit(3)
    sys.exit(0)

