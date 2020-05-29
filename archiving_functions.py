import config
import datetime as dt
import subprocess
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Optional


from mongo_utils import mongo_set, mongo_set_unset, mongo_delete_doc, mongo_ingest
from util import get_timestamp, log_email

COLLECTION = config.mongo["collection"]


def build_archived_path_faculty(pi, submitter, project):
    today = str(dt.date.today())
    # PREFIX allows for easy testing
    archived_path = (
        f"/archive/faculty/{pi.lower()}-lab/{submitter.lower()}/{today}/{project}"
    )
    return archived_path


def validate_service_path(service_path):
    while service_path[0] == "/":
        service_path = service_path[1:]
    test_list = ["archive", "service", "singlecell", "microscopy", "gt"]
    fields = service_path.split("/")
    for field in fields:
        for to_test in test_list:
            if to_test in field.lower():
                # When this function is called it should be in a try/except
                # so that the following string will be returned to user.
                raise Exception(
                    f"service_path: {service_path} is malformed. Cannot include {field}."
                )
    return service_path


def build_archived_path_services(service_name: str, service_path: str):
    if service_name != "gt":
        try:
            service_path = validate_service_path(service_path)
        except Exception as e:
            return f"Error occured when validating service_path: {e}"
        service_path = Path(service_path)
        for parent in service_path.parents:
            # test if 'service' will match as a substring
            # When this function is called it should be in a try/except
            # so that the following string will be returned to user.
            if parent.match(f"*/{{services,archive,{service_name}}}*"):
                raise Exception("invalid service_path")
        archived_path = f"{config.PREFIX}/services/{service_name}/{service_path}"
    else:
        tail_path_fields = service_path.split("/")[3:]
        tail_path = "/".join(tail_path_fields)
        # year = str(datetime.date.today()).split("-")[0]
        year = service_path.split("/")[4][0:4]
        archived_path = f"/archive/GT/{year}/{tail_path}"
    return archived_path


def insert_archived_path(metadata):
    if metadata["request_type"] == "faculty":
        pi = metadata["manager_user_id"]
        submitter = metadata["user_id"]
        source_path = metadata["source_folder"]
        service_path = metadata["service_path"]

        project = (
            metadata["project_name"]
            if len(metadata["project_name"]) > 0
            else source_path.split("/")[-1]
        )
        project = project.replace(" ", "_")

        metadata["archivedPath"] = build_archived_path_faculty(pi, submitter, project)
    else:
        service_name = metadata["request_type"]
        service_path = (
            metadata["source_folder"]
            if metadata["request_type"] == "gt"
            else metadata["service_path"]
        )
        metadata["archivedPath"] = build_archived_path_services(
            service_name, service_path
        )
    return metadata


def validate_source_path(*, action: str, path: str, parent: Optional[str] = None):
    assert path, f"{action} source path ({path}) must not be empty"
    path = Path(path)
    assert path.is_absolute(), f"{action} source path ({path}) must be an absolute path"
    assert path.is_dir(), f"{action} source path ({path}) is not a directory"
    if parent:
        parent = Path(parent)
        assert (
            parent.exists() and parent.is_absolute()
        ), f"Parent directory {parent} isn't absolute"
        assert path.relative_to(parent), f"{path} does not begin with '{parent}'"
    if action == "archive":
        log_email(f"{path} will be archived")
    else:
        log_email(f"{path} will be retrieved from the archive")
    return str(path)


def validate_destination_path(*, action: str, path: str, parent: Optional[str] = None):
    assert path, f"{action} destination path ({path}) must not be empty"
    log_email(f"recieved path: {path}")
    path = Path(path)
    assert (
        path.is_absolute()
    ), f"{action} destination path ({path}) must be an absolute path"
    if action != "retrieve":
        assert not path.exists(), f"{action} destination path ({path}) must not exist"
        if path.exists():
            log_email(f"path for {action} request {path} exists")
            return False
    if parent:
        parent = Path(parent)
        assert (
            parent.exists() and parent.is_absolute()
        ), f"Parent directory {parent} isn't absolute"
        assert path.relative_to(parent), f"{path} does not begin with '{parent}'"
    if action == "archive":
        log_email(f"archiver will deposit files at {path}")
    else:
        log_email(f"archiver will retrieve files to {path}")
    return str(path)


