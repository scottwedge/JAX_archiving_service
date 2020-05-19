import sys
import flask
import flask_session
import markupsafe

## local imports:
import config
import util

## init mongodb collection object for config.mongo['collection']; 
##   then can pass collection object to modules that need it:

mongo_collection = util.get_mongo_collection()
if not mongo_collection:
    util.log_email("ERROR: could not connect to collection.", error=True)
    sys.exit(3)

## initialize flask object:
app = flask.Flask(__name__.split('.')[0])

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

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        return user_dict
        ## value = status_updater.archive_processing(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: /archive_processing exception: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


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

## temporary route for testing purposes:
@app.route("/test", methods=['GET'])
def test():
    output = ''
    try: 
        cursor = mongo_collection.find({})
        for rec in cursor: 
            output += f"{rec}<br>"
    except Exception as e:
        return f"ERROR: find failed: {e}"

    return output


###########################################################################################
## MAIN: 

if __name__.split('.')[0] == '__main__': 
    ## execute as 'try' block to gracefully handle uncaught exceptions:
    try:
        ## listen to localhost only; ssl w/o certificates; auto refresh http server after code edits:
        app.run(host='127.0.0.1', ssl_context='adhoc', debug=True)  
    except Exception as e:
        util.log_email(f"ERROR: uncaught exception of type '{type(e)}': {e}", error=True)

    sys.exit(0)

