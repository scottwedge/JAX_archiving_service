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

@app.route("/archive")
def archive_url():
    url = "/archive"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/retrieve")
def retrieve_url():
    url = "/retrieve"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/archive_failed")
def archive_failed_url():
    url = "/archive_failed"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/archive_processing")
def archive_processing_url():
    url = "/archive_processing"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/archive_success")
def archive_succes_url():
    url = "/archive_success"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/retrieve_failed")
def retrieve_failed_url():
    url = "/retrieve_failed"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/retrieve_processing")
def retrieve_processing_url():
    url = "/retrieve_processing"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

@app.route("/retrieve_success")
def retrieve_success_url():
    url = "/retrieve_success"
    args_str = markupsafe.escape(str(flask.request.args))
    return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

## for now, just for testing/demo flask:
@app.route("/")
def root_url():
  url = "/"
  args_str = markupsafe.escape(str(flask.request.args))
  return f"ERROR: reached unimplemented route '{url}'; args: '{args_str}'"

## for now, just for testing/demo flask:
@app.route("/info/<id>")
def info_url(id):
  url = "/info"
  args_str = markupsafe.escape(str(flask.request.args))
  id_str = markupsafe.escape(str(id))
  return f"ERROR: reached unimplemented route '{url/id_str}'; args: '{args_str}'"

if __name__.split('.')[0] == '__main__': 
  app.run(host='127.0.0.1', ssl_context='adhoc')                 ## ssl w/o certificates; listen to localhost only