def completion_notification_body(
    action, source_path, destination_path, user, status=True
):
    email_content = {
        "subject": f"{user['fname'].capitalize()}, notice of your {action} request status"
    }
    email_content["body"] = (
        f"Hi {user['fname'].capitalize()},\nYour request to {action} {source_path} has "
        f"{'completed successfully' if status else 'failed'}.\n"
    )
    if status:
        if action == "archive":
            email_content["body"] = (
                email_content["body"]
                + f"\nYour files were deposited in the archive at {destination_path}"
            )
        else:
            delete_date_raw = dt.date.today() + timedelta(days=30)
            fmt = "%B %d, %Y"
            delete_date = delete_date_raw.strftime(fmt)

            email_content["body"] = (
                email_content["body"]
                + f"\nYour retrieved files are waiting for you at {destination_path}\n"
                "Please be sure to access and retrieve your files before "
                + str(delete_date)
                + " at which time they will autodelete from fastscratch.\n"
                + "Once you retriveve your files from fastscratch to your working "
                + "directory, you should delete your files from fastscratch."
            )
    return email_content


def dup_archive_request_body(source_path, destination_path, user):
    email_content = {
        "subject": f"{user['fname'].capitalize()}, notice: your archive request"
        + " was not processed",
        "body": f"Hi {user['fname'].capitalize()},\nYour archive request was not processed "
        f"because the generated path in the archive '{destination_path}' already "
        f"exists. This means your request to archive '{source_path}' was likely "
        "previously archived. Please contact Research IT if you require further assistance.",
    }
    return email_content


def get_src_groups(path):
    pass


def processing_notification_body(action, source_path, user):
    email_content = {
        "subject": f"{user['fname'].capitalize()}, notice of your {action} request status"
    }

    email_content["body"] = (
        f"Hi {user['fname'].capitalize()},\nYour request to {action} {source_path} "
        + "is now leaving the queue and is beginning to process. "
        + f"You will receive another email when this {action} request completes."
    )
    return email_content


def metadata_invalid(metadata: dict):
    """
    :description: Given in input metadata, give a reason metadata might be invalid.
    Else, return nothing.

    :returns: A string with an explanation of a problem with the input metadata.
    If there are no problems, then the return value is False stating metadata
    is not invalid.
    """
    required_keys = {
        "manager_user_id": {
            "type": str,
            "error_msg": "managerUserId should be a string.",
        },
        "user_id": {"type": str, "error_msg": "user_id should be a string."},
        "project_name": {"type": str, "error_msg": "projectName should be a string."},
        "grant_id": {"type": str, "error_msg": "grant_id should be a string."},
        "notes": {"type": str, "error_msg": "notes should be a string."},
        "system_groups": {
            "type": list,
            "error_msg": "system_groups should be a list of strings.",
        },
        "request_type": {"type": str, "error_msg": "request_type should be a string."},
    }
    for key in required_keys:
        if key not in metadata:
            return f"Key {key} not in metadata"
        if not isinstance(metadata[key], required_keys[key]["type"]):
            return required_keys[key]["error_msg"]
        if type(metadata[key]) == str and key not in ("notes", "grant_id"):
            if len(metadata[key]) < 1:
                return f"({key}) should not be the empty string"
        if "grant_id" in key and len(metadata[key]) == 0:
            metadata["grant_id"] = "None_entered_by_user"

    metadata_link = (
        "https://github.com/TheJacksonLaboratory/JAX_archiving_service#metadata"
    )
    request_types = ["faculty", "gt", "singlecell", "microscopy"]
    if not metadata["request_type"].lower() in request_types:
        return f'"request_type" not properly set. See {metadata_link} for guidance'
    return None


