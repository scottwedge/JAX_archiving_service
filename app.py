import sys
import flask
import flask_session
import markupsafe

## local imports:
import config
import util
import status_updater
import document_getter

## init mongodb collection object for config.mongo['collection'];
##   then can pass collection object to modules that need it:

mongo_collection = util.get_mongo_collection()
if not mongo_collection:
    util.log_email("ERROR: could not connect to collection.", error=True)
    sys.exit(3)

## initialize flask object:
app = flask.Flask(__name__.split(".")[0])

#############################################################################################################
## ROUTES:


@app.route("/archive", methods=["POST"])
def archive_url():
    url = "/archive"
    if flask.request.is_json:  ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:  ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"


@app.route("/retrieve", methods=["POST"])
def retrieve_url():
    url = "/retrieve"
    if flask.request.is_json:  ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:  ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"


@app.route("/archive_queued", methods=["GET"])
def archive_queued_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/archive_queued is only available to admins.")
        value = status_updater.archive_queued(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /archive_queued: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/archive_processing", methods=["GET"])
def archive_processing_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/archive_processing is only available to admins.")
        value = status_updater.archive_processing(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /archive_processing: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/archive_success", methods=["GET"])
def archive_success_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/archive_success is only available to admins.")
        value = status_updater.archive_success(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /archive_success: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/archive_failed", methods=["GET"])
def archive_failed_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/archive_failed is only available to admins.")
        value = status_updater.archive_failed(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /archive_failed: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/retrieve_queued", methods=["GET"])
def retrieve_queued_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/retrieve_queued is only available to admins.")
        value = status_updater.retrieve_queued(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /retrieve_queued: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/retrieve_processing", methods=["GET"])
def retrieve_processing_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/retrieve_processing is only available to admins.")
        value = status_updater.retrieve_processing(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /retrieve_processing: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/retrieve_success", methods=["GET"])
def retrieve_success_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/retrieve_success is only available to admins.")
        value = status_updater.retrieve_success(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /retrieve_success: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/retrieve_failed", methods=["GET"])
def retrieve_failed_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/retrieve_failed is only available to admins.")
        value = status_updater.retrieve_failed(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /retrieve_failed: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/get_documents", methods=["GET"])
def get_documents_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        value = document_getter.get_documents(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /get_documents: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/get_document_by_objectid", methods=["GET"])
def get_document_by_objectid_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        value = document_getter.get_document_by_objectid(
            args, user_dict, mongo_collection
        )
    except Exception as e:
        msg = f"ERROR: from /get_document_by_objectid: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


@app.route("/get_last_document", methods=["GET"])
def get_last_document_url():

    try:
        args = dict(flask.request.args)
        user_dict = util.get_api_user(args)
        if not user_dict.get("admin"):
            raise Exception("/get_last_document is only available to admins.")
        value = document_getter.get_last_document(args, user_dict, mongo_collection)
    except Exception as e:
        msg = f"ERROR: from /get_last_document: {e}"
        util.log_email(msg, error=True)
        return msg

    return value


## for now, just for testing/demo flask:
@app.route("/", methods=["GET", "POST"])
def root_url():
    url = "/"
    if flask.request.method == "GET":  ## submitted parameters as part of URI
        return f"ERROR: GET reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"
    elif flask.request.is_json:  ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:  ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"


## for now, just for testing/demo flask:
@app.route("/info/<id1>", methods=["GET", "POST"])
def info_url(id1):
    url = f"/info/{id1}"
    if flask.request.method == "GET":  ## submitted parameters as part of URI
        return f"ERROR: GET reached unimplemented route '{url}'; args: '{dict(flask.request.args)}'"
    elif flask.request.is_json:  ## submitted parameters thru api call w/ json
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{flask.request.json}'"
    else:  ## submitted parameters thru web page form
        return f"ERROR: POST reached unimplemented route '{url}'; args: '{dict(flask.request.form)}'"


## temporary route for testing purposes:
@app.route("/test", methods=["GET"])
def test():
    output = ""
    try:
        cursor = mongo_collection.find({})
        for rec in cursor:
            output += f"{rec}<br>"
    except Exception as e:
        return f"ERROR: find failed: {e}"

    return output


###########################################################################################
## MAIN:

if __name__.split(".")[0] == "__main__":
    ## execute as 'try' block to gracefully handle uncaught exceptions:
    try:
        ## listen to localhost only; ssl w/o certificates; auto refresh http server after code edits:
        app.run(host="127.0.0.1", ssl_context="adhoc", debug=True)
    except Exception as e:
        util.log_email(
            f"ERROR: uncaught exception of type '{type(e)}': {e}", error=True
        )

    sys.exit(0)