def request_invalid(request):
    required_keys = {
        "metadata": {"type": dict, "error_msg": "metadata must be a dict,"},
        "source_folder": {"type": str, "error_msg": "source_folder must be a string"},
        "service_path": {"type": str, "error_msg": "service_path must be a string"},
    }
    for key in required_keys:
        if key not in request:
            return f"Key '{key}' not in request."
        if not isinstance(request[key], required_keys[key]["type"]):
            return required_keys[key]["error_msg"]
    return None


def process_metadata(json_arg, api_user):
    metadata = json_arg["metadata"]
    metadata["request_type"] = metadata["request_type"].lower()
    metadata["user_id"] = json_arg["metadata"]["user_id"].lower()
    metadata["manager_user_id"] = metadata["manager_user_id"].lower()
    metadata["submitter"] = api_user
    metadata["source_folder"] = json_arg["source_folder"]
    metadata["system_groups"] = get_src_groups(metadata["source_folder"])
    # TODO: delete the two keys below when archive success
    metadata["service_path"] = json_arg["service_path"]
    metadata["archival_status"] = "processing_metadata"
    return metadata


def is_valid_for_pbs(archivedPath, collection):
    document = collection.find_one({"archivedPath": archivedPath})
    if document:
        if document["archival_status"] == "ready_for_pbs":
            return True
        return False
    return False


def submit_to_pbs(
    source: str, dest: str, action: str, group: str = None, obj_id: str = None
):
    # TODO: copy shell scripts to this repo and adjust curl for correct
    # name of endpoints
    script = (
        config.PBS_ARCHIVE_SCRIPT if action == "archive" else config.PBS_RETRIEVE_SCRIPT
    )

    cmd = f'/usr/local/bin/qsub -v IN="{source}",OUT="{dest}",GROUP="{group}",ID="{obj_id}" "{script}"'
    log_email(f"Submitting job: {cmd}")

    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    (o, e) = proc.communicate()

    try:
        if proc.returncode == 0:
            job_id = o.decode().replace("\n", "")
        else:
            raise ValueError("error submitting job: " + e.decode())
    except Exception as e:
        msg = f"pbs error: {e}"
        log_email(msg)
        return None

    log_email(f"Submitted to PBS: {job_id}\nstderr:{e.decode()}\nstdout:{o.decode()}")
    return job_id


def archive_directory(json_arg, api_user, debug: bool = False) -> None:
    """
    :param json_arg: A decoded JSON string which it at its top level a
    dictionary.  Must have the following keys: requested_dest_dir,
    source_folder, and metadata.  Additional keys are ignored.

    :param debug: Cause a dry-run of submitting to PBS; the result will be
    metadata ingested and no submission to pbs.
    """
    try:  # validate request
        request_error = request_invalid(json_arg)
        if request_error:
            raise ValueError(request_error)
    except Exception as e:
        log_email(f"Error processing request: {e}")
        return {"message": f"Error processing request: {e}"}, 400

    try:  # validate and preprocess metadata
        metadata = process_metadata(json_arg, api_user)
        metadata_error = metadata_invalid(metadata)
        if metadata_error:
            raise ValueError(metadata_error)

    except Exception as e:
        return {"message": f"Error processing metadata: {e}"}, 400

    log_email(
        f"{api_user['fname']} {api_user['lname']} ({api_user['username']}) requesting"
        + f" to archive {metadata['source_folder']}"
    )

    try:  # create and insert archivedPath
        metadata = insert_archived_path(metadata)
    except Exception as e:
        return (
            {"message": f"Error processing and/or inserting archivedPath: {e}"},
            400,
        )

    try:  # insert metadata into mongoDB
        metadata = mongo_ingest(metadata)
    except Exception as e:
        return {"message": f"Error ingesting metadata: {e}"}, 400

    try:  # validate tentative archivedPath
        source_path = metadata["source_folder"]
        destination_path = validate_destination_path(
            action="archive", path=metadata["archivedPath"], parent="/"
        )
        if destination_path:
            mongo_set(
                "archivedPath",
                destination_path,
                {
                    "when_ready_for_pbs": get_timestamp(),
                    "archival_status": "ready_for_pbs",
                },
                COLLECTION,
            )
        else:  # requested archivedPath not valid
            pass
            # TODO: create duplicate archive request email body
            # send_dup_archive_notification(
            #     input["source_dir"], input["archive_dest_dir"], user
            # )
            raise Exception(
                f"archive destination path '{destination_path}' must not exist."
            )

    except Exception as e:  # destination_path already in archive
        source_path = metadata["source_folder"]
        destination_path = metadata["archivedPath"]
        status = metadata["archival_status"]
        if "completed" not in status:
            mongo_set(
                "archivedPath",
                destination_path,
                {
                    "archival_status": "failed",
                    "exception_caught": str(e),
                    "when_archival_failed": get_timestamp(),
                },
                COLLECTION,
            )
        msg = f"Error while validating tentative archivedPath: {e}"
        # TODO: sort out reporting of errors via email
        # log_email(msg error=True)
        return {"message": msg}, 400

    try:
        if "debug" in json_arg.keys():
            debug = json_arg["debug"]
        if not debug:
            if is_valid_for_pbs(destination_path):
                mongo_set(
                    "archivedPath",
                    destination_path,
                    {"archival_status": "submitting"},
                    COLLECTION,
                )
                job_id = submit_to_pbs(source_path, destination_path, "archive")
                if job_id:  # successfully submitted
                    mongo_set(
                        "archivedPath",
                        destination_path,
                        {
                            "archival_status": "submitted",
                            "when_submitted_to_pbs": get_timestamp(),
                            "job_id": job_id,
                        },
                        COLLECTION,
                    )
                    return {"id": str(metadata["_id"])}
                else:  # failed
                    mongo_set(
                        "archivedPath",
                        destination_path,
                        {
                            "archival_status": "failed",
                            "when_archival_failed": get_timestamp(),
                            "job_id": job_id,
                        },
                        COLLECTION,
                    )
                    return (
                        {"message": "Submitting to pbs failed, please see logs."},
                        400,
                    )

            else:
                status = metadata["archival_status"]
                msg = f"Archive request denied. Current status of {metadata['archivedPath']}: {status}"

                log_email(msg)
                return {"message": msg}, 400
        else:
            if "completed" not in metadata["archival_status"]:
                mongo_set(
                    "archivedPath",
                    metadata["archivedPath"],
                    {"archival_status": "dry_run"},
                    COLLECTION,
                )
                return (
                    {
                        "message": f"Dry run request, metadata for '{metadata['archivedPath']}'"
                        + " present in mongo and not archived. Request not submitted"
                    },
                )
            return (
                {
                    "message": f"Dry run request and {metadata['archivedPath']}"
                    + " previously archived. Request not submitted."
                },
            )
    except Exception as e:  # noqa: e722
        return {"message": f"Failed to send to queue with error: {e}"}, 400


# def archive_helper(input: dict, user: dict):
#     action = "archive"
#     # TODO: input from oauth2_jwt
#     try:
#         source_path = input["source_dir"]
#         destination_path = validate_destination_path(
#             action=action, path=input["archive_dest_dir"], parent="/"
#         )
#         if not destination_path:
#             send_dup_archive_notification(
#                 input["source_dir"], input["archive_dest_dir"], user
#             )
#             raise Exception(
#                 f"{action} destination path ({input['archive_dest_dir']}) must not exist."
#             )
#
#         job_id = submit_to_pbs(source_path, destination_path, action)
#         update_archive_queued(destination_path, job_id)
#         send_queue_notification(action, source_path, user)
#
#     except Exception as e:
#         source_path = input["source_dir"]
#         destination_path = input["archive_dest_dir"]
#         metadata = get_metadata("archivedPath", destination_path)
#         status = metadata["archival_status"]
#         if "completed" not in status:
#             update_metadata_by_key(destination_path, "archival_status", "failed")
#             update_metadata_by_key(destination_path, "exception_caught", str(e))
#         tb = traceback.format_exc()
#         send_completion_notification(
#             action,
#             source_path,
#             destination_path,
#             user,
#             False,
#             exception=str(e),
#             traceback=tb,
#         )
